from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.categoria import Categoria
from app.models.mensaje import Mensaje
from app.models.intercambio import SolicitudIntercambio
from app.models.productos import Producto


router = APIRouter(
    prefix="/usuario",
    tags=["Usuario"]
)

templates = Jinja2Templates(directory="app/views")


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
    }
    contexto.update(extra)
    return contexto


@router.get("")
def inicio_usuario(request: Request):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/inicio.html",
        context=_contexto_usuario(request),
    )


@router.get("/inicio")
def inicio_usuario_alias(request: Request):
    return inicio_usuario(request)


@router.get("/objetos")
def listar_objetos(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/objetos.html",
        context=_contexto_usuario(
            request,
            objetos=db.query(Producto).filter(Producto.disponible.is_(True)).order_by(Producto.id.desc()).all(),
        ),
    )


@router.get("/publicar")
def mostrar_publicar(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(request, categorias=db.query(Categoria).order_by(Categoria.nombre).all()),
    )


@router.post("/publicar")
async def publicar_objeto(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: int | None = Form(None),
    modalidad: str = Form("venta"),
    categoria_id: int = Form(...),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    nombre = nombre.strip()
    descripcion = descripcion.strip()

    if not nombre or not descripcion:
        return templates.TemplateResponse(
            request=request,
            name="usuario/publicar.html",
            context=_contexto_usuario(
                request,
                error="Debes completar el nombre y la descripcion del objeto.",
                categorias=db.query(Categoria).order_by(Categoria.nombre).all(),
            ),
            status_code=400,
        )

    categoria = db.get(Categoria, categoria_id)
    es_intercambio = modalidad == "intercambio"
    if modalidad not in {"venta", "intercambio"} or not categoria or (not es_intercambio and (precio is None or precio < 0)):
        return templates.TemplateResponse(
            request=request, name="usuario/publicar.html",
            context=_contexto_usuario(request, error="Selecciona una categoría y un precio válido para la venta.", categorias=db.query(Categoria).all()),
            status_code=400,
        )

    nombre_archivo = None
    if imagen and imagen.filename:
        extension = Path(imagen.filename).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            return templates.TemplateResponse(
                request=request, name="usuario/publicar.html",
                context=_contexto_usuario(request, error="La imagen debe ser JPG, PNG o WEBP.", categorias=db.query(Categoria).all()),
                status_code=400,
            )
        carpeta = Path("app/static/uploads")
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = f"{uuid4().hex}{extension}"
        (carpeta / nombre_archivo).write_bytes(await imagen.read())

    producto = Producto(
        nombre=nombre, descripcion=descripcion, precio=0 if es_intercambio else precio,
        es_intercambio=es_intercambio, categoria_id=categoria.id,
        vendedor_id=request.session["usuario_id"], imagen=nombre_archivo, disponible=True,
    )
    db.add(producto)
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(
            request,
            mensaje=(
                f"Objeto '{nombre}' publicado correctamente."
            ),
            categorias=db.query(Categoria).order_by(Categoria.nombre).all(),
        ),
    )


