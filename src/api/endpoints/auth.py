from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..schemas.user import UserCreate, UserRead
from ..schemas.auth import Token
from ..models.user import User
from ..db.session import get_session
from ..core.security import get_password_hash, verify_password
from ..utils.jwt_handler import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Expects form-data:
      - grant_type (ignored, default "password")
      - username
      - password
      - scope (optional)
    """
    username = form_data.username
    password = form_data.password

    statement = select(User).where(User.username == username)
    db_user = session.exec(statement).first()

    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}