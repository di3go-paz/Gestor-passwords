from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import hashear_password, verificar_password, crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=schemas.UsuarioRespuesta)
def registrar(datos: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    existe = db.query(models.Usuario).filter(
        models.Usuario.email == datos.email
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con ese email"
        )

    nuevo_usuario = models.Usuario(
        email=datos.email,
        password_hash=hashear_password(datos.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == form_data.username
    ).first()

    if not usuario or not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    token = crear_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}