from sqlalchemy.orm import Session
from schema.db_schema import Transactions, TransactionItem, Products
from schema.transactions_schema import TransactionCreate


class TransactionService:

    def createTransaction(db: Session, transaction_data: TransactionCreate, current_user_id: int):

        try:
            total_amount = 0
            items_list = []

            for item in transaction_data.items:

                subtotal = item.quantity * item.unit_price
                total_amount += subtotal

                new_item = TransactionItem(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=subtotal
                )

                items_list.append(new_item)

            new_transaction = Transactions(
                user_id=current_user_id,
                amount=total_amount,
                transaction_type=transaction_data.transaction_type,
                payment_method=transaction_data.payment_method,
                payment_status=transaction_data.payment_status,
                items=items_list
            )

            db.add(new_transaction)
            db.commit()
            db.refresh(new_transaction)

            return {
                "success": True,
                "transaction": new_transaction,
                "message": "Transaction created successfully"
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "transaction": None,
                "message": f"{e}"
            }

    def readTransactions(db: Session, current_user_id: int):

        results = db.query(Transactions).filter_by(user_id=current_user_id).all()

        if not results:
            return {
                "success": True,
                "transaction": None,
                "message": "No transactions found"
            }

        return {
            "success": True,
            "transaction": results,
            "message": "Transactions retrieved"
        }

    def readTransactionByID(db: Session, current_user_id: int, transaction_id: int):

        try:
            results = db.query(Transactions).filter_by(user_id=current_user_id).all()

            if not results:
                return {
                    "success": True,
                    "transaction": None,
                    "message": "You do not have any transactions"
                }

            if not any(transaction_id == result.id for result in results):
                return {
                    "success": False,
                    "transaction": None,
                    "message": "You cannot access a transaction not tied to your account"
                }

            transaction = db.get(Transactions, transaction_id)

            if not transaction:
                return {
                    "success": False,
                    "transaction": None,
                    "message": "Transaction not found"
                }

            return {
                "success": True,
                "transaction": transaction,
                "message": "Transaction retrieved"
            }

        except Exception as e:
            return {
                "success": False,
                "transaction": None,
                "message": f"{e}"
            }

    def deleteTransaction(db: Session, current_user_id: int, transaction_id: int):

        try:
            results = db.query(Transactions).filter_by(user_id=current_user_id).all()

            if not results:
                return {
                    "success": False,
                    "transaction": None,
                    "message": "You do not have any transactions"
                }

            if not any(transaction_id == result.id for result in results):
                return {
                    "success": False,
                    "transaction": None,
                    "message": "You cannot delete a transaction not tied to your account"
                }

            transaction = db.get(Transactions, transaction_id)

            if not transaction:
                return {
                    "success": False,
                    "transaction": None,
                    "message": "Transaction not found"
                }

            db.delete(transaction)
            db.commit()

            return {
                "success": True,
                "transaction": transaction,
                "message": "Transaction deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "transaction": None,
                "message": f"{e}"
            }