from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
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


def obtener_items_de_precio(db: Session, usuario_id: int):
    items = (
        db.query(Carrito)
        .options(selectinload(Carrito.producto))
        .filter(Carrito.usuario_id == usuario_id)
        .all()
    )
    valid_items = []
    subtotal = 0

    for item in items:
        producto = item.producto
        if not producto or producto.tipo_publicacion != "precio" or (producto.precio or 0) <= 0:
            continue
        subtotal += (producto.precio or 0) * item.cantidad
        valid_items.append(item)

    impuestos = round(subtotal * 0.10)
    total_pedido = round(subtotal * 1.10)
    return valid_items, subtotal, impuestos, total_pedido


@router.post("/agregar/{producto_id}")
def agregar_al_carrito(request: Request, producto_id: int, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto or producto.estado != "Disponible":
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    if producto.usuario_id == usuario_id:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    if producto.tipo_publicacion in {"gratis", "intercambio"}:
        return RedirectResponse(url=f"/usuario/mensaje/{producto.id}", status_code=303)

    if producto.tipo_publicacion != "precio" or (producto.precio or 0) <= 0:
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

    items, subtotal, impuestos, total_pedido = obtener_items_de_precio(db, usuario_id)
    tipo_entrega = request.session.get("tipo_entrega") or "domicilio"
    comprado = request.query_params.get("comprado") == "1"
    return templates.TemplateResponse(
        request=request,
        name="usuario/carrito.html",
        context={
            "request": request,
            "items": items,
            "subtotal": subtotal,
            "impuestos": impuestos,
            "total_pedido": total_pedido,
            "comprado": comprado,
            "tipo_entrega": tipo_entrega,
        },
    )


@router.post("/pago")
def preparar_pago(request: Request, tipo_entrega: str = Form(...), db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    tipo_entrega = (tipo_entrega or "domicilio").strip().lower()
    if tipo_entrega not in {"domicilio", "recogida"}:
        tipo_entrega = "domicilio"

    request.session["tipo_entrega"] = tipo_entrega
    items, subtotal, impuestos, total_pedido = obtener_items_de_precio(db, usuario_id)
    if not items:
        return RedirectResponse(url="/carrito/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="usuario/pago.html",
        context={
            "request": request,
            "items": items,
            "subtotal": subtotal,
            "impuestos": impuestos,
            "total_pedido": total_pedido,
            "tipo_entrega": tipo_entrega,
            "metodo_pago": request.session.get("metodo_pago") or "tarjeta",
        },
    )


@router.post("/confirmar-pago")
def confirmar_pago(
    request: Request,
    metodo_pago: str = Form(...),
    nombre_titular: str = Form(""),
    numero_tarjeta: str = Form(""),
    fecha_vencimiento: str = Form(""),
    cvv: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    metodo_pago = (metodo_pago or "tarjeta").strip().lower()
    if metodo_pago not in {"tarjeta", "transferencia", "efectivo"}:
        return RedirectResponse(url="/carrito/", status_code=303)

    request.session["metodo_pago"] = metodo_pago
    tipo_entrega = request.session.get("tipo_entrega") or "domicilio"
    items, subtotal, impuestos, total_pedido = obtener_items_de_precio(db, usuario_id)

    if not items:
        return RedirectResponse(url="/carrito/", status_code=303)

    if metodo_pago == "tarjeta":
        if not nombre_titular or not numero_tarjeta or not fecha_vencimiento or not cvv:
            return templates.TemplateResponse(
                request=request,
                name="usuario/pago.html",
                context={
                    "request": request,
                    "items": items,
                    "subtotal": subtotal,
                    "impuestos": impuestos,
                    "total_pedido": total_pedido,
                    "tipo_entrega": tipo_entrega,
                    "metodo_pago": metodo_pago,
                    "error": "Completa todos los datos de la tarjeta para continuar.",
                },
            )

    for item in items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if producto:
            producto.estado = "Vendida"

    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()
    db.commit()
    return RedirectResponse(url="/carrito/?comprado=1", status_code=303)


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

    items, subtotal, impuestos, total_pedido = obtener_items_de_precio(db, usuario_id)
    if not items:
        return RedirectResponse(url="/carrito/?comprado=0", status_code=303)

    request.session["metodo_pago"] = request.session.get("metodo_pago") or "tarjeta"
    for item in items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if producto:
            producto.estado = "Vendida"

    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()
    db.commit()
    return RedirectResponse(url="/carrito/?comprado=1", status_code=303)