from fastapi import APIRouter
from .api import store 



router = APIRouter()


router.include_router(store.router)