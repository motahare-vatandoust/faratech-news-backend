from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db.models.admin import Admin
from db.session import get_db
from models.admin import (
    AdminChangePasswordRequest,
    AdminLoginRequest,
    AdminRegisterRequest,
    AdminResponse,
    AuthTokenResponse,
)
from services import auth as auth_service

router = APIRouter(prefix="/admin", tags=["admin-auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def _to_admin_response(admin: Admin) -> AdminResponse:
    return AdminResponse(
        id=admin.id,
        email=admin.email,
        full_name=admin.full_name,
        is_active=admin.is_active,
        created_at=admin.created_at,
        updated_at=admin.updated_at,
    )


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    admin_id = auth_service.decode_access_token(credentials.credentials)
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    admin = db.get(Admin, UUID(admin_id))
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive",
        )
    return admin


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register_admin(data: AdminRegisterRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    if auth_service.get_admin_by_email(db, data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this email already exists",
        )

    admin = auth_service.create_admin(
        db, email=data.email, full_name=data.full_name, password=data.password
    )
    token = auth_service.create_access_token(admin_id=str(admin.id))

    return AuthTokenResponse(access_token=token, admin=_to_admin_response(admin))


@router.post("/login", response_model=AuthTokenResponse)
def login_admin(data: AdminLoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    admin = auth_service.authenticate_admin(
        db, email=data.email, password=data.password
    )
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = auth_service.create_access_token(admin_id=str(admin.id))
    return AuthTokenResponse(access_token=token, admin=_to_admin_response(admin))


@router.get("/me", response_model=AdminResponse)
def me(admin: Admin = Depends(get_current_admin)) -> AdminResponse:
    return _to_admin_response(admin)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: AdminChangePasswordRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
) -> None:
    changed = auth_service.change_admin_password(
        db,
        admin=admin,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
