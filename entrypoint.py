from fastapi import FastAPI
from schemas import UserCreate, UserLogin, PostCreate
import uvicorn
from database_config import SessionLocal, UserModel, PostModel
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from utils import hash_password, create_token, get_current_user, get_db, require_roles

app = FastAPI(
    title="Servidor Clase",
    description="Servidor para la clase de FastAPI",
    version="1.0.0"
)

@app.get("/")
def hello_check():
    return {"message": "Servidor funcionando correctamente"}

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    data = user.model_dump()
    data["password"] = hash_password(data["password"])
    new_user = UserModel(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(username=form_data.username).first()
    if not user or user.password != hash_password(form_data.password):
        return {"message":"Credenciales invalidas"}
    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/list")
def users_lists( db: Session = Depends(get_db),current_user: UserModel = Depends(require_roles("admin"))):
    user = db.query(UserModel).all()
    return user

@app.get("/users/{user_id}")
def me(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return {"message":"usuario no encontrado"}
    return user

@app.delete("/users/{user_id}")
def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return {"message":"usuario no encontrado"}
    db.delete(user)
    db.commit()
    return {"message": f"Usuario con ID {user_id} eliminado",
            "user":user}

@app.post("/posts/")
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(require_roles("user", "admin"))):
    new_post = PostModel(title=post.title, 
                         content=post.content, 
                         user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/")
def get_my_posts(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return db.query(PostModel).filter_by(user_id=current_user.id).all()

@app.get("/protected/admin-area")
def admin_area(current_user: UserModel = Depends(require_roles("admin"))):
    return {
        "msg": "Welcome to the admin area",
        "data":current_user
    }

@app.get("/protected/admin-user-area")
def admin_user_area(current_user: UserModel = Depends(require_roles("admin","user"))):
    return {
        "msg": "Welcome to the admin user area",
        "data":current_user
        }

@app.get("/protected/user-area")
def user_area(current_user: UserModel = Depends(require_roles("user"))):
    return {
        "msg": "Welcome to the user area",
        "data":current_user
        }


if __name__ == "__main__":
    uvicorn.run("entrypoint:app", 
                host="localhost", 
                port=8000, 
                reload=True)