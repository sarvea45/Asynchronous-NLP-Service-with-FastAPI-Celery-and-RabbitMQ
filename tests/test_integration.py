import time
import os
import pytest
import httpx

# This test should only be run against the real docker-compose environment
# Usage: RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py

API_URL = os.getenv("API_URL", "http://localhost:8000")

@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "1", reason="Requires real Docker environment. Set RUN_INTEGRATION_TESTS=1")
def test_end_to_end_flow():
    # 1. Submit a task
    response = httpx.post(
        f"{API_URL}/api/nlp/process", 
        json={"text": "Apple is buying a startup for $1B.", "task_type": "named_entity_recognition"}
    )
    assert response.status_code == 202
    task_id = response.json()["task_id"]
    
    # 2. Poll for completion
    max_retries = 30
    for i in range(max_retries):
        res = httpx.get(f"{API_URL}/api/nlp/status/{task_id}")
        assert res.status_code == 200
        data = res.json()
        
        if data["status"] == "COMPLETED":
            assert "entities" in data["result"]
            break
        elif data["status"] == "FAILED":
            pytest.fail(f"Task failed: {data['error_message']}")
            
        time.sleep(1)
    else:
        pytest.fail("Task timed out while processing.")
