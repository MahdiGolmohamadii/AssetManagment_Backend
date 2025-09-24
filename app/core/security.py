from passlib.context import CryptContext




pwd_cntx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_plain_password(password: str):
    return pwd_cntx.hash(password)