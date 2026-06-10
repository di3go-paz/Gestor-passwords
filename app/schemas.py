from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# usuarios

class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str

class UsuarioRespuesta(BaseModel):
    id: int
    email: str
    fecha_creacion: datetime

    model_config = {"from_attributes": True}

# login

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# categoria

class CategoriaCrear(BaseModel):
    nombre: str

class CategoriaRespuesta(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}

# cuenta

class CuentaCrear(BaseModel):
    nombre: str
    url: Optional[str] = None
    usuario: str
    password: str
    notas: Optional[str] = None
    favorito: bool = False
    categoria_id: Optional[int] = None

class CuentaEditar(BaseModel):
    nombre: Optional[str] = None
    url: Optional[str] = None
    usuario: Optional[str] = None
    password: Optional[str] = None
    notas: Optional[str] = None
    favorito: Optional[bool] = None
    categoria_id: Optional[int] = None

class CuentaRespuesta(BaseModel):
    id: int
    nombre: str
    url: Optional[str]
    usuario: str
    notas: Optional[str]
    favorito: bool
    categoria_id: Optional[int]
    fecha_creacion: datetime
    fecha_modificacion: datetime

    model_config = {"from_attributes": True}

# historial

class HistorialRespuesta(BaseModel):
    id: int
    cuenta_id: int
    campo_modificado: str
    valor_anterior: Optional[str]
    fecha: datetime

    model_config = {"from_attributes": True}
