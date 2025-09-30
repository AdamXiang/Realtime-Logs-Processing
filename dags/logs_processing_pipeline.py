import datetime                                
from airflow import DAG                        
from airflow.operators.python import PythonOperator  
from confluent_kafka import Consumer, KafkaException 
from elasticsearch import Elasticsearch         
from elasticsearch.helpers import bulk         
import logging                                  
import re                                      
from .utils import get_secret                  

logger = logging.getLogger(__name__)            # Module-level logger named after current module


def parsed_log_entry(log_entry):
   # Regex pattern with named groups to extract fields from an access-log-like line
   log_pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*?)\] "(?P<method>\w+) (?P<endpoint>[\w/]+) (?P<protocol>[\w/\.]+)'
   match = re.match(log_pattern, log_entry)     # Try to match from the start of the string

   if not match:
      logger.warning(f"Invaild log format: {log_entry}")  # Log and skip if the line doesn't match the expected format
      return None
   
   data = match.groupdict()                     # Convert matched named groups into a dict

   try:
      # Parse timestamp string into a Python datetime, then normalize to ISO 8601 string
      # NOTE: since we imported the module `datetime`, call is `datetime.datetime.strptime(...)`
      parsed_timestamp = datetime.strptime(data['timestamp'], '%b %d %Y, %H:%M:%S')
      data['@timestamp'] = parsed_timestamp.isoformat()

   except ValueError:
      logger.error(f'Timestamp parsing error: {data["timestamp"]}')  # If timestamp doesn't match format, log and skip
      return None
   
   return data                                  # Return the parsed dict (now includes '@timestamp')


def consume_and_index_logs(**context):
  # Pull credentials/config from a secret store (key name provided)
  secrets = get_secret('MWAA_Side_Project_Secret')

  # Kafka consumer configuration (SASL/SSL auth with username/password)
  consumer_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'group.id': 'mwaa_log_indexer',          # Consumer group id for offset coordination
    'auto.offset_reset': 'latest'             # If no prior offset, start from latest messages
  }

  # Elasticsearch connection configuration (cloud endpoint + API key)
  es_config = {
    'hosts': [secrets['ELASTICSEARCH_URL']],
    'api_key': secrets['ELASTICSEARCH_API_KEY']
  }
  
  consumer = Consumer(consumer_config)         # Create Kafka consumer
  es = Elasticsearch(**es_config)              # Create Elasticsearch client

  topic = 'website_logs'           # Topic to consume from (string literal here)

  consumer.subscribe([topic])                  # Subscribe consumer to the topic

  try:
    index_name = 'MWAA_Side_Project_Secret'    # Target Elasticsearch index name (string literal here)
    if not es.indices.exists(index=index_name):# Create the index if it doesn't exist
      es.indices.create(index=index_name)
      logger.info(f'Created index: {index_name}')
  except Exception as e: 
      logger.error(f'Failed to create index: {index_name} {e}')  # Log any index-creation errors

  logs = []                                    # Buffer to accumulate parsed documents before bulk indexing
  try:
     while True:                               # Poll until no more messages (break when poll returns None)
        msg = consumer.poll(timeout=1.0)       # Fetch one message or None if nothing within timeout
        if msg is None:
           break                               # No more messages available right now → exit loop
        
        if msg.error():                        # If an error object is attached to the message
           if msg.error().code() == KafkaException._PARTITION_EOF:
              break                            # Reached end of partition → exit loop
           raise KafkaException(msg.error())   # Other errors → raise to outer handler
        
        log_entry = msg.value().decode('utf-8')  # Raw message payload → decode to string
        parsed_log = parsed_log_entry(log_entry) # Try to parse into a structured dict

        if parsed_log:
            logs.append(parsed_log)            # Keep only well-formed entries

        if len(logs) >= 15000:                 # When buffer reaches batch size, perform a bulk index
            actions = [
              {
                  '_op_type': 'create',        # Create operation (fails if doc id exists; no _id provided here)
                  '_index': index_name,        # Target index
                  '_source': log               # Document body
              }
              for log in logs
            ]
            success, failed = bulk(es, actions, refresh=True)  # Bulk API call; refresh makes docs searchable immediately
            logger.info(f'Indexed {success} logs, {len(failed)} failed')  # Log bulk outcome

            # reset the logs
            logs = []                          # Clear buffer after bulk indexing

  except Exception as e:
     logger.error(f'Failed to index log: {e}') # Catch any exceptions during consumption/bulk and log


  try:
    # index any remaining logs (flush the tail of the buffer)
    if logs:
      actions = [
            {
                '_op_type': 'create',
                '_index': index_name,
                '_source': log
            }
            for log in logs
        ]
      bulk(es, actions, refresh=True)          # Bulk index the remaining docs
  except Exception as e:
     logger.error(f'Log processing error {e}') # Log any final bulk errors

  finally:
     consumer.close()                          # Always close the Kafka consumer to commit/clean up
     es.close()                                # Close Elasticsearch client


default_args = {
  'owner': 'Adam Chang',                       # DAG owner (for visibility/auditing)
  'depends_on_past': False,                    # Do not depend on previous run’s state
  'email_on_failure': False,                   # Disable email notifications on failure
  'retries': 1,                                # Retry once if the task fails
  'retry_delay': datetime.timedelta(seconds=5) # Wait time between retries
}

dag = DAG(
  dag_id='log_consumption_pipeline',           # Unique DAG identifier
  default_args=default_args,                   # Apply default task args
  description='Consume and index synthetic logs', # Human-readable description
  schedule_interval='*/2 * * * *',             # Run every 2 minutes (cron format)
  start_date=datetime.datetime(2025, 9, 30),   # Earliest execution time (UTC); no runs before this
  catchup=False,                               # Do not backfill historical runs
  tags=['logs', 'kafka', 'production']         # Tags shown in Airflow UI for filtering
)

consume_logs_task = PythonOperator(
  task_id='generate_and_consume_logs',         # Task id displayed in UI
  python_callable=consume_and_index_logs,      # Python function to execute as the task
  dag=dag                                      # Attach the task to the DAG
)
