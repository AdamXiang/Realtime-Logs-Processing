import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Producer
from faker import Faker
import logging
from .utils import get_secret
import random


fake = Faker()
logger = logging.getLogger(__name__)


def create_kafka_producer(config):
  return Producer(config)


def generate_log():
  '''
    Generate synthetic log
  '''
  methods = ['GET', 'POST', 'PUT', 'DELETE']
  endpoints = ['/api/users', '/home', '/about', '/contact', '/services']
  statuses = [200, 301, 302, 400, 404, 500]

  user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Mozilla/5.0 (iPad; CPU OS 16_7_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
  ]

  referrers = ['https://example.com', 'https://google.com', '-', 'https://bing.com', 'https://yahoo.com']

  ip = fake.ipv4()
  timestamp = datetime.now().strftime('%b %d %Y, %H:%M:%S')
  method = random.choice(methods)
  endpoint = random.choice(endpoints)
  status = random.choice(statuses)
  size = random.randint(1000, 15000)
  referer = random.choice(referrers)
  user_agent = random.choice(user_agents)

  log_entry = (
    f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size} "{referer}" {user_agent}'
  )

  return log_entry


def delivery_report(err, msg):
  if err is not None:
    logger.error(f'Message delivery failed: {err}')
  else:
    logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def product_logs(**content):
  '''
    Product log entries into Kafka
  '''
  secrets = get_secret('MWAA_Side_Project_Secret')

  kafka_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'session_timeout.ms': 50000
  }

  producer = create_kafka_producer(kafka_config)
  topic = 'website_logs'

  for _ in range(15000):
    log = generate_log()
    
    try:
      producer.produce(topic, log.encode('utf-8'), on_delivery=delivery_report)
      producer.flush()
    except Exception as e:
      logger.error(f'Error producing log: {e}')
      raise
  
  logger.info(f'Produced 15,000 logs to topic {topic}')


default_args = {
  'owner': 'Adam Chang',
  'depends_on_past': False,
  'email_on_failure': False,
  'retries': 1,
  'retry_delay': datetime.timedelta(seconds=5)
}

dag = DAG(
  dag_id='log_generation_pipeline',
  default_args=default_args,
  description='Generate and produce synthetic logs',
  schedule_interval='*/5 * * * *',
  start_date=datetime(2025, 9, 30),
  catchup=False,
  tags=['logs', 'kafka', 'production']
)


produce_logs_task = PythonOperator(
  task_id='generate_and_produce_logs',
  python_callable=product_logs,
  dag=dag
)