import boto3
import json
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_name, region_name='us-east-1'):
  '''
    Retrieve secrets from AWS Secrets Manager
  '''
  session = boto3.session.Session()
  client = session.client(service_name='secretsmanager', region_name=region_name)

  try:
    response = client.get_secret_value(SecretId=secret_name)
    return json.load(response['SecretString'])
  except Exception as e:
    logger.error(f'Secret retrival error: {e}')
    raise