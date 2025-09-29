import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Consumer, KafkaException
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import re
from .utils import get_secret

logger = logging.getLogger(__name__)


def parsed_log_entry(log_entry):
   log_pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*?)\] "(?P<method>\w+) (?P<endpoint>[\w/]+) (?P<protocol>[\w/\.]+)'
   match = re.match(log_pattern, log_entry)

   if not match:
      logger.warning(f"Invaild log format: {log_entry}")
      return None
   
   data = match.groupdict()

   try:
      parsed_timestamp = datetime.strptime(data['timestamp'], '%b %d %Y, %H:%M:%S')
      data['@timestamp'] = parsed_timestamp.isoformat()

   except ValueError:
      logger.error(f'Timestamp parsing error: {data["timestamp"]}')
      return None
   
   return data


def consume_and_index_logs(**context):
  secrets = get_secret('MWAA_Side_Project_Secret')

  consumer_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'group.id': 'mwaa_log_indexer',
    'auto.offset_reset': 'latest'
  }

  es_config = {
    'hosts': [secrets['ELASTICSEARCH_URL']],
    'api_key': secrets['ELASTICSEARCH_API_KEY']
  }
  
  consumer = Consumer(consumer_config)
  es = Elasticsearch(**es_config)

  topic = 'MWAA_Side_Project_Secret'

  consumer.subscribe([topic])

  try:
    index_name = 'MWAA_Side_Project_Secret'
    if not es.indices.exists(index=index_name):
      es.indices.create(index=index_name)
      logger.info(f'Created index: {index_name}')
  except Exception as e: 
      logger.error(f'Failed to create index: {index_name} {e}')

  logs = []
  try:
     while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
           break
        
        if msg.error():
           if msg.error().code() == KafkaException._PARTITION_EOF:
              break
           raise KafkaException(msg.error())
        
        log_entry = msg.value().decode('utf-8')
        parsed_log = parsed_log_entry(log_entry)

        if parsed_log:
            logs.append(parsed_log)

        if len(logs) >= 15000:
            actions = [
              {
                  '_op_type': 'create',
                  '_index': index_name,
                  '_source': log
              }
              for log in logs
            ]
            success, failed = bulk(es, actions, refresh=True)
            logger.info(f'Indexed {success} logs, {len(failed)} failed')

            # reset the logs
            logs = []

  except Exception as e:
     logger.error(f'Failed to index log: {e}')


  try:
    # index any remaining logs
    if logs:
      actions = [
            {
                '_op_type': 'create',
                '_index': index_name,
                '_source': log
            }
            for log in logs
        ]
      bulk(es, actions, refresh=True)
  except Exception as e:
     logger.error(f'Log processing error {e}')

  finally:
     consumer.close()
     es.close()

default_args = {
  'owner': 'Adam Chang',
  'depends_on_past': False,
  'email_on_failure': False,
  'retries': 1,
  'retry_delay': datetime.timedelta(seconds=5)
}

dag = DAG(
  dag_id='log_consumption_pipeline',
  default_args=default_args,
  description='Consume and index synthetic logs',
  schedule_interval='*/5 * * * *',
  start_date=datetime(2025, 9, 30),
  catchup=False,
  tags=['logs', 'kafka', 'production']
)

consume_logs_task = PythonOperator(
  task_id='generate_and_consume_logs',
  python_callable=consume_and_index_logs,
  dag=dag
)