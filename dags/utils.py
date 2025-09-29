import boto3                      
import json                         
import logging                       

logger = logging.getLogger(__name__)  # Create a module-level logger named after this module

def get_secret(secret_name, region_name='us-east-1'):
  '''
    Retrieve secrets from AWS Secrets Manager
    - secret_name: name or ARN of the secret in AWS Secrets Manager
    - region_name: AWS region where the secret is stored (default: us-east-1)
  '''
  session = boto3.session.Session()   # Create a new boto3 session (credentials/region resolved via env/config/role)
  client = session.client(            # Build a Secrets Manager client bound to the target region
    service_name='secretsmanager',
    region_name=region_name
  )

  try:
    response = client.get_secret_value(     # Call AWS to fetch the current secret value (may include rotation metadata)
      SecretId=secret_name
    )
    # NOTE: response can contain either 'SecretString' (text) or 'SecretBinary' (base64-encoded bytes).
    # The line below assumes a JSON *string* is returned and tries to parse it.
    # Caveat: json.load() expects a file-like object; json.loads() would be used for strings.
    return json.load(response['SecretString'])  # Return the parsed JSON for the secret (as dict) if successful
  except Exception as e:
    logger.error(f'Secret retrival error: {e}')  # Log any error encountered during the fetch/parse process
    raise                                        # Re-raise to let callers handle failure (e.g., fail task/DAG)
