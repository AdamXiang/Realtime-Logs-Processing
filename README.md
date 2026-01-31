# Real-Time Web Server Log Processing Pipeline

<p align="center">
  <img src="https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white" alt="Airflow">
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" alt="Kafka">
  <img src="https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white" alt="Elasticsearch">
  <img src="https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="AWS">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

A production-ready, event-driven log processing pipeline that generates synthetic web server access logs, streams them through Kafka, and indexes them into Elasticsearch for real-time analytics. Built with Apache Airflow for orchestration and AWS Secrets Manager for secure credential management.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## 🎯 Project Overview

This project demonstrates a complete real-time data streaming pipeline that simulates web server log generation, processes them through a message queue, and makes them searchable in Elasticsearch.

**Business Scenario:**
Simulate a high-traffic website generating access logs that need to be collected, processed, and analyzed in real-time for monitoring, troubleshooting, and business intelligence.

**Core Value Proposition:**
- **Learn event-driven architecture** with Kafka as the message broker
- **Understand ELK Stack** (Elasticsearch + Kibana) for log analytics
- **Master Airflow** for workflow orchestration and scheduling
- **Practice secure DevOps** with AWS Secrets Manager integration
- **Generate realistic test data** without exposing real user information

**Target Audience:**
- Data engineers learning streaming architectures
- DevOps engineers building observability pipelines
- Backend engineers exploring message queues
- Anyone interested in real-time data processing

## 🏗 Architecture

### System Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Apache Airflow                               │
│                                                                        │
│  ┌───────────────────────────┐      ┌────────────────────────────┐  │
│  │   Producer DAG            │      │   Consumer DAG             │  │
│  │   (Every 2 minutes)       │      │   (Every 2 minutes)        │  │
│  │                           │      │                            │  │
│  │  1. Generate 15k logs     │      │  1. Poll Kafka messages    │  │
│  │  2. Faker + Random data   │      │  2. Regex parse logs       │  │
│  │  3. Produce to Kafka      │      │  3. Normalize timestamp    │  │
│  │                           │      │  4. Bulk index to ES       │  │
│  └───────────────────────────┘      └────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
           │                                        ▲
           │ SASL/SSL (Encrypted)                   │ SASL/SSL
           │                                        │
           ▼                                        │
    ┌─────────────────────────┐                    │
    │   Apache Kafka Cluster  │                    │
    │                         │────────────────────┘
    │   Topic: website_logs   │
    │   Partition: 3          │
    │   Replication: 3        │
    └─────────────────────────┘
                                          
                                          ▼
                              ┌──────────────────────────┐
                              │   Elasticsearch Cluster  │
                              │                          │
                              │   Index: logs            │
                              │   Shards: 1              │
                              │   Replicas: 1            │
                              └──────────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────────┐
                              │   Kibana Dashboard       │
                              │                          │
                              │   - Search logs          │
                              │   - Visualizations       │
                              │   - Real-time analytics  │
                              └──────────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────────┐
                              │   AWS Secrets Manager    │
                              │                          │
                              │   - Kafka credentials    │
                              │   - ES API keys          │
                              │   - Encrypted storage    │
                              └──────────────────────────┘
```

### Data Flow

1. **Log Generation (Producer DAG)**
   - Airflow triggers every 2 minutes
   - Generates 15,000 synthetic access logs using Faker
   - Produces messages to Kafka topic `website_logs`
   - Uses SASL/SSL for encrypted transmission

2. **Message Streaming (Kafka)**
   - Receives logs from producer
   - Stores in distributed partitions
   - Maintains high availability with replication
   - Consumer polls messages with `auto.offset.reset='latest'`

3. **Log Processing (Consumer DAG)**
   - Airflow triggers every 2 minutes
   - Polls messages from Kafka
   - Parses log lines using regex
   - Normalizes timestamps to ISO 8601
   - Batch processes 15,000 logs

4. **Indexing (Elasticsearch)**
   - Receives parsed logs via bulk API
   - Creates inverted index for fast search
   - Stores in `logs` index
   - Immediately available for queries

5. **Visualization (Kibana)**
   - Real-time dashboards
   - Query interface
   - Log analytics and monitoring

### Why This Architecture?

**Event-Driven Design:**
- Decouples producers and consumers
- Scales independently
- Handles backpressure naturally

**Kafka as Message Bus:**
- High throughput (millions of messages/sec)
- Durable message storage
- Replay capability

**Airflow Orchestration:**
- Visual workflow management
- Automatic retries on failure
- Detailed execution logs
- Dependency management

**Elasticsearch for Analytics:**
- Near real-time search
- Full-text capabilities
- Aggregations and analytics
- Scales horizontally

## 🛠 Tech Stack

| Technology | Version | Purpose | Key Features |
|------------|---------|---------|--------------|
| **Apache Airflow** | 3.1+ | Workflow orchestration | DAG scheduling, retries, monitoring |
| **Apache Kafka** | - | Message queue | Distributed streaming, high throughput |
| **Elasticsearch** | 9.1+ | Search engine | Full-text search, real-time indexing |
| **Kibana** | 9.1+ | Visualization | Dashboards, log explorer |
| **Faker** | 37.8+ | Synthetic data | Realistic IP addresses, user agents |
| **confluent-kafka** | 2.11+ | Kafka Python client | Based on librdkafka, high performance |
| **Boto3** | 1.40+ | AWS SDK | Secrets Manager integration |
| **uv** | Latest | Python package manager | Fast dependency resolution |
| **Python** | 3.12 | Programming language | Main development language |

## ✨ Key Features

### 1. Realistic Synthetic Log Generation

**Problem:** Testing data pipelines with production data exposes sensitive user information.

**Solution:** Generate realistic synthetic logs using Faker and Python's random module.

**Generated Log Format:**
```
123.45.67.89 - - [Jan 29 2026, 14:32:15] "GET /api/users HTTP/1.1" 200 12345 "https://google.com" Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)
```

**Generation Logic (`log_producer.py`):**

```python
def generate_log():
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    endpoints = ['/api/users', '/home', '/about', '/contact', '/services']
    statuses = [200, 301, 302, 400, 404, 500]
    
    user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0',
        'Mozilla/5.0 (iPad; CPU OS 16_7_6) AppleWebKit/605.1.15'
    ]
    
    referrers = ['https://example.com', 'https://google.com', '-']
    
    # Generate random values
    ip = fake.ipv4()
    timestamp = datetime.datetime.now().strftime('%b %d %Y, %H:%M:%S')
    method = random.choice(methods)
    endpoint = random.choice(endpoints)
    status = random.choice(statuses)
    size = random.randint(1000, 15000)
    referer = random.choice(referrers)
    user_agent = random.choice(user_agents)
    
    # Format as Apache/Nginx access log
    return f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size} "{referer}" {user_agent}'
