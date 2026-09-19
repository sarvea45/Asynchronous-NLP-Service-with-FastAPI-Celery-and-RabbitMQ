import traceback
from app.celery_app import celery_instance
from app.database import SessionLocal
from app.models import NLPTask
from app.nlp_engine import analyze_sentiment, extract_entities

@celery_instance.task(bind=True, max_retries=3)
def process_text_task(self, task_id: str):
    db = SessionLocal()
    task = db.query(NLPTask).filter(NLPTask.id == task_id).first()
    
    if not task:
        db.close()
        return

    try:
        # Update status to PROCESSING
        task.status = "PROCESSING"
        db.commit()

        # Execute NLP logic based on task_type
        if task.task_type == "sentiment_analysis":
            result = analyze_sentiment(task.input_text)
        elif task.task_type == "named_entity_recognition":
            result = extract_entities(task.input_text)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")

        # Update status to COMPLETED
        task.status = "COMPLETED"
        task.result = result
        db.commit()

    except Exception as e:
        # Update status to FAILED and save traceback
        task.status = "FAILED"
        task.error_message = traceback.format_exc()
        db.commit()
    finally:
        db.close()
