from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from services.inventory_service import InventoryService as ivs
from dependency.db import get_db
from schema.product_schema import ProductCreate, ProductDisplay, ProductResponse, ProductUpdate
from routers import user_router, inventory_router, transactions_router
from dependency.current_user import get_current_user_token
from pydantic import BaseModel
from ai.intent_model import extract_order_data

app = FastAPI(
    version='0.1',
    description='Business Operations Support System'
)

app.include_router(user_router.router)
app.include_router(inventory_router.router)
app.include_router(transactions_router.router)


class UserMessage(BaseModel):
    message: str

@app.post("/process-message")
def process_message(user_msg: UserMessage):
    result = extract_order_data(user_msg.message)

    # 🔒 Validation layer (VERY IMPORTANT)
    if "error" in result:
        return result

    if result["confidence"] < 0.6:
        return {
            "status": "uncertain",
            "data": result
        }

    # 🎯 Trigger backend logic
    if result["intent"] == "CREATE_ORDER":
        return {
            "status": "success",
            "action": "create_order",
            "data": result
        }

    return {
        "status": "processed",
        "data": result
    }

