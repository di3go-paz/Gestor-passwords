from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.routers import auth, cuentas, categorias
from app.auth import obtener_usuario_actual
import secrets
import string

# Crea todas las tablas en la base de datos al arrancar
# Si ya existen, no hace nada
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor de Contraseñas",
    description="API segura para gestionar tus credenciales",
    version="1.0.0"
)

# Conecta todos los routers
app.include_router(auth.router)
app.include_router(cuentas.router)
app.include_router(categorias.router)


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "Gestor de contraseñas activo"}


@app.get("/generar-password", tags=["General"])
def generar_password(
    largo: int = 16,
    simbolos: bool = True,
    numeros: bool = True,
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Genera una contraseña segura aleatoria"""

    # Siempre incluye letras
    caracteres = string.ascii_letters

    if numeros:
        caracteres += string.digits

    if simbolos:
        caracteres += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Genera la contraseña
    password = "".join(secrets.choice(caracteres) for _ in range(largo))

    # Calcula su fortaleza
    fortaleza = calcular_fortaleza(password)

    return {
        "password": password,
        "largo": largo,
        "fortaleza": fortaleza
    }


@app.get("/verificar-fortaleza", tags=["General"])
def verificar_fortaleza(
    password: str,
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Verifica qué tan segura es una contraseña"""
    return {
        "password": password,
        "fortaleza": calcular_fortaleza(password),
        "detalles": obtener_detalles_fortaleza(password)
    }


def calcular_fortaleza(password: str) -> str:
    puntaje = 0

    if len(password) >= 8:
        puntaje += 1
    if len(password) >= 12:
        puntaje += 1
    if len(password) >= 16:
        puntaje += 1
    if any(c.islower() for c in password):
        puntaje += 1
    if any(c.isupper() for c in password):
        puntaje += 1
    if any(c.isdigit() for c in password):
        puntaje += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        puntaje += 1

    if puntaje <= 2:
        return "Muy débil"
    elif puntaje <= 3:
        return "Débil"
    elif puntaje <= 5:
        return "Media"
    elif puntaje == 6:
        return "Fuerte"
    else:
        return "Muy fuerte"


def obtener_detalles_fortaleza(password: str) -> dict:
    return {
        "largo_suficiente": len(password) >= 8,
        "tiene_minusculas": any(c.islower() for c in password),
        "tiene_mayusculas": any(c.isupper() for c in password),
        "tiene_numeros": any(c.isdigit() for c in password),
        "tiene_simbolos": any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ),
        "largo": len(password)
    }