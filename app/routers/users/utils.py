from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
  

email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

def is_valid_email(email: str) -> bool:  
    return re.search(email_regex, email)
