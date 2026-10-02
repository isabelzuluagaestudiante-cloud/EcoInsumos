from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
import os

from app.database.database import get_db
from app.models.carrito import Carrito
from app.models.categoria import Categoria
from app.models.mensaje import Mensaje
from app.models.productos import Producto
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/usuario",
    tags=["Usuario"]
)

APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = APP_DIR / "static" / "img" / "productos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_INTERCAMBIO_DIR = APP_DIR / "static" / "img" / "intercambios"
UPLOAD_INTERCAMBIO_DIR.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(APP_DIR / "views"))


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
    query = query.filter(Producto.estado == "Disponible")
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

    if producto.estado != "Disponible":
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="usuario/enviar_mensaje.html",
        context=_contexto_usuario(request, objeto=producto),
    )


@router.post("/mensaje/{producto_id}")
async def enviar_mensaje(
    request: Request,
    producto_id: int,
    contenido: str = Form(...),
    oferta_imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return RedirectResponse(url="/usuario/objetos", status_code=303)

    if producto.estado != "Disponible":
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

    tipo_solicitud = producto.tipo_publicacion if producto.tipo_publicacion in {"gratis", "intercambio"} else "mensaje"
    estado = "pendiente" if tipo_solicitud == "intercambio" else "enviado"
    oferta_imagen_url = None

    if tipo_solicitud == "intercambio" and oferta_imagen and oferta_imagen.filename:
        extension = Path(oferta_imagen.filename).suffix.lower() or ".jpg"
        nombre_guardado = f"intercambio_{producto_id}_{remitente_id}{extension}"
        ruta_guardado = UPLOAD_INTERCAMBIO_DIR / nombre_guardado

        contenido_imagen = await oferta_imagen.read()
        with open(ruta_guardado, "wb") as archivo:
            archivo.write(contenido_imagen)

        oferta_imagen_url = f"/static/img/intercambios/{nombre_guardado}"

    mensaje = Mensaje(
        contenido=texto,
        remitente_id=remitente_id,
        destinatario_id=producto.usuario_id,
        producto_id=producto.id,
        tipo_solicitud=tipo_solicitud,
        estado=estado,
        oferta_imagen_url=oferta_imagen_url,
    )
    db.add(mensaje)
    db.commit()

    return RedirectResponse(url="/usuario/mensajes", status_code=303)


@router.post("/mensaje/decision/{mensaje_id}")
def decidir_intercambio(
    request: Request,
    mensaje_id: int,
    decision: str = Form(...),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if not mensaje:
        return RedirectResponse(url="/usuario/mensajes", status_code=303)

    producto = mensaje.producto
    if not producto or producto.usuario_id != usuario_id:
        return RedirectResponse(url="/usuario/mensajes", status_code=303)

    decision = (decision or "").strip().lower()
    if mensaje.tipo_solicitud != "intercambio" or decision not in {"aceptado", "rechazado"}:
        return RedirectResponse(url="/usuario/mensajes", status_code=303)

    mensaje.estado = decision
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


@router.get("/configuracion")
def mostrar_configuracion(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/configuracion.html",
        context=_contexto_usuario(request),
    )


@router.post("/cambiar_contrasena")
def cambiar_contrasena(
    request: Request,
    nueva_contrasena: str = Form(...),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        return RedirectResponse(url="/usuario/configuracion", status_code=303)

    nueva_contrasena = nueva_contrasena.strip()
    if not nueva_contrasena:
        return templates.TemplateResponse(
            request=request,
            name="usuario/configuracion.html",
            context=_contexto_usuario(request, error="La nueva contraseña no puede estar vacía."),
            status_code=400,
        )

    usuario.contrasena = nueva_contrasena
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="usuario/configuracion.html",
        context=_contexto_usuario(request, mensaje="Contraseña cambiada exitosamente."),
    )


@router.post("/eliminar_cuenta")
def eliminar_cuenta(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    # Eliminar objetos relacionados (productos, mensajes, etc.)
    db.query(Producto).filter(Producto.usuario_id == usuario_id).delete()
    db.query(Mensaje).filter(
        (Mensaje.remitente_id == usuario_id) | (Mensaje.destinatario_id == usuario_id)
    ).delete()
    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()

    db.delete(usuario)
    db.commit()

    request.session.clear()  # Limpiar la sesión del usuario

    return RedirectResponse(url="/", status_code=303)


@router.post("/cerrar_sesion")
def cerrar_sesion(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/cambiar-password")
def mostrar_cambiar_password(request: Request):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/perfil.html",
        context=_contexto_usuario(request),
    )


@router.post("/cambiar-password")
def cambiar_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    usuario = db.query(Usuario).filter(Usuario.id == request.session.get("usuario_id")).first()
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    current_password = current_password.strip()
    new_password = new_password.strip()
    confirm_password = confirm_password.strip()

    if not current_password or not new_password or not confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="usuario/perfil.html",
            context=_contexto_usuario(request, error="Completa todos los campos para cambiar la contraseña."),
            status_code=400,
        )

    if usuario.password != current_password:
        return templates.TemplateResponse(
            request=request,
            name="usuario/perfil.html",
            context=_contexto_usuario(request, error="La contraseña actual no es correcta."),
            status_code=400,
        )

    if len(new_password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="usuario/perfil.html",
            context=_contexto_usuario(request, error="La nueva contraseña debe tener al menos 6 caracteres."),
            status_code=400,
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="usuario/perfil.html",
            context=_contexto_usuario(request, error="La nueva contraseña y la confirmación no coinciden."),
            status_code=400,
        )

    usuario.password = new_password
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="usuario/perfil.html",
        context=_contexto_usuario(request, success="Contraseña actualizada correctamente."),
    )


@router.post("/eliminar-cuenta")
def eliminar_cuenta(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)

    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()
    db.query(Mensaje).filter((Mensaje.remitente_id == usuario_id) | (Mensaje.destinatario_id == usuario_id)).delete()

    productos_usuario = db.query(Producto).filter(Producto.usuario_id == usuario_id).all()
    for producto in productos_usuario:
        producto.usuario_id = None

    db.delete(usuario)
    db.commit()
    request.session.clear()

    return RedirectResponse(url="/", status_code=303)


@router.post("/producto/eliminar/{producto_id}")
def eliminar_producto_propio(
    request: Request,
    producto_id: int,
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta

    usuario_id = request.session.get("usuario_id")
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto or producto.usuario_id != usuario_id:
        return RedirectResponse(url="/usuario", status_code=303)

    if producto.imagen_url:
        relative_path = producto.imagen_url.replace("/static/", "")
        ruta_imagen = APP_DIR / "static" / relative_path.replace("/", os.sep)
        if ruta_imagen.exists():
            ruta_imagen.unlink()

    db.query(Carrito).filter(Carrito.producto_id == producto.id).delete()
    db.query(Mensaje).filter(Mensaje.producto_id == producto.id).delete()
    db.delete(producto)
    db.commit()

    return RedirectResponse(url="/usuario", status_code=303)
