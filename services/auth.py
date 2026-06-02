from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from db.models.admin import Admin

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_admin_by_email(db: Session, email: str) -> Optional[Admin]:
    stmt = select(Admin).where(Admin.email == email.lower().strip())
    return db.scalars(stmt).first()


def create_admin(db: Session, *, email: str, full_name: str, password: str) -> Admin:
    admin = Admin(
        email=email.lower().strip(),
        full_name=full_name.strip(),
        hashed_password=hash_password(password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def authenticate_admin(db: Session, *, email: str, password: str) -> Optional[Admin]:
    admin = get_admin_by_email(db, email)
    if admin is None or not admin.is_active:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin


def change_admin_password(
    db: Session, *, admin: Admin, current_password: str, new_password: str
) -> bool:
    if not verify_password(current_password, admin.hashed_password):
        return False
    admin.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(admin)
    return True


def create_access_token(*, admin_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": admin_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        return str(subject) if subject else None
    except jwt.PyJWTError:
        return None
