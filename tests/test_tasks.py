import pytest
from unittest.mock import patch
from app.models import NLPTask
from app.tasks import process_text_task

@patch("app.tasks.analyze_sentiment")
@patch("app.tasks.SessionLocal")
def test_process_text_task_success(mock_session_maker, mock_analyze, db_session):
    # We will use the db_session fixture provided from conftest to mock SessionLocal
    mock_session_maker.return_value = db_session
    mock_analyze.return_value = {"sentiment": "Mock Positive"}
    
    # Create pending task
    task = NLPTask(input_text="I love this", task_type="sentiment_analysis", status="PENDING")
    db_session.add(task)
    db_session.commit()
    
    # Run task synchronously
    process_text_task(task.id)
    
    # Verify status changed
    db_session.refresh(task)
    assert task.status == "COMPLETED"
    assert task.result == {"sentiment": "Mock Positive"}

@patch("app.tasks.analyze_sentiment")
@patch("app.tasks.SessionLocal")
def test_process_text_task_failure(mock_session_maker, mock_analyze, db_session):
    mock_session_maker.return_value = db_session
    mock_analyze.side_effect = Exception("Model exploded")
    
    task = NLPTask(input_text="Crash it", task_type="sentiment_analysis", status="PENDING")
    db_session.add(task)
    db_session.commit()
    
    process_text_task(task.id)
    
    db_session.refresh(task)
    assert task.status == "FAILED"
    assert "Model exploded" in task.error_message
