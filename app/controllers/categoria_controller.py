from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.categoria import Categoria
from app.models.productos import Producto

router = APIRouter(prefix="/categorias", tags=["categorias"])
templates = Jinja2Templates(directory="app/views")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_categorias(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("usuario_id"):
        return RedirectResponse(url="/", status_code=303)
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse(
        "usuario/categorias.html",
        {"request": request, "categorias": categorias, "nombre": request.session.get("nombre", "Usuario")},
    )


@router.get("/{categoria_id}")
def productos_categoria(categoria_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("usuario_id"):
        return RedirectResponse(url="/", status_code=303)
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        return RedirectResponse(url="/categorias/", status_code=303)
    productos = db.query(Producto).filter(
        Producto.categoria_id == categoria_id, Producto.disponible.is_(True)
    ).order_by(Producto.id.desc()).all()
    return templates.TemplateResponse("usuario/objetos.html", {
        "request": request, "nombre": request.session.get("nombre", "Usuario"),
        "objetos": productos, "categoria_actual": categoria,
    })
