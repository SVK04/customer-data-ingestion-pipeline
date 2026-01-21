# Customer Data Ingestion Pipeline

A Dockerized backend assessment implementing a customer data ingestion pipeline using Flask, FastAPI, and PostgreSQL.

## Project Overview

This project demonstrates a 3-service data pipeline architecture where customer data is fetched from a mock API, ingested into a database, and exposed via a query API.

The goal is to simulate a real-world backend ingestion workflow with pagination, idempotency, and Docker-based orchestration.

## Architecture Flow

Flask Mock Server (JSON) → FastAPI Ingestion Service → PostgreSQL Database → FastAPI Read APIs

### Components

1. Flask Mock Server  
   - Serves customer data from a static JSON file  
   - Supports pagination and single-record lookups  

2. FastAPI Pipeline Service  
   - Fetches paginated data from Flask  
   - Performs idempotent upserts into PostgreSQL  
   - Exposes APIs to query stored customers  

3. PostgreSQL  
   - Stores customer records using a relational schema  

## Tech Stack

- Language: Python 3.10+  
- Frameworks: Flask, FastAPI  
- Database: PostgreSQL 15  
- ORM: SQLAlchemy (synchronous)  
- Containerization: Docker, Docker Compose  

## Setup & Execution

### Prerequisites
- Docker
- Docker Compose

### Start All Services

```bash
docker compose up --build -d
```

Verify containers are running:

```bash
docker ps
```

View Logs
```bash
docker logs -f mock
docker logs -f pipeline
docker logs -f db
```

Stop Services
```bash
docker compose down
```

API Endpoints & Testing
Flask Mock Server (Port 5000)
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
curl "http://localhost:5000/api/customers/<customer_id>"
curl "http://localhost:5000/api/health"
```

FastAPI Pipeline Service (Port 8000)
```bash
curl -X POST "http://localhost:8000/api/ingest"
curl "http://localhost:8000/api/customers?page=1&limit=5"
curl "http://localhost:8000/api/customers/<customer_id>"
```

Database Inspection
```bash
docker exec -it db psql -U postgres -d customer_db
```

```sql
SELECT * FROM customers;
```

Design Decisions & Known Limitations

- The ingestion pipeline assumes a stable and well-formed JSON response from the mock Flask API.

- Only non-null fields from the source payload are used to update existing records, preventing accidental data loss.

- Ingestion is executed as a single transaction for atomicity.

- Date and timestamp formats are assumed to match the database schema.