@router.get("/objetos/{producto_id}")
def detalle_objeto(producto_id: int, request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Objeto no encontrado.")
    return templates.TemplateResponse(request=request, name="usuario/detalle_objeto.html", context=_contexto_usuario(request, objeto=producto))


@router.get("/intercambio/{producto_id}")
def mostrar_propuesta_intercambio(producto_id: int, request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    producto = db.get(Producto, producto_id)
    if not producto or not producto.disponible or not producto.es_intercambio:
        raise HTTPException(status_code=404, detail="Este objeto no está disponible para intercambio.")
    if producto.vendedor_id == request.session["usuario_id"]:
        raise HTTPException(status_code=400, detail="No puedes proponer un intercambio por tu propio objeto.")
    objetos_propios = db.query(Producto).filter(
        Producto.vendedor_id == request.session["usuario_id"], Producto.disponible.is_(True)
    ).order_by(Producto.nombre).all()
    return templates.TemplateResponse(request=request, name="usuario/proponer_intercambio.html", context=_contexto_usuario(
        request, objeto=producto, objetos_propios=objetos_propios
    ))


@router.post("/intercambio/{producto_id}")
def crear_propuesta_intercambio(
    producto_id: int, request: Request, producto_ofrecido_id: int = Form(...), mensaje: str = Form(""), db: Session = Depends(get_db)
):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    solicitante_id = request.session["usuario_id"]
    solicitado = db.get(Producto, producto_id)
    ofrecido = db.get(Producto, producto_ofrecido_id)
    if not solicitado or not solicitado.disponible or not solicitado.es_intercambio:
        raise HTTPException(status_code=404, detail="El objeto solicitado ya no está disponible para intercambio.")
    if not ofrecido or not ofrecido.disponible or ofrecido.vendedor_id != solicitante_id or ofrecido.id == solicitado.id:
        raise HTTPException(status_code=400, detail="Selecciona uno de tus objetos disponibles para ofrecer.")
    repetida = db.query(SolicitudIntercambio).filter(
        SolicitudIntercambio.solicitante_id == solicitante_id,
        SolicitudIntercambio.producto_solicitado_id == solicitado.id,
        SolicitudIntercambio.producto_ofrecido_id == ofrecido.id,
        SolicitudIntercambio.estado == "pendiente",
    ).first()
    if not repetida:
        db.add(SolicitudIntercambio(
            solicitante_id=solicitante_id, producto_solicitado_id=solicitado.id,
            producto_ofrecido_id=ofrecido.id, mensaje=mensaje.strip() or None,
        ))
        db.commit()
    return RedirectResponse(url="/usuario/intercambios", status_code=303)


@router.get("/intercambios")
def listar_intercambios(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    usuario_id = request.session["usuario_id"]
    solicitudes = db.query(SolicitudIntercambio).join(
        Producto, SolicitudIntercambio.producto_solicitado_id == Producto.id
    ).filter(
        (SolicitudIntercambio.solicitante_id == usuario_id) | (Producto.vendedor_id == usuario_id)
    ).order_by(SolicitudIntercambio.creada_en.desc()).all()
    return templates.TemplateResponse(request=request, name="usuario/intercambios.html", context=_contexto_usuario(
        request, solicitudes=solicitudes, usuario_id=usuario_id
    ))


@router.post("/intercambios/{solicitud_id}/{accion}")
def responder_intercambio(solicitud_id: int, accion: str, request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    solicitud = db.get(SolicitudIntercambio, solicitud_id)
    if not solicitud or solicitud.producto_solicitado.vendedor_id != request.session["usuario_id"]:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if solicitud.estado != "pendiente" or accion not in {"aceptar", "rechazar"}:
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue gestionada.")
    if accion == "aceptar":
        if not solicitud.producto_solicitado.disponible or not solicitud.producto_ofrecido.disponible:
            raise HTTPException(status_code=400, detail="Uno de los objetos ya no está disponible.")
        solicitud.producto_solicitado.disponible = False
        solicitud.producto_ofrecido.disponible = False
        solicitud.estado = "aceptada"
        for otra in db.query(SolicitudIntercambio).filter(SolicitudIntercambio.estado == "pendiente").all():
            usa_objeto_intercambiado = (
                otra.producto_solicitado_id in {solicitud.producto_solicitado_id, solicitud.producto_ofrecido_id}
                or otra.producto_ofrecido_id in {solicitud.producto_solicitado_id, solicitud.producto_ofrecido_id}
            )
            if otra.id != solicitud.id and usa_objeto_intercambiado:
                otra.estado = "rechazada"
    else:
        solicitud.estado = "rechazada"
    db.commit()
    return RedirectResponse(url="/usuario/intercambios", status_code=303)


@router.get("/mensaje/{producto_id}")
def mostrar_mensaje(producto_id: int, request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Objeto no encontrado.")
    return templates.TemplateResponse(request=request, name="usuario/enviar_mensaje.html", context=_contexto_usuario(request, objeto=producto))


@router.post("/mensaje/{producto_id}")
def enviar_mensaje(producto_id: int, request: Request, contenido: str = Form(...), db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)
    if respuesta:
        return respuesta
    producto = db.get(Producto, producto_id)
    if not producto or not producto.vendedor_id:
        raise HTTPException(status_code=404, detail="Objeto no encontrado.")
    if producto.vendedor_id == request.session["usuario_id"]:
        raise HTTPException(status_code=400, detail="No puedes enviarte mensajes a ti mismo.")
    contenido = contenido.strip()
    if not contenido:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")
    db.add(Mensaje(remitente_id=request.session["usuario_id"], destinatario_id=producto.vendedor_id, producto_id=producto.id, contenido=contenido))
    db.commit()
    return RedirectResponse(url="/usuario/mensajes", status_code=303)


@router.get("/mensajes")
def listar_mensajes(request: Request, db: Session = Depends(get_db)):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/mensajes.html",
        context=_contexto_usuario(
            request,
            mensajes=db.query(Mensaje).filter(
                (Mensaje.remitente_id == request.session["usuario_id"]) |
                (Mensaje.destinatario_id == request.session["usuario_id"])
            ).order_by(Mensaje.creado_en.desc()).all(),
        ),
    )
