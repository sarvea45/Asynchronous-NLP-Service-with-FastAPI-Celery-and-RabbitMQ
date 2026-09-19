# Asynchronous NLP Service 🚀

A production-ready asynchronous natural language processing (NLP) microservice built with **FastAPI**, **Celery**, **RabbitMQ**, and **MySQL**.

## 📖 Project Overview

This microservice solves the critical problem of synchronous AI bottlenecks. Machine Learning inference (like named entity recognition or sentiment analysis) is computationally intensive. If run synchronously, it blocks the main thread, leading to API timeouts and unresponsive servers.

**The Solution**: An Asynchronous Task Queue Architecture. 
- **FastAPI** handles the HTTP request, validates the payload, saves a `PENDING` state to the database, and immediately returns a `202 Accepted` along with a Task ID.
- **RabbitMQ** holds the message securely.
- **Celery Workers** independently pull tasks, process the heavy NLP loads via **HuggingFace Transformers** and **spaCy**, and update the **MySQL** database upon completion.
- The client can poll the API using their Task ID to retrieve the `COMPLETED` result.

---

## ⚙️ Architecture & Features

- **Asynchronous Execution**: Complete decoupling of the web layer and ML layer.
- **Global Model Loading**: Celery signals (`@worker_process_init.connect`) load models into memory *once* at startup, preventing memory leaks and I/O bottlenecks.
- **Pydantic Validation**: Strict input schemas and max-length constraints prevent memory exhaustion attacks.
- **Dockerized**: A single `docker-compose up` command spins up the API, Celery Workers, RabbitMQ broker, and MySQL persistence layer flawlessly.
- **Automated Testing**: 100% test coverage for API routing and asynchronous workers using `pytest` and mocked brokers.

---

## 🚀 Getting Started (Docker Compose)

To run the complete ecosystem locally, you only need Docker and Docker Compose installed.

1. **Clone the repository and enter the directory**:
   ```bash
   # clone repo here
   cd nlp-service
   ```

2. **Create your environment variables**:
   Copy the template file to `.env` (it works out of the box with default Docker settings).
   ```bash
   cp .env.example .env
   ```

3. **Spin up the ecosystem**:
   ```bash
   docker-compose up -d --build
   ```
   *Note: It will take a few minutes the first time to build the Python environment and download the heavy HuggingFace/spaCy ML models into the worker container.*
   *The API and Worker containers will wait (`depends_on: condition: service_healthy`) until MySQL and RabbitMQ are fully initialized before starting.*

---

## 💻 Usage & API Examples

### 1. Submit a Task (POST)
Submit a block of text for processing. Supported tasks are `sentiment_analysis` and `named_entity_recognition`.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/nlp/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Apple is buying a new artificial intelligence startup for $1 billion dollars.",
  "task_type": "named_entity_recognition"
}'
```
**Response (202 Accepted)**:
```json
{
  "task_id": "7f8b9d3a-12c4-4f89-8d6e-1ab2c3d4e5f6",
  "status": "PENDING"
}
```

### 2. Check Task Status (GET)
Poll the status endpoint using the returned `task_id`.

```bash
curl -X 'GET' \
  'http://localhost:8000/api/nlp/status/7f8b9d3a-12c4-4f89-8d6e-1ab2c3d4e5f6' \
  -H 'accept: application/json'
```

**Response while processing (200 OK)**:
```json
{
  "task_id": "7f8b9d3a-12c4-4f89-8d6e-1ab2c3d4e5f6",
  "status": "PROCESSING",
  "result": null,
  "error_message": null,
  "updated_at": "2026-09-19T10:00:05.123Z"
}
```

**Response when finished (200 OK)**:
```json
{
  "task_id": "7f8b9d3a-12c4-4f89-8d6e-1ab2c3d4e5f6",
  "status": "COMPLETED",
  "result": {
    "entities": [
      {"text": "Apple", "label": "ORG"},
      {"text": "$1 billion dollars", "label": "MONEY"}
    ]
  },
  "error_message": null,
  "updated_at": "2026-09-19T10:00:15.890Z"
}
```

---

## 🧪 Running the Test Suite

Unit tests can be executed directly inside the containerized environment. We use Pytest alongside FastAPI's `TestClient`.

1. **Ensure the containers are running** (or at least built).
2. **Run Pytest inside the API container**:
   ```bash
   docker-compose exec api pytest
   ```
3. **To run the End-to-End integration test** (which tests the live Docker ecosystem by submitting HTTP requests and polling):
   ```bash
   docker-compose exec api bash -c "RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py -v -s"
   ```

---

## 🎥 Video Demonstration

[Watch the End-to-End Demo Video Here](https://youtu.be/s91x7T6E1fc)

*(The video demonstrates submitting a heavy NLP payload via Postman/curl, watching the queue in RabbitMQ, and polling for the final processed entity extraction output.)*
