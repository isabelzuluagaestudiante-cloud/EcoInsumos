from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.carrito import Carrito
from app.models.compra import Compra
from app.models.productos import Producto

router = APIRouter(prefix="/carrito", tags=["carrito"])
templates = Jinja2Templates(directory="app/views")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def ver_carrito(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)
    items = db.query(Carrito).filter(Carrito.usuario_id == usuario_id).all()
    cantidad_carrito = sum(item.cantidad for item in items)
    return templates.TemplateResponse(
        "usuario/carrito.html",
        {
            "request": request,
            "items": items,
            "cantidad_carrito": cantidad_carrito,
            "nombre": request.session.get("nombre", "Usuario"),
        },
    )


@router.get("/contador")
def obtener_contador_carrito(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return {"cantidad": 0}
    cantidad = sum(item.cantidad for item in db.query(Carrito).filter(Carrito.usuario_id == usuario_id).all())
    return {"cantidad": cantidad}


@router.post("/agregar/{producto_id}")
def agregar_al_carrito(producto_id: int, request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión para agregar productos.")
    producto = db.get(Producto, producto_id)
    if not producto or not producto.disponible:
        raise HTTPException(status_code=404, detail="Producto no disponible.")
    if producto.es_intercambio:
        raise HTTPException(status_code=400, detail="Este objeto se ofrece únicamente para intercambio. Contacta al publicador.")
    if producto.vendedor_id == usuario_id:
        raise HTTPException(status_code=400, detail="No puedes agregar tu propio producto.")
    item = db.query(Carrito).filter(Carrito.usuario_id == usuario_id, Carrito.producto_id == producto_id).first()
    if item:
        return {"ok": True, "mensaje": "El producto ya está en tu carrito."}
    db.add(Carrito(usuario_id=usuario_id, producto_id=producto_id, cantidad=1))
    db.commit()
    return {"ok": True, "mensaje": "Producto agregado al carrito."}


@router.post("/quitar/{producto_id}")
def quitar_del_carrito(producto_id: int, request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión.")
    eliminado = db.query(Carrito).filter(
        Carrito.usuario_id == usuario_id, Carrito.producto_id == producto_id
    ).delete()
    db.commit()
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito.")
    return {"ok": True, "mensaje": "Producto eliminado del carrito."}


@router.post("/comprar/{producto_id}")
def comprar_producto(producto_id: int, request: Request, db: Session = Depends(get_db)):
    comprador_id = request.session.get("usuario_id")
    if not comprador_id:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión para comprar.")
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    if not producto.vendedor_id:
        raise HTTPException(status_code=400, detail="Este producto aún no tiene vendedor asignado.")
    if producto.vendedor_id == comprador_id:
        raise HTTPException(status_code=400, detail="No puedes comprar tu propio producto.")
    if not producto.disponible:
        raise HTTPException(status_code=400, detail="Este producto ya no está disponible.")
    db.add(Compra(comprador_id=comprador_id, producto_id=producto.id))
    producto.disponible = False
    db.query(Carrito).filter(Carrito.producto_id == producto.id).delete()
    db.commit()
    return {"ok": True, "mensaje": "Compra registrada. El vendedor recibirá tu WhatsApp para coordinar el domicilio."}


@router.get("/ventas")
def ver_ventas(request: Request, db: Session = Depends(get_db)):
    vendedor_id = request.session.get("usuario_id")
    if not vendedor_id:
        return RedirectResponse(url="/", status_code=303)
    ventas = (db.query(Compra).join(Producto).filter(Producto.vendedor_id == vendedor_id)
              .order_by(Compra.creada_en.desc()).all())
    compras_realizadas = (db.query(Compra).filter(Compra.comprador_id == vendedor_id)
                         .order_by(Compra.creada_en.desc()).all())
    return templates.TemplateResponse("usuario/ventas.html", {
        "request": request, "ventas": ventas, "compras_realizadas": compras_realizadas,
        "nombre": request.session.get("nombre", "Usuario")})
