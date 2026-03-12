from schema.user_schema import Register, Login, Update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schema.db_schema import Users
import bcrypt


class UserService:
    def password_hashing_function(password:str):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt(12)
        return bcrypt.hashpw(password, salt).decode('utf-8')
    
    def verify_password(password: str, hashed_password):
        password = password.encode('utf-8')
        hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password, hashed_password)
        
    # CRUD for the users
    def create_user(db: Session, data:Register):
        if data.password is not None:
            hashed_password = UserService.password_hashing_function(data.password)
        else:
            hashed_password = None
            
        new_user = Users(
            name = data.name,
            phone_number = data.phone_number,
            email = data.email,
            business_name = data.business_name,
            business_address = data.business_address,
            password = hashed_password
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {'success': True, 'user': new_user, 'message': 'Registeration successful'}
        except IntegrityError as e:
            db.rollback()
            return {
                "success": False,
                "message": "Duplicate account detected"
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": "Something went wrong pls try again"
            }
    
    def read_user_by_phone_number_and_password(db: Session, data: Login):

        user = db.query(Users).filter_by(phone_number=data.phone_number).first()

        if not user:
            return {
                "success": False,
                "message": "User does not exist. Please check phone number and password."
            }

        if not UserService.verify_password(data.password, user.password):
            return {
                "success": False,
                "message": "Incorrect password."
            }

        return {
            "success": True,
            "message": "Login successful",
            "user": user
        }
            
    def update_user(db: Session, id: int, data: Update):
        try:
            user = db.get(Users, id)

            if not user:
                return {"success": False, "message": "User does not exist"}

            update_data = data.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["password"] = UserService.password_hashing_function(update_data["password"])

            for key, value in update_data.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)

            return {"success": True, "message": "User details updated successfully"}

        except IntegrityError:
            db.rollback()
            return {"success": False, "message": "Duplicate value detected"}

        except Exception:
            db.rollback()
            return {"success": False, "message": "Something went wrong"}
        
    def delete_user(db: Session, id:int):
        try:
            user = db.get(Users, id)
            if not user:
                return {"success": False, "message": "User does not exist"}
            
            db.delete(user)
            db.commit()
            return {"success": True, "message": "User account deleted successfully"}
        except Exception as e:
           return {"success": True, "message": f"{e}"}