from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.categoria import Categoria
from app.models.mensaje import Mensaje
from app.models.productos import Producto


router = APIRouter(
    prefix="/usuario",
    tags=["Usuario"]
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "app" / "static" / "img" / "productos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(BASE_DIR / "views"))


def _usuario_autenticado(request: Request) -> bool:
    return bool(request.session.get("usuario_id"))


def _redirigir_si_no_hay_sesion(request: Request) -> RedirectResponse | None:
    if not _usuario_autenticado(request):
        return RedirectResponse(url="/", status_code=303)

    return None


def _contexto_usuario(request: Request, **extra):
    contexto = {
        "request": request,
        "nombre": request.session.get("nombre", "Usuario"),
        "usuario_actual_id": request.session.get("usuario_id"),
    }
    contexto.update(extra)
    return contexto


@router.get("")
def inicio_usuario(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    mis_objetos = (
        db.query(Producto)
        .filter(Producto.usuario_id == usuario_id)
        .order_by(Producto.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="usuario/inicio.html",
        context=_contexto_usuario(request, mis_objetos=mis_objetos),
    )


@router.get("/inicio")
def inicio_usuario_alias(request: Request, db: Session = Depends(get_db)):
    return inicio_usuario(request, db)


@router.get("/objetos")
def listar_objetos(request: Request, db: Session = Depends(get_db), categoria_id: int | None = None):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    categorias = db.query(Categoria).order_by(Categoria.nombre).all()

    query = db.query(Producto)
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == categoria_id)

    objetos = (
        query
        .filter((Producto.usuario_id != usuario_id) | (Producto.usuario_id.is_(None)))
        .order_by(Producto.id.desc())
        .all()
    )

    mis_objetos = (
        db.query(Producto)
        .filter(Producto.usuario_id == usuario_id)
        .order_by(Producto.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="usuario/objetos.html",
        context=_contexto_usuario(
            request,
            objetos=objetos,
            mis_objetos=mis_objetos,
            categorias=categorias,
            categoria_id_seleccionada=categoria_id,
        ),
    )


@router.get("/publicar")
def mostrar_publicar(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    categorias = db.query(Categoria).order_by(Categoria.nombre).all()

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(request, categorias=categorias),
    )


@router.post("/publicar")
async def publicar_objeto(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: int = Form(0),
    categoria_id: int = Form(...),
    tipo_publicacion: str = Form("precio"),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    nombre = nombre.strip()
    descripcion = descripcion.strip()
    tipo_publicacion = (tipo_publicacion or "precio").strip().lower()

    if tipo_publicacion not in {"precio", "intercambio", "gratis"}:
        tipo_publicacion = "precio"

    if not nombre or not descripcion:
        categorias = db.query(Categoria).order_by(Categoria.nombre).all()
        return templates.TemplateResponse(
            request=request,
            name="usuario/publicar.html",
            context=_contexto_usuario(
                request,
                error="Debes completar el nombre y la descripcion del objeto.",
                categorias=categorias,
            ),
            status_code=400,
        )

    if tipo_publicacion == "precio":
        if precio is None or precio <= 0:
            categorias = db.query(Categoria).order_by(Categoria.nombre).all()
            return templates.TemplateResponse(
                request=request,
                name="usuario/publicar.html",
                context=_contexto_usuario(
                    request,
                    error="Si eliges precio, debes ingresar un valor mayor a cero.",
                    categorias=categorias,
                ),
                status_code=400,
            )
    else:
        precio = 0

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        categorias = db.query(Categoria).order_by(Categoria.nombre).all()
        return templates.TemplateResponse(
            request=request,
            name="usuario/publicar.html",
            context=_contexto_usuario(
                request,
                error="Debes seleccionar una categoría válida.",
                categorias=categorias,
            ),
            status_code=400,
        )

    usuario_id = request.session.get("usuario_id")
    nombre_archivo = imagen.filename if imagen and imagen.filename else "sin imagen"

    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        tipo_publicacion=tipo_publicacion,
        categoria_id=categoria.id,
        usuario_id=usuario_id,
        estado="Disponible",
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    if imagen and imagen.filename:
        extension = Path(imagen.filename).suffix.lower() or ".jpg"
        nombre_guardado = f"producto_{nuevo_producto.id}{extension}"
        ruta_guardado = UPLOAD_DIR / nombre_guardado

        contenido = await imagen.read()
        with open(ruta_guardado, "wb") as archivo:
            archivo.write(contenido)

        nuevo_producto.imagen_url = f"/static/img/productos/{nombre_guardado}"
        db.commit()

    categorias = db.query(Categoria).order_by(Categoria.nombre).all()

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(
            request,
            mensaje=(
                f"Objeto '{nombre}' publicado correctamente. "
                f"Archivo recibido: {nombre_archivo}."
            ),
            categorias=categorias,
        ),
    )


@router.get("/mensaje/{producto_id}")
def mostrar_formulario_mensaje(request: Request, producto_id: int, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    if producto.usuario_id == request.session.get("usuario_id"):
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="usuario/enviar_mensaje.html",
        context=_contexto_usuario(request, objeto=producto),
    )


@router.post("/mensaje/{producto_id}")
def enviar_mensaje(
    request: Request,
    producto_id: int,
    contenido: str = Form(...),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    remitente_id = request.session.get("usuario_id")
    if not remitente_id or producto.usuario_id == remitente_id:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    texto = contenido.strip()
    if not texto:
        return templates.TemplateResponse(
            request=request,
            name="usuario/enviar_mensaje.html",
            context=_contexto_usuario(request, objeto=producto, error="Escribe un mensaje antes de enviar."),
            status_code=400,
        )

    mensaje = Mensaje(
        contenido=texto,
        remitente_id=remitente_id,
        destinatario_id=producto.usuario_id,
        producto_id=producto.id,
    )
    db.add(mensaje)
    db.commit()

    return RedirectResponse(url="/usuario/mensajes", status_code=303)


@router.get("/mensajes")
def listar_mensajes(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    mensajes = (
        db.query(Mensaje)
        .filter((Mensaje.remitente_id == usuario_id) | (Mensaje.destinatario_id == usuario_id))
        .order_by(Mensaje.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="usuario/mensajes.html",
        context=_contexto_usuario(request, mensajes=mensajes),
    )
