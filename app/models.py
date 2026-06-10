from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cuentas = relationship("Cuenta", back_populates="propietario")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    cuentas = relationship("Cuenta", back_populates="categoria")

class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    url = Column(String, nullable=True)
    usuario = Column(String, nullable=False)
    password_encriptado = Column(Text, nullable=False)
    notas = Column(Text, nullable=True)
    favorito = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_modificacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    categoria = relationship("Categoria", back_populates="cuentas")
    propietario = relationship("Usuario", back_populates="cuentas")

class Historial(Base):
    __tablename__ = "historial"

    id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    campo_modificado = Column(String, nullable=False)
    valor_anterior = Column(String, nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cuenta = relationship("Cuenta")