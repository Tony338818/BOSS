from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schema.db_schema import Products, Users
from schema.product_schema import ProductCreate, ProductUpdate

class InventoryService:
    def createProduct(db: Session, product_data: ProductCreate, current_user_id:int):
        new_product = Products(
            user_id = current_user_id,
            **product_data.model_dump(exclude_unset=False)
        )
        
        try:
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return {
                'success': True,
                'product': new_product,
                'message': 'Product added successfully'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'product': None,
                'message': 'Failed to add product please try again'
            }
            
    def readProducts(db: Session, current_user_id:int):
        # user = db.get(Users, current_user_id)
        # if not user:
        #     return {
        #         'success': False,
        #         'data': [],
        #         'message': 'User not found!'
        #     }
            
        results = db.query(Products).filter_by(user_id = current_user_id)
        if not results:
            return {
                'success': True,
                'product': None,
                'message': 'No products Found'
            }
        
        products = [
            {
                'id': product.id,
                'name' : product.name,
                'quantity' : product.quantity,
                'cost_price' : product.cost_price,
                'selling_price' : product.selling_price,
                'supplier' : product.supplier,
                'img_url' : product.img_url,
                'description' : product.description,
                'buy_date' : product.buy_date,
                'expiry_date' : product.expiry_date
            } for product in results
        ]
        return {
                'success': True,
                'product': products,
                'message': 'Products retrieved'
            }
        
    def readProductByID(db: Session,current_user_id:int, product_id: int):
        try:
            results = db.query(Products).filter_by(user_id = current_user_id)
            if not results:
                return {
                    'success': True,
                    'product': None,
                    'message': 'No products Found'
                }
            result = db.get(Products, product_id)
            if not result:
                return 'Data does not exist in the DB'
            
            return result
        except Exception as e:
            return e
    def updateProduct(db: Session, current_user_id: int, product_id:int, data: ProductUpdate):
        try:
            results = db.query(Products).filter_by(user_id = current_user_id).all()
            if not results:
                return {
                    'success': True,
                    'product': None,
                    'message': 'You do not have any products in the database'
                }
                
            if not any(product_id == result.id for result in results):
                return {
                    'success': False,
                    'product': None,
                    'message': 'You cannot edit a product not tied to your account'
                }
                
            product = db.get(Products, product_id)
            if not product:
                return {
                    'success': False,
                    'product': None,
                    'message': 'No products Found'
                }
            
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(product, key, value)
                
            db.commit()
            return {
                'success': True,
                'product': product,
                'message':'Product detail Updated Successfully'
                }
        except Exception as e:
            return {
                'success': False,
                'product': None,
                'message':f'{e}'
                }
    def deleteProduct(db: Session, current_user_id: int, product_id: int):
        try:
            results = db.query(Products).filter_by(user_id = current_user_id).all()
            if not results:
                return {
                    'success': False,
                    'product': None,
                    'message': 'You do not have any products in the database'
                }
                
            if not any(product_id == result.id for result in results):
                return {
                    'success': False,
                    'product': None,
                    'message': 'You cannot delete a product not tied to your account'
                }
                
            product = db.get(Products, product_id)
           
            if not product:
                return {
                    'success': False,
                    'product': None,
                    'message': 'You cannot delete a product not tied to your account'
                }
           
            db.delete(product)
            db.commit()
            return {
                'success': True,
                'product': product,
                'message': 'product deleted successfully'
            }
        except Exception as e:
             return {
                'success': False,
                'product': None,
                'message': f'{e}'
            }