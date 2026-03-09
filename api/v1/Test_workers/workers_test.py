from fastapi import APIRouter
from Elysium_Celery.tasks import idk_man,celery
from celery.result import AsyncResult


from pydantic import BaseModel


class Task_Id(BaseModel):
    id: str


router = APIRouter()


@router.post("/start/test/worker", tags=["test_worker"])
def some_test_worker():
    result=idk_man.delay()
    # result = celery.send_task('celery_config.some_task',kwargs={
    #     "test":"some_test",
    #     "tata":"byee"
    # })
    return {"id": result.id}


@router.post("/some/task/result", tags=["task_result"])
def get_some_task_result(task: Task_Id):
    result = AsyncResult(task.id, app=celery)
    return {"status": result.state, "result": result.result}
    
    