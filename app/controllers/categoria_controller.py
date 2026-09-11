from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.database import SessionLocal
from app.models.categoria import Categoria
from app.models.productos import Producto

router = APIRouter(prefix="/categorias", tags=["categorias"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "views"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
@router.get("/")
def listar_categorias(request: Request, categoria_id: int | None = None, db: Session = Depends(get_db)):
    categorias = db.query(Categoria).order_by(Categoria.nombre).all()
    usuario_id = request.session.get("usuario_id")

    if categoria_id is not None:
        productos = (
            db.query(Producto)
            .filter(Producto.categoria_id == categoria_id)
        )
        if usuario_id:
            productos = productos.filter((Producto.usuario_id != usuario_id) | (Producto.usuario_id.is_(None)))
        productos = productos.order_by(Producto.id.desc()).all()
        categoria_seleccionada = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    else:
        productos = []
        categoria_seleccionada = None

    return templates.TemplateResponse(
        request=request,
        name="usuario/categorias.html",
        context={
            "request": request,
            "categorias": categorias,
            "categoria_seleccionada": categoria_seleccionada,
            "productos": productos,
            "usuario_actual_id": usuario_id,
        },
    )