from fastapi import APIRouter, Request, Depends

#------ Удалить

router = APIRouter()

@router.post("/notifications")
async def user_notifications(request: Request):
    pass

@router.get("/notifications")
async def users_list_notifications(request: Request):
    pass

@router.delete("/notifications/{id}")
async def users_delete_notifications(request: Request):
    pass