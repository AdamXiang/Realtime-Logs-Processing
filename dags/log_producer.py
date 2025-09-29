import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Producer
from faker import Faker
import logging
from .utils import get_secret
import random


# Instantiate a Faker generator (used to fake IPs and other fields)
fake = Faker()
# Create a module-level logger named after this module
logger = logging.getLogger(__name__)


def create_kafka_producer(config):
  """
  Given a dict of Kafka configs, return a Producer instance.
  """
  return Producer(config)


def generate_log():
  """
  Generate a single synthetic web-server log line with random fields.
  """
  # Possible HTTP methods/endpoints/status codes for the fake log
  methods = ['GET', 'POST', 'PUT', 'DELETE']
  endpoints = ['/api/users', '/home', '/about', '/contact', '/services']
  statuses = [200, 301, 302, 400, 404, 500]

  # A small pool of realistic user-agent strings to sample from
  user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Mozilla/5.0 (iPad; CPU OS 16_7_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
  ]

  # Common HTTP referrers (or "-" for no referrer)
  referrers = ['https://example.com', 'https://google.com', '-', 'https://bing.com', 'https://yahoo.com']

  # Fake an IPv4 address, e.g., "123.45.67.89"
  ip = fake.ipv4()
  # NOTE: since we imported the module `import datetime`, use datetime.datetime.now()
  # timestamp = datetime.now().strftime('%b %d %Y, %H:%M:%S')   # <-- would raise NameError
  timestamp = datetime.datetime.now().strftime('%b %d %Y, %H:%M:%S')

  # Randomly choose request method, endpoint, HTTP status, response size, referrer, and user agent
  method = random.choice(methods)
  endpoint = random.choice(endpoints)
  status = random.choice(statuses)
  size = random.randint(1000, 15000)
  referer = random.choice(referrers)
  user_agent = random.choice(user_agents)

  # Build a single Apache/Nginx-like access log line
  log_entry = (
    f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size} "{referer}" {user_agent}'
  )

  # Return the formatted log string
  return log_entry


def delivery_report(err, msg):
  """
  Kafka delivery callback: called when a message is delivered or fails.
  """
  if err is not None:
    # If delivery failed, log an error with the reason
    logger.error(f'Message delivery failed: {err}')
  else:
    # If successful, log topic and partition
    logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def product_logs(**context):
  """
  Produce (send) a batch of synthetic log entries into a Kafka topic.
  Airflow will pass runtime context via **context (unused here).
  """
  # Fetch secrets (e.g., from AWS Secrets Manager) by key name
  secrets = get_secret('MWAA_Side_Project_Secret')

  # Build Kafka producer configuration using your secret values
  kafka_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],  # Kafka brokers
    'security.protocol': 'SASL_SSL',                         # Encrypted auth channel
    'sasl.mechanisms': 'PLAIN',                              # SASL mechanism
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],         # Username from secret
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],         # Password from secret
    'session_timeout.ms': 50000                              # Session timeout
  }

  # Create the Kafka Producer
  producer = create_kafka_producer(kafka_config)
  # Target topic to send logs to
  topic = 'website_logs'

  # Send 15,000 synthetic log messages
  for _ in range(15000):
    log = generate_log()  # Generate one log line
    
    try:
      # Asynchronously enqueue the message for delivery; register a delivery callback
      producer.produce(topic, log.encode('utf-8'), on_delivery=delivery_report)
      # Force sending buffered messages to the broker immediately
      # (Note: flushing every loop is simple but slower; in production, batch and flush less often.)
      producer.flush()
    except Exception as e:
      # If produce/flush fails, log and re-raise to fail the task
      logger.error(f'Error producing log: {e}')
      raise
  
  # Final info log after all messages are sent
  logger.info(f'Produced 15,000 logs to topic {topic}')


# Airflow default arguments applied to all tasks unless overridden
default_args = {
  'owner': 'Adam Chang',                          # DAG owner (for visibility)
  'depends_on_past': False,                       # Do not wait on previous run’s task states
  'email_on_failure': False,                      # Disable failure emails
  'retries': 1,                                   # Retry once on failure
  'retry_delay': datetime.timedelta(seconds=5)    # Wait 5 seconds between retries
}

# Define the DAG (workflow) itself
dag = DAG(
  dag_id='log_generation_pipeline',               # Unique DAG identifier
  default_args=default_args,                      # Apply defaults above
  description='Generate and produce synthetic logs',  # Human-readable description
  schedule_interval='*/2 * * * *',                # Run every 2 minutes (cron)
  start_date=datetime.datetime(2025, 9, 30),      # Earliest execution date/time (UTC)
  catchup=False,                                  # Do not backfill missed runs
  tags=['logs', 'kafka', 'production']            # UI tags to group/search DAGs
)

# A single task: run the product_logs() Python function when the DAG schedules
produce_logs_task = PythonOperator(
  task_id='generate_and_produce_logs',  # Task id shown in Airflow UI
  python_callable=product_logs,         # The function executed by this task
  dag=dag                               # Attach to the DAG defined above
)
