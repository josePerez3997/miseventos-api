from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions import CredentialsException
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import Token, Login, Register, PasswordReset, PasswordUpdate
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_in: Register,
    auth_service: AuthService = Depends(),
    user_service: UserService = Depends(),
):
    """
    Register a new user
    """
    try:
        user = auth_service.register_new_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise CredentialsException(detail="Incorrect email or password")
    
    return auth_service.create_token_for_user(user)

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    login_data: Login,
    auth_service: AuthService = Depends(),
):
    """
    Login endpoint for API clients (non-form based)
    """
    user = auth_service.authenticate_user(
        email=login_data.email, password=login_data.password
    )
    if not user:
        raise CredentialsException(detail="Incorrect email or password")
    
    return auth_service.create_token_for_user(user)

@router.post("/password-reset", status_code=status.HTTP_204_NO_CONTENT)
def password_reset(
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(),
):
    """
    Password reset request
    
    In a real application, this would send an email with a token
    For this example, we just check if the user exists
    """
    auth_service.reset_password(email=password_reset.email)
    return None

@router.post("/password-update", status_code=status.HTTP_204_NO_CONTENT)
def password_update(
    password_update: PasswordUpdate,
    auth_service: AuthService = Depends(),
):
    """
    Update password using reset token
    
    In a real application, this would validate the token from the email
    For this example, we don't implement token validation
    """
    return None

@router.get("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_active_user)):
    """
    Test access token
    """
    return current_user