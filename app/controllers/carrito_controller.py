from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.database import SessionLocal
from app.models.carrito import Carrito
from app.models.productos import Producto

router = APIRouter(prefix="/carrito", tags=["carrito"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "views"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/agregar/{producto_id}")
def agregar_al_carrito(request: Request, producto_id: int, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    if producto.usuario_id == usuario_id:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    item = (
        db.query(Carrito)
        .filter(Carrito.usuario_id == usuario_id, Carrito.producto_id == producto_id)
        .first()
    )

    if item:
        item.cantidad += 1
    else:
        db.add(Carrito(usuario_id=usuario_id, producto_id=producto_id, cantidad=1))

    db.commit()
    return RedirectResponse(url="/carrito/", status_code=303)


@router.get("/")
def ver_carrito(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    items = (
        db.query(Carrito)
        .filter(Carrito.usuario_id == usuario_id)
        .all()
    )
    comprado = request.query_params.get("comprado") == "1"
    return templates.TemplateResponse(
        request=request,
        name="usuario/carrito.html",
        context={"request": request, "items": items, "comprado": comprado},
    )


@router.post("/eliminar/{item_id}")
def eliminar_del_carrito(request: Request, item_id: int, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    item = db.query(Carrito).filter(Carrito.id == item_id, Carrito.usuario_id == usuario_id).first()
    if item:
        db.delete(item)
        db.commit()

    return RedirectResponse(url="/carrito/", status_code=303)


@router.post("/comprar")
def comprar_carrito(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    items = db.query(Carrito).filter(Carrito.usuario_id == usuario_id).all()
    if not items:
        return RedirectResponse(url="/carrito/?comprado=0", status_code=303)

    for item in items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if producto:
            producto.estado = "Vendida"

    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()
    db.commit()
    return RedirectResponse(url="/carrito/?comprado=1", status_code=303)