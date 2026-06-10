from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import obtener_usuario_actual

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.post("/", response_model=schemas.CategoriaRespuesta)
def crear_categoria(
    datos: schemas.CategoriaCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Crea una nueva categoría"""
    categoria = models.Categoria(nombre=datos.nombre)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("/", response_model=list[schemas.CategoriaRespuesta])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Lista todas las categorías"""
    return db.query(models.Categoria).all()


@router.delete("/{categoria_id}")
def borrar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    """Borra una categoría"""
    categoria = db.query(models.Categoria).filter(
        models.Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    db.delete(categoria)
    db.commit()
    return {"mensaje": "Categoría borrada"}