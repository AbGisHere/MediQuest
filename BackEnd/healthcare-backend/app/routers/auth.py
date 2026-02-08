"""
Authentication router.
Handles user registration, login, token refresh, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.user import User
from app.models.audit import AuditAction
from app.schemas import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.services.audit import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Brute force protection settings
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user (admin, doctor, or patient).
    Returns access and refresh tokens.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.USER_CREATED,
        actor=user,
        resource_type="user",
        resource_id=user.id,
        description=f"User registered: {user.username} ({user.role.value})",
        ip_address=request.client.host if request.client else None
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role.value
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    Returns access and refresh tokens.
    Implements brute-force protection.
    """
    # Get user
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user:
        # Audit failed login
        AuditService.log_auth_event(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            user_id=None,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            error_message="User not found"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if account is locked due to failed attempts
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        if user.last_failed_login:
            lockout_until = user.last_failed_login + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            if datetime.now(timezone.utc) < lockout_until:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked due to too many failed attempts. Try again later."
                )
            else:
                # Reset failed attempts after lockout period
                user.failed_login_attempts = 0
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.now(timezone.utc)
        db.commit()
        
        # Audit failed login
        AuditService.log_auth_event(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            user_id=user.id,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            error_message="Invalid password"
        )
        
        # Check if brute force detected
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            AuditService.log_security_event(
                db=db,
                action=AuditAction.BRUTE_FORCE_DETECTED,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                description=f"Brute force detected for user: {user.username}",
                metadata={"user_id": user.id, "attempts": user.failed_login_attempts}
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.last_failed_login = None
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Audit successful login
    AuditService.log_auth_event(
        db=db,
        action=AuditAction.LOGIN_SUCCESS,
        user_id=user.id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        success=True
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role.value
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Audit token refresh
    AuditService.log_auth_event(
        db=db,
        action=AuditAction.TOKEN_REFRESH,
        user_id=user.id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        success=True
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role.value
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout (client should discard tokens).
    """
    # Audit logout
    AuditService.log_auth_event(
        db=db,
        action=AuditAction.LOGOUT,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        success=True
    )
    
    return {"message": "Successfully logged out"}
