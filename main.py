from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from services.inventory_service import InventoryService as ivs
from dependency.db import get_db
from schema.product_schema import ProductCreate, ProductDisplay, ProductResponse, ProductUpdate
from routers import user_router, inventory_router, transactions_router
from dependency.current_user import get_current_user_token

app = FastAPI(
    version='0.1',
    description='Business Operations Support System'
)

app.include_router(user_router.router)
app.include_router(inventory_router.router)
app.include_router(transactions_router.router)
