from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import NLPTask
from app.schemas import TaskCreateRequest, TaskResponse, TaskStatusResponse
# We will import the Celery task here. The import will work once tasks.py is created.
from app.tasks import process_text_task

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asynchronous NLP Service")

@app.post("/api/nlp/process", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
def create_nlp_task(request: TaskCreateRequest, db: Session = Depends(get_db)):
    # Create a new PENDING task record
    new_task = NLPTask(
        input_text=request.text,
        task_type=request.task_type.value,
        status="PENDING"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Dispatch Celery task
    process_text_task.delay(new_task.id)

    return {"task_id": new_task.id, "status": new_task.status}


@app.get("/api/nlp/status/{task_id}", response_model=TaskStatusResponse)
def get_nlp_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(NLPTask).filter(NLPTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error_message": task.error_message,
        "updated_at": task.updated_at
    }
