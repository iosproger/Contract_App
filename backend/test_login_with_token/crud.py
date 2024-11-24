from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()



def create_user(db: Session, name: str, hashed_password: bytes, active: bool):
    new_user = User(name=name, hashed_password=hashed_password,active=active)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, name: str, password: str):
    user = get_user_by_name(db, name)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def user_check( db: Session ,name : str = None) -> bool:

    if not (user := get_user_by_name(db=db,name=name)):
        return False

    return True
