import pytest
from unittest.mock import patch
from app.models import NLPTask

def test_create_task_validation_error(client):
    # Test empty text
    response = client.post("/api/nlp/process", json={"text": "", "task_type": "sentiment_analysis"})
    assert response.status_code == 422
    
    # Test invalid task type
    response = client.post("/api/nlp/process", json={"text": "hello", "task_type": "invalid_type"})
    assert response.status_code == 422

@patch("app.main.process_text_task.delay")
def test_create_task_success(mock_delay, client):
    response = client.post("/api/nlp/process", json={"text": "Apple is great.", "task_type": "named_entity_recognition"})
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"
    mock_delay.assert_called_once_with(data["task_id"])

def test_get_task_not_found(client):
    response = client.get("/api/nlp/status/invalid-uuid")
    assert response.status_code == 404
    
def test_get_task_success(client, db_session):
    # Insert mock task
    task = NLPTask(input_text="Test", task_type="sentiment_analysis", status="COMPLETED", result={"sentiment": "POSITIVE"})
    db_session.add(task)
    db_session.commit()
    
    response = client.get(f"/api/nlp/status/{task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["status"] == "COMPLETED"
    assert data["result"] == {"sentiment": "POSITIVE"}
