from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app import models, schemas
from app.auth import obtener_usuario_actual, encriptar, desencriptar

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


@router.post("/", response_model=schemas.CuentaRespuesta)
def crear_cuenta(
    datos: schemas.CuentaCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Crea una nueva cuenta guardada"""
    nueva_cuenta = models.Cuenta(
        nombre=datos.nombre,
        url=datos.url,
        usuario=datos.usuario,
        password_encriptado=encriptar(datos.password),
        notas=datos.notas,
        favorito=datos.favorito,
        categoria_id=datos.categoria_id,
        usuario_id=usuario_actual.id
    )
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)
    return nueva_cuenta


@router.get("/", response_model=list[schemas.CuentaRespuesta])
def listar_cuentas(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Lista todas las cuentas del usuario"""
    return db.query(models.Cuenta).filter(
        models.Cuenta.usuario_id == usuario_actual.id
    ).all()


@router.get("/favoritos", response_model=list[schemas.CuentaRespuesta])
def listar_favoritos(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Lista solo las cuentas marcadas como favoritas"""
    return db.query(models.Cuenta).filter(
        models.Cuenta.usuario_id == usuario_actual.id,
        models.Cuenta.favorito == True
    ).all()


@router.get("/buscar", response_model=list[schemas.CuentaRespuesta])
def buscar_cuentas(
    q: str,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Busca cuentas por nombre"""
    return db.query(models.Cuenta).filter(
        models.Cuenta.usuario_id == usuario_actual.id,
        models.Cuenta.nombre.ilike(f"%{q}%")
    ).all()


@router.get("/{cuenta_id}", response_model=schemas.CuentaRespuesta)
def obtener_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Obtiene una cuenta específica"""
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == cuenta_id,
        models.Cuenta.usuario_id == usuario_actual.id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return cuenta


@router.get("/{cuenta_id}/password")
def obtener_password(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Desencripta y devuelve la contraseña de una cuenta"""
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == cuenta_id,
        models.Cuenta.usuario_id == usuario_actual.id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return {"password": desencriptar(cuenta.password_encriptado)}


@router.put("/{cuenta_id}", response_model=schemas.CuentaRespuesta)
def editar_cuenta(
    cuenta_id: int,
    datos: schemas.CuentaEditar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Edita una cuenta — solo los campos que mandes"""
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == cuenta_id,
        models.Cuenta.usuario_id == usuario_actual.id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    # Guarda en historial cada campo que cambie
    campos = datos.model_dump(exclude_unset=True)
    for campo, valor_nuevo in campos.items():
        if campo == "password":
            valor_anterior = desencriptar(cuenta.password_encriptado)
            historial = models.Historial(
                cuenta_id=cuenta.id,
                campo_modificado="password",
                valor_anterior="[protegido]"
            )
        else:
            valor_anterior = getattr(cuenta, campo)
            historial = models.Historial(
                cuenta_id=cuenta.id,
                campo_modificado=campo,
                valor_anterior=str(valor_anterior)
            )
        db.add(historial)

    # Aplica los cambios
    for campo, valor in campos.items():
        if campo == "password":
            cuenta.password_encriptado = encriptar(valor)
        else:
            setattr(cuenta, campo, valor)

    cuenta.fecha_modificacion = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.delete("/{cuenta_id}")
def borrar_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Borra una cuenta"""
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == cuenta_id,
        models.Cuenta.usuario_id == usuario_actual.id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    db.delete(cuenta)
    db.commit()
    return {"mensaje": "Cuenta borrada"}


@router.get("/{cuenta_id}/historial",
            response_model=list[schemas.HistorialRespuesta])
def ver_historial(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Ver el historial de cambios de una cuenta"""
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.id == cuenta_id,
        models.Cuenta.usuario_id == usuario_actual.id
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return db.query(models.Historial).filter(
        models.Historial.cuenta_id == cuenta_id
    ).all()