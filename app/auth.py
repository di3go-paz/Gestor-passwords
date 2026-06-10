from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app import models
from app.database import get_db
import os
import base64

load_dotenv()

# ─── CONFIGURACIÓN ──────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# ─── HASHEO ─────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)

# ─── ENCRIPTACIÓN ───────────────────────────────────────

def obtener_fernet():
    key_bytes = ENCRYPTION_KEY.encode()
    key_b64 = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'0'))
    return Fernet(key_b64)

def encriptar(texto: str) -> str:
    f = obtener_fernet()
    return f.encrypt(texto.encode()).decode()

def desencriptar(texto_encriptado: str) -> str:
    f = obtener_fernet()
    return f.decrypt(texto_encriptado.encode()).decode()

# ─── JWT ────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def crear_token(data: dict) -> str:
    datos = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos.update({"exp": expira})
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise error
    except JWTError:
        raise error

    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email
    ).first()

    if usuario is None:
        raise error

    return usuario