```

**Components:**
- **IP Address**: Faker generates random IPv4 (`123.45.67.89`)
- **Timestamp**: Current time in Apache log format (`Jan 29 2026, 14:32:15`)
- **HTTP Method**: Random selection from GET/POST/PUT/DELETE
- **Endpoint**: Realistic API paths (`/api/users`, `/home`)
- **Status Code**: Common HTTP status codes (200, 404, 500)
- **Response Size**: Random bytes (1000-15000)
- **Referrer**: Simulated traffic sources
- **User-Agent**: Real browser/device identification strings

**Benefits:**
- ✅ No privacy concerns with synthetic data
- ✅ Controllable data volume and patterns
- ✅ Test edge cases (errors, spikes)
- ✅ Reproducible test scenarios

### 2. Secure Credential Management with AWS Secrets Manager

**Problem:** Hardcoding Kafka passwords and Elasticsearch API keys in code is a security risk.

**Solution:** Centralize secrets in AWS Secrets Manager with IAM-based access control.

**Implementation (`utils.py`):**

```python
import boto3
import json
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_name, region_name='us-east-1'):
    """
    Retrieve secrets from AWS Secrets Manager
    - secret_name: Name or ARN of the secret
    - region_name: AWS region (default: us-east-1)
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        logger.error(f'Secret retrieval error: {e}')
        raise
```

**Secret JSON Structure:**

```json
{
  "KAFKA_BOOTSTRAP_SERVER": "your-kafka.cloud:9092",
  "KAFKA_SASL_USERNAME": "your_api_key",
  "KAFKA_SASL_PASSWORD": "your_api_secret",
  "ELASTICSEARCH_URL": "https://your-es.cloud:9200",
  "ELASTICSEARCH_API_KEY": "your_es_api_key"
}
```

**Usage in DAGs:**

```python
# Fetch secrets at runtime
secrets = get_secret('MWAA_Side_Project_Secret')

# Use in Kafka config
kafka_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD']
}
```

**Advantages:**
- ✅ No credentials in source code
- ✅ IAM role-based access control
- ✅ Automatic credential rotation support
- ✅ CloudTrail audit logging
- ✅ Encrypted at rest and in transit

### 3. High-Throughput Kafka Producer

**Configuration:**

```python
kafka_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',     # Encrypted transport
    'sasl.mechanisms': 'PLAIN',          # SASL mechanism
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'session.timeout.ms': 50000          # Session timeout
}

producer = Producer(kafka_config)
```

**Production Logic:**

```python
def product_logs(**context):
    producer = create_kafka_producer(kafka_config)
    topic = 'website_logs'
    
    for _ in range(15000):
        log = generate_log()
        
        try:
            # Asynchronous produce with callback
            producer.produce(
                topic,
                log.encode('utf-8'),
                on_delivery=delivery_report
            )
            producer.flush()  # Force immediate send
        except Exception as e:
            logger.error(f'Error producing log: {e}')
            raise
    
    logger.info(f'Produced 15,000 logs to topic {topic}')
```

**Delivery Callback:**

```python
def delivery_report(err, msg):
    """Called when message is delivered or fails"""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Delivered to {msg.topic()}[{msg.partition()}]')
```

**Key Points:**
- **Asynchronous production**: Non-blocking, high throughput
- **Delivery guarantees**: Callback confirms success/failure
- **Error handling**: Logs errors and raises to fail Airflow task
- **SASL/SSL**: Encrypted authentication and data transfer

**Performance Note:**
- Current: `flush()` after every message (simple, slower)
- Production: Batch 1000 messages then flush (10x faster)

### 4. Reliable Kafka Consumer

**Configuration:**

```python
consumer_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'group.id': 'mwaa_log_indexer',      # Consumer group
    'auto.offset.reset': 'latest'         # Start from latest
}

consumer = Consumer(consumer_config)
consumer.subscribe(['website_logs'])
```

**Consumption Loop:**

```python
logs = []

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            break  # No more messages
        
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                break  # End of partition
            raise KafkaException(msg.error())
        
        # Decode and parse
        log_entry = msg.value().decode('utf-8')
        parsed_log = parsed_log_entry(log_entry)
        
        if parsed_log:
            logs.append(parsed_log)
        
        # Bulk index when buffer is full
        if len(logs) >= 15000:
            bulk_index_to_elasticsearch(logs)
            logs = []  # Reset buffer
            
finally:
    consumer.close()  # Always close to commit offsets
```

**Consumer Group Benefits:**
- **Parallel processing**: Multiple consumers share load
- **Fault tolerance**: If one consumer fails, others continue
- **Offset management**: Tracks which messages are processed

### 5. Regex-Based Log Parsing

**Challenge:** Convert unstructured log strings into structured JSON.

**Solution:** Named capture groups in regex pattern.

**Parsing Logic (`logs_processing_pipeline.py`):**

```python
import re
import datetime

def parsed_log_entry(log_entry):
    # Regex with named groups
    pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*?)\] "(?P<method>\w+) (?P<endpoint>[\w/]+) (?P<protocol>[\w/\.]+)'
    
    match = re.match(pattern, log_entry)
    
    if not match:
        logger.warning(f"Invalid log format: {log_entry}")
        return None
    
    data = match.groupdict()
    
    try:
        # Normalize timestamp to ISO 8601
        parsed_timestamp = datetime.datetime.strptime(
            data['timestamp'],
            '%b %d %Y, %H:%M:%S'
        )
        data['@timestamp'] = parsed_timestamp.isoformat()
    except ValueError:
        logger.error(f'Timestamp parsing error: {data["timestamp"]}')
        return None
    
    return data
```

**Input (raw log):**
```
123.45.67.89 - - [Jan 29 2026, 14:32:15] "GET /api/users HTTP/1.1" 200 12345
```

**Output (parsed JSON):**
```json
{
  "ip": "123.45.67.89",
  "timestamp": "Jan 29 2026, 14:32:15",
  "@timestamp": "2026-01-29T14:32:15",
  "method": "GET",
  "endpoint": "/api/users",
  "protocol": "HTTP/1.1"
}
```

**Why `@timestamp`?**
- Elasticsearch convention for time-series data
- Enables time-based queries and aggregations
- ISO 8601 format for consistency

### 6. Elasticsearch Bulk Indexing

**Problem:** Indexing 15,000 documents one-by-one = 15,000 HTTP requests (slow)

**Solution:** Bulk API sends all documents in one request (fast)

**Implementation:**

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

def consume_and_index_logs(**context):
    es_config = {
        'hosts': [secrets['ELASTICSEARCH_URL']],
        'api_key': secrets['ELASTICSEARCH_API_KEY']
    }
    es = Elasticsearch(**es_config)
    
    index_name = 'logs'
    
    # Create index if not exists
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        logger.info(f'Created index: {index_name}')
    
    # Prepare bulk actions
    actions = [
        {
            '_op_type': 'create',
            '_index': index_name,
            '_source': log
        }
        for log in logs
    ]
    
    # Execute bulk indexing
    success, failed = bulk(es, actions, refresh=True)
    logger.info(f'Indexed {success} logs, {len(failed)} failed')
```

**Bulk API Advantages:**
- **Performance**: 100x faster than individual inserts
- **Network efficiency**: Single HTTP request
- **Atomicity**: All-or-nothing per batch
- **Error handling**: Partial failures reported

**`refresh=True` explanation:**
- Default: Documents searchable after ~1 second
- `refresh=True`: Immediately searchable (for real-time queries)
- Trade-off: Slightly slower indexing

### 7. Airflow DAG Orchestration

**Producer DAG Structure:**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime

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
    schedule_interval='*/2 * * * *',  # Every 2 minutes
    start_date=datetime.datetime(2025, 9, 30),
    catchup=False,
    tags=['logs', 'kafka', 'production']
)

produce_logs_task = PythonOperator(
    task_id='generate_and_produce_logs',
    python_callable=product_logs,
    dag=dag
)
```

**Consumer DAG Structure:**

```python
dag = DAG(
    dag_id='log_consumption_pipeline',
    default_args=default_args,
    description='Consume and index synthetic logs',
    schedule_interval='*/2 * * * *',
    start_date=datetime.datetime(2025, 9, 30),
    catchup=False,
    tags=['logs', 'kafka', 'production']
)

consume_logs_task = PythonOperator(
    task_id='generate_and_consume_logs',
    python_callable=consume_and_index_logs,
    dag=dag
)
```

**Airflow Benefits:**
- **Visual workflow**: Graphical DAG representation
- **Automatic retries**: Configurable retry logic
- **Detailed logging**: Per-task execution logs
- **Dependency management**: Task dependencies and triggers
- **Alerting**: Email/Slack notifications on failures
- **Backfill support**: Reprocess historical data

**Schedule Coordination:**
- Both DAGs run every 2 minutes
- Producer generates 15k logs → Consumer processes them
- Offset ensures consumer doesn't miss messages

## 📁 Project Structure

```
realtime-logs-processing/
├── dags/
│   ├── log_producer.py              # Producer DAG (generate & send logs)
│   ├── logs_processing_pipeline.py  # Consumer DAG (consume & index logs)
│   └── utils.py                     # AWS Secrets Manager helper
├── pyproject.toml                   # uv project config & dependencies
├── .python-version                  # Python version (3.12)
├── LICENSE                          # MIT License
└── README.md                        # This documentation
```

### File Descriptions

**`dags/log_producer.py`:**
- Defines `log_generation_pipeline` DAG
- Generates 15,000 synthetic logs with Faker
- Produces messages to Kafka topic `website_logs`
- Runs every 2 minutes

**`dags/logs_processing_pipeline.py`:**
- Defines `log_consumption_pipeline` DAG
- Consumes messages from Kafka
- Parses logs with regex
- Bulk indexes to Elasticsearch
- Runs every 2 minutes

**`dags/utils.py`:**
- Helper function `get_secret()`
- Fetches credentials from AWS Secrets Manager
- Used by both DAGs

**`pyproject.toml`:**
- uv package manager configuration
- Lists all Python dependencies
- Managed with `uv sync`

## 📦 Prerequisites

### Required Services

- **AWS Account** (for Secrets Manager)
- **Kafka Cluster** (Confluent Cloud or self-hosted)
- **Elasticsearch Cluster** (Elastic Cloud or self-hosted)
- **Python 3.12+**
- **uv package manager**

### System Requirements

- **OS**: macOS, Linux, or Windows (WSL recommended)
- **RAM**: 4GB minimum (8GB recommended for local Kafka/ES)
- **Disk**: 10GB free space

### IAM Permissions

Your AWS credentials need:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:*:*:secret:MWAA_Side_Project_Secret-*"
  }]
}
```

## 🚀 Installation & Setup

### Step 1: Install uv Package Manager

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### Step 2: Clone Repository & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/realtime-logs-processing.git
cd realtime-logs-processing

# Install dependencies (creates virtual environment automatically)
uv sync
```

**What `uv sync` does:**
1. Reads `pyproject.toml`
2. Creates Python 3.12 virtual environment
3. Installs all dependencies:
   - apache-airflow >= 3.1.0
   - confluent-kafka >= 2.11.1
   - faker >= 37.8.0
   - boto3 >= 1.40.40
   - elasticsearch >= 9.1.1

### Step 3: Set Up Kafka Cluster

**Option A: Confluent Cloud (Recommended for beginners)**

1. Sign up at [confluent.cloud](https://confluent.cloud/)
2. Create a Kafka cluster (Basic tier free for 30 days)
3. Create topic: `website_logs`
   - Partitions: 3
   - Replication factor: 3
4. Create API Key (SASL/PLAIN authentication)
5. Note down:
   - Bootstrap server (e.g., `pkc-xxxxx.us-east-1.aws.confluent.cloud:9092`)
   - API Key (username)
   - API Secret (password)

**Option B: Local Kafka with Docker**

```bash
# Create docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

# Start services
docker-compose up -d

# Create topic
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic website_logs \
  --partitions 3 \
  --replication-factor 1
```

### Step 4: Set Up Elasticsearch

**Option A: Elastic Cloud**

1. Sign up at [cloud.elastic.co](https://cloud.elastic.co/)
2. Create deployment (14-day free trial)
3. Create API Key:
   - Elasticsearch → Security → API Keys
   - Name: `log_indexer`
   - Permissions: `create_index`, `write`, `manage`
4. Note down:
   - Cloud ID or HTTPS endpoint
   - API Key

**Option B: Local Elasticsearch with Docker**

```bash
# Run Elasticsearch
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:9.1.0

# Run Kibana (optional, for visualization)
docker run -d \
  --name kibana \
  --link elasticsearch \
  -p 5601:5601 \
  docker.elastic.co/kibana/kibana:9.1.0

# Verify Elasticsearch is running
curl http://localhost:9200
```

### Step 5: Configure AWS Secrets Manager

**Create the secret:**

```bash
aws secretsmanager create-secret \
  --name MWAA_Side_Project_Secret \
  --description "Credentials for realtime log processing pipeline" \
  --secret-string '{
    "KAFKA_BOOTSTRAP_SERVER": "your-kafka.cloud:9092",
    "KAFKA_SASL_USERNAME": "your_api_key",
    "KAFKA_SASL_PASSWORD": "your_api_secret",
    "ELASTICSEARCH_URL": "https://your-es-cluster.cloud:9200",
    "ELASTICSEARCH_API_KEY": "your_es_api_key"
  }'
```

**For local Kafka/ES (no authentication):**

```bash
aws secretsmanager create-secret \
  --name MWAA_Side_Project_Secret \
  --secret-string '{
    "KAFKA_BOOTSTRAP_SERVER": "localhost:9092",
    "KAFKA_SASL_USERNAME": "",
    "KAFKA_SASL_PASSWORD": "",
    "ELASTICSEARCH_URL": "http://localhost:9200",
    "ELASTICSEARCH_API_KEY": ""
  }'
```

**Grant IAM permissions:**

Attach this policy to your IAM user/role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:MWAA_Side_Project_Secret-*"
  }]
}
```

**Verify secret:**

```bash
aws secretsmanager get-secret-value \
  --secret-id MWAA_Side_Project_Secret \
  --query SecretString \
  --output text | jq
```

### Step 6: Initialize Airflow

```bash
# Set Airflow home directory
export AIRFLOW_HOME="${PWD}/.airflow"

# Ensure DAGs folder is recognized
mkdir -p $AIRFLOW_HOME/dags
ln -s ${PWD}/dags $AIRFLOW_HOME/dags

# Initialize Airflow metadata database
uv run airflow db init

# Create admin user
uv run airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

**What happens:**
- SQLite database created at `$AIRFLOW_HOME/airflow.db`
- Default configuration at `$AIRFLOW_HOME/airflow.cfg`
- Admin user with full privileges

### Step 7: Start Airflow Services

Open **two terminal windows**:

**Terminal 1 - Webserver:**
```bash
export AIRFLOW_HOME="${PWD}/.airflow"
uv run airflow webserver --port 8080
```

**Terminal 2 - Scheduler:**
```bash
export AIRFLOW_HOME="${PWD}/.airflow"
uv run airflow scheduler
```

**Access Airflow UI:**
1. Open browser: http://localhost:8080
2. Login with `admin` / `admin`
3. You should see the Airflow dashboard

### Step 8: Enable DAGs

In the Airflow UI:

1. Navigate to **DAGs** page
2. Find `log_generation_pipeline` → Toggle **ON**
3. Find `log_consumption_pipeline` → Toggle **ON**
4. Wait for scheduled execution (every 2 minutes) or click **Play** button to trigger manually

**Verify execution:**
- Click on DAG name → Grid view
- Green boxes = successful runs
- Click on task boxes → View Logs

## 💻 Usage

### Monitoring DAG Execution

**In Airflow UI:**

1. **DAGs Overview:**
   - Shows all DAGs with status
   - Last run time and next schedule

2. **Graph View:**
   - Visual representation of task dependencies
   - Click tasks to see details

3. **Grid View:**
   - Historical run matrix
   - Color-coded status (green=success, red=failed)

4. **Task Logs:**
   - Click task box → Logs tab
   - See detailed execution output
   - Debug errors here

**Example log output (Producer):**

```
[2026-01-29 14:32:15,123] INFO - Generated log: 123.45.67.89 - - [Jan 29 2026, 14:32:15] ...
[2026-01-29 14:32:15,234] INFO - Delivered to website_logs[0]
[2026-01-29 14:32:15,345] INFO - Delivered to website_logs[1]
...
[2026-01-29 14:35:42,678] INFO - Produced 15,000 logs to topic website_logs
```

**Example log output (Consumer):**

```
[2026-01-29 14:35:45,123] INFO - Polling Kafka messages...
[2026-01-29 14:35:46,234] INFO - Parsed log: {'ip': '123.45.67.89', 'method': 'GET', ...}
[2026-01-29 14:35:55,678] INFO - Indexed 15000 logs, 0 failed
```

### Querying Elasticsearch

**Using Kibana (Recommended):**

1. Open Kibana: http://localhost:5601
2. Navigate to **Discover**
3. Create Index Pattern: `logs*`
4. Select `@timestamp` as time field

**Search examples:**
```
method: "GET"
status: 404
ip: "123.*"
endpoint: "/api/users"
```

**Using Elasticsearch REST API:**

**Search all logs:**
```bash
curl -X GET "localhost:9200/logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": { "match_all": {} },
    "size": 10,
    "sort": [{ "@timestamp": { "order": "desc" }}]
  }'
```

**Filter by HTTP method:**
```bash
curl -X GET "localhost:9200/logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": { "method": "POST" }
    }
  }'
```

**Aggregate by status code:**
```bash
curl -X GET "localhost:9200/logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "status_codes": {
        "terms": { "field": "status.keyword" }
      }
    }
  }'
```

**Response example:**
```json
{
  "aggregations": {
    "status_codes": {
      "buckets": [
        { "key": "200", "doc_count": 12543 },
        { "key": "404", "doc_count": 1876 },
        { "key": "500", "doc_count": 581 }
      ]
    }
  }
}
```

**Using Python elasticsearch client:**

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Search 404 errors
results = es.search(
    index='logs',
    body={
        'query': {
            'match': {'status': '404'}
        },
        'size': 10
    }
)

for hit in results['hits']['hits']:
    log = hit['_source']
    print(f"{log['@timestamp']} - {log['ip']} - {log['method']} {log['endpoint']} - {log['status']}")
```

### Manual DAG Triggering

**Via Airflow UI:**
1. Click the **Play** button next to DAG name
2. Confirm trigger
3. Monitor in Grid view

**Via Airflow CLI:**

```bash
# Trigger producer DAG
uv run airflow dags trigger log_generation_pipeline

# Trigger consumer DAG
uv run airflow dags trigger log_consumption_pipeline

# Trigger with execution date
uv run airflow dags trigger log_generation_pipeline \
  --exec-date "2026-01-29T14:30:00"
```

### Inspecting Kafka Topics

**List topics:**
```bash
kafka-topics --bootstrap-server localhost:9092 --list
```

**Describe topic:**
```bash
kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic website_logs
```

**Consume messages (peek at data):**
```bash
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic website_logs \
  --from-beginning \
  --max-messages 10
```

**Check consumer group lag:**
```bash
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group mwaa_log_indexer
```

## ⚙️ Configuration

### Runtime Parameters

| Setting | File | Default | Description |
|---------|------|---------|-------------|
| **Kafka topic** | `log_producer.py` | `website_logs` | Topic name for log messages |
| **Messages per run** | `log_producer.py` | `15000` | Logs generated each execution |
| **Producer schedule** | `log_producer.py` | `*/2 * * * *` | Cron: every 2 minutes |
| **Consumer schedule** | `logs_processing_pipeline.py` | `*/2 * * * *` | Cron: every 2 minutes |
| **ES index** | `logs_processing_pipeline.py` | `logs` | Elasticsearch index name |
| **Consumer group** | `logs_processing_pipeline.py` | `mwaa_log_indexer` | Kafka consumer group ID |
| **Secret name** | Both DAGs | `MWAA_Side_Project_Secret` | AWS Secrets Manager key |
| **AWS region** | `utils.py` | `us-east-1` | Secrets Manager region |

### Customizing Generation Volume

**Edit `log_producer.py`:**

```python
# Change from 15000 to 50000
for _ in range(50000):  # Line ~75
    log = generate_log()
    producer.produce(topic, log.encode('utf-8'))
```

**Also update consumer batch size:**

```python
# In logs_processing_pipeline.py, line ~95
if len(logs) >= 50000:  # Match producer count
    bulk(es, actions, refresh=True)
```

### Changing Schedule Frequency

**Edit DAG schedule:**

```python
# Every 5 minutes instead of 2
schedule_interval='*/5 * * * *'

# Hourly
schedule_interval='0 * * * *'

# Daily at midnight
schedule_interval='0 0 * * *'
```

### Adjusting Kafka Configuration

**Add more producer configs:**

```python
kafka_config = {
    'bootstrap.servers': secrets['KAFKA_BOOTSTRAP_SERVER'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': secrets['KAFKA_SASL_USERNAME'],
    'sasl.password': secrets['KAFKA_SASL_PASSWORD'],
    'session.timeout.ms': 50000,
    
    # Additional configs
    'acks': 'all',                    # Wait for all replicas
    'compression.type': 'gzip',       # Compress messages
    'linger.ms': 10,                  # Batch window
    'batch.size': 16384               # Batch size in bytes
}
```

## 📊 Monitoring

### Airflow Metrics

**Key metrics to watch:**
- **DAG Success Rate**: % of successful runs
- **Task Duration**: Average task execution time
- **Failure Rate**: Number of failed tasks
- **Schedule Delay**: Lag behind schedule

**Access metrics:**
- UI: Browse & Monitoring → Dashboard
- CLI: `airflow dags list-runs -d log_generation_pipeline`

### Kafka Monitoring

**Using Confluent Cloud Console:**
- Throughput (messages/sec)
- Consumer lag
- Partition distribution

**Using CLI:**

```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group mwaa_log_indexer

# Output shows:
# - Current offset
# - Log end offset
# - Lag (difference)
```

**Ideal state:** Lag = 0 (consumer keeping up)

### Elasticsearch Monitoring

**Using Kibana:**
- Stack Monitoring → Elasticsearch
- Index size and document count
- Indexing rate

**Using API:**

```bash
# Index stats
curl -X GET "localhost:9200/logs/_stats?pretty"

# Cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"

# Document count
curl -X GET "localhost:9200/logs/_count?pretty"
```

### AWS CloudWatch (if using AWS-managed services)

**Metrics to monitor:**
- Secrets Manager API call rate
- IAM authentication failures
- Lambda function errors (if using Lambda)

## 🔧 Troubleshooting

### Issue 1: Kafka Connection Failed

**Symptom:**
```
ERROR - Failed to connect to Kafka
confluent_kafka.KafkaException: Failed to connect
```

**Causes & Solutions:**

1. **Incorrect bootstrap server:**
   ```bash
   # Verify in secret
   aws secretsmanager get-secret-value \
     --secret-id MWAA_Side_Project_Secret \
     --query SecretString --output text | jq -r '.KAFKA_BOOTSTRAP_SERVER'
   
   # Test connectivity
   telnet your-kafka.cloud 9092
   ```

2. **Invalid SASL credentials:**
   - Verify API key hasn't been rotated
   - Check username/password in secret
   - Regenerate API key if needed

3. **Network firewall:**
   - Check security groups (AWS)
   - Verify port 9092 is open
   - Try from different network

4. **SASL mechanism mismatch:**
   ```python
   # Ensure correct mechanism
   'sasl.mechanisms': 'PLAIN'  # or 'SCRAM-SHA-256'
   ```

### Issue 2: Elasticsearch Indexing Failed

**Symptom:**
```
ERROR - Bulk indexing failed
elasticsearch.exceptions.AuthenticationException
```

**Causes & Solutions:**

1. **Invalid API key:**
   ```bash
   # Test API key
   curl -X GET "https://your-es.cloud:9200" \
     -H "Authorization: ApiKey YOUR_API_KEY"
   
   # Should return cluster info, not 401 error
   ```

2. **Insufficient permissions:**
   - Recreate API key with `create_index`, `write`, `manage` privileges
   - Or use superuser credentials for testing

3. **Index name contains invalid characters:**
   ```python
   # Must be lowercase, no spaces
   index_name = 'logs'  # ✅ Valid
   index_name = 'Logs'  # ❌ Invalid (uppercase)
   index_name = 'log data'  # ❌ Invalid (space)
   ```

4. **Connection timeout:**
   ```python
   # Increase timeout
   es = Elasticsearch(
       [secrets['ELASTICSEARCH_URL']],
       api_key=secrets['ELASTICSEARCH_API_KEY'],
       timeout=60  # Seconds
   )
   ```

### Issue 3: Log Parsing Errors

**Symptom:**
```
WARNING - Invalid log format: ...
```

**Causes & Solutions:**

1. **Regex doesn't match log format:**
   - Print the actual log line
   - Compare with regex pattern
   - Test regex at [regex101.com](https://regex101.com/)

2. **Timestamp format mismatch:**
   ```python
   # Ensure format string matches generated timestamp
   datetime.datetime.strptime(
       data['timestamp'],
       '%b %d %Y, %H:%M:%S'  # Must match: "Jan 29 2026, 14:32:15"
   )
   ```

3. **Encoding issues:**
   ```python
   # Ensure UTF-8 encoding
   log_entry = msg.value().decode('utf-8')
   ```

### Issue 4: DAGs Not Appearing in Airflow UI

**Symptom:** DAGs missing from UI after enabling

**Causes & Solutions:**

1. **Python syntax errors:**
   ```bash
   # Validate Python files
   python dags/log_producer.py
   python dags/logs_processing_pipeline.py
   ```

2. **DAGs folder not recognized:**
   ```bash
   # Check Airflow config
   airflow config get-value core dags_folder
   
   # Should point to: /path/to/project/dags
   ```

3. **Import errors:**
   ```bash
   # Check scheduler logs
   tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log
   ```

4. **Restart scheduler:**
   ```bash
   # Stop scheduler (Ctrl+C)
   # Start again
   uv run airflow scheduler
   ```

### Issue 5: AWS Secrets Retrieval Failed

**Symptom:**
```
ERROR - Secret retrieval error: An error occurred (AccessDenied)
```

**Causes & Solutions:**

1. **Missing IAM permissions:**
   ```bash
   # Check current IAM user/role
   aws sts get-caller-identity
   
   # Verify permissions
   aws iam get-user-policy --user-name YOUR_USER --policy-name SecretAccess
   ```

2. **Wrong secret name:**
   ```bash
   # List all secrets
   aws secretsmanager list-secrets
   
   # Verify exact name (case-sensitive)
   ```

3. **Wrong AWS region:**
   ```python
   # In utils.py, change region
   def get_secret(secret_name, region_name='us-west-2'):  # Your region
   ```

4. **AWS credentials not configured:**
   ```bash
   # Configure AWS CLI
   aws configure
   
   # Or set environment variables
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Issue 6: High Consumer Lag

**Symptom:** Kafka consumer can't keep up with producer

**Check lag:**
```bash
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group mwaa_log_indexer

# Output shows LAG column (should be < 1000)
```

**Solutions:**

1. **Increase consumer parallelism:**
   - Add more partitions to topic
   - Run multiple consumer instances

2. **Optimize bulk indexing:**
   ```python
   # Increase batch size
   if len(logs) >= 50000:  # Larger batches
       bulk(es, actions, refresh=False)  # Don't refresh immediately
   ```

3. **Reduce producer rate:**
   ```python
   # Generate fewer logs
   for _ in range(5000):  # Instead of 15000
   ```

## 🚀 Performance Optimization

### Producer Optimizations

**1. Batch flushing:**

```python
# Current (slow): flush every message
for _ in range(15000):
    producer.produce(topic, log)
    producer.flush()  # ❌ 15,000 network calls

# Optimized: batch flush
batch_size = 1000
for i in range(15000):
    producer.produce(topic, log)
    if (i + 1) % batch_size == 0:
        producer.flush()  # ✅ Only 15 network calls
```

**2. Enable compression:**

```python
kafka_config['compression.type'] = 'gzip'  # 5-10x smaller payloads
```

**3. Async delivery:**

```python
# Remove flush() entirely, rely on producer buffer
for _ in range(15000):
    producer.produce(topic, log, on_delivery=delivery_report)

# Flush only at the end
producer.flush()
```

### Consumer Optimizations

**1. Larger poll batches:**

```python
# Poll for more messages at once
msgs = consumer.consume(num_messages=1000, timeout=1.0)

for msg in msgs:
    if not msg.error():
        parsed = parsed_log_entry(msg.value().decode('utf-8'))
        logs.append(parsed)
```

**2. Parallel processing:**

```python
# Use multiprocessing to parse logs
from multiprocessing import Pool

with Pool(4) as pool:
    parsed_logs = pool.map(parsed_log_entry, raw_logs)
```

### Elasticsearch Optimizations

**1. Larger bulk size:**

```python
# Increase from 15000 to 50000
if len(logs) >= 50000:
    bulk(es, actions)
```

**2. Disable refresh for faster indexing:**

```python
# Only refresh at the end
bulk(es, actions, refresh=False)

# Manual refresh after all batches
es.indices.refresh(index='logs')
```

**3. Use index templates:**

```python
# Define mapping upfront for better performance
es.indices.put_template(
    name='logs_template',
    body={
        'index_patterns': ['logs*'],
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0  # No replicas for testing
        },
        'mappings': {
            'properties': {
                '@timestamp': {'type': 'date'},
                'ip': {'type': 'ip'},
                'method': {'type': 'keyword'},
                'endpoint': {'type': 'keyword'},
                'status': {'type': 'integer'}
            }
        }
    }
)
```

### Expected Throughput

**After optimizations:**
- **Producer**: 50,000 messages/sec
- **Consumer**: 30,000 messages/sec
- **Elasticsearch**: 20,000 docs/sec (bulk insert)

## 🔮 Future Enhancements

### Planned Features

- [ ] **Data quality monitoring** with Great Expectations
  - Validate log format before indexing
  - Alert on anomalies (e.g., 90% 500 errors)

- [ ] **Dead Letter Queue (DLQ)** for failed messages
  - Send unparseable logs to separate Kafka topic
  - Retry with backoff

- [ ] **Prometheus + Grafana monitoring**
  - Producer/consumer lag metrics
  - Elasticsearch indexing rate
  - Airflow task duration

- [ ] **Multiple log formats support**
  - JSON logs
  - Syslog format
  - Custom formats via config

- [ ] **Data deduplication**
  - Use Elasticsearch `_id` based on log hash
  - Prevent duplicate indexing

- [ ] **Schema Registry integration**
  - Define message schema in Avro/Protobuf
  - Validate messages at produce/consume time

- [ ] **Alerting on anomalies**
  - Slack/Email alerts for high error rates
  - PagerDuty integration for critical failures

- [ ] **Cost optimization**
  - Archive old logs to S3 (cheaper storage)
  - Use Elasticsearch lifecycle management (ILM)

### Contribution Ideas

Contributions welcome! Areas to improve:

- **Performance**: Further optimize bulk operations
- **Testing**: Add unit tests for parsing logic
- **Documentation**: More query examples
- **Monitoring**: Additional Grafana dashboards
- **Security**: Implement mTLS for Kafka

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Adam Chang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- **Apache Airflow Community** - Excellent orchestration platform and documentation
- **Confluent** - Kafka Python client and cloud platform
- **Elastic** - Elasticsearch and Kibana for search and visualization
- **Faker** - Realistic synthetic data generation
- **AWS** - Secrets Manager for secure credential management
- **CodeWithYu** - [Data Engineer Youtuber](linkedin.com/in/yusuf-ganiyu-b90140107)

## 📚 Additional Resources

### Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Elasticsearch Python Client](https://www.elastic.co/docs/reference/elasticsearch/clients/python)
- [AWS Secrets Manager](https://aws.amazon.com/tw/secrets-manager/)

### Tutorials
- [Kafka Quickstart](https://kafka.apache.org/quickstart/)
- [Elasticsearch Getting Started](https://www.elastic.co/virtual-events/getting-started-elasticsearch)
- [Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html)

### Community
- [Airflow Slack](https://apache-airflow-slack.herokuapp.com/)
- [Kafka Users Mailing List](https://kafka.apache.org/community/contact/)
- [Elastic Community Forums](https://discuss.elastic.co/c/elastic-community-ecosystem/12)

---

<p align="center">
  <strong>Built with ⚡ by Adam Chang</strong>
</p>

<p align="center">
  <a href="https://github.com/AdamXiang/realtime-logs-processing/issues">Report Bug</a> •
  <a href="https://github.com/AdamXiang/realtime-logs-processing/issues">Request Feature</a> •
  <a href="https://github.com/AdamXiang/realtime-logs-processing/pulls">Contribute</a>
</p>

<p align="center">⭐ Star this repo if you find it helpful!</p>
