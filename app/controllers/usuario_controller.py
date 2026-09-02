from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/usuario",
    tags=["Usuario"]
)

templates = Jinja2Templates(directory="app/views")


OBJETOS_DEMO = [
    {
        "id": 1,
        "nombre": "Archivador metalico",
        "descripcion": "Archivador en buen estado para carpetas y documentos.",
        "categoria": "oficina",
        "estado": "Disponible",
        "icono": "🗂️",
    },
    {
        "id": 2,
        "nombre": "Kit de marcadores",
        "descripcion": "Set de marcadores escolares con poco uso.",
        "categoria": "escolar",
        "estado": "Disponible",
        "icono": "🖍️",
    },
    {
        "id": 3,
        "nombre": "Teclado USB",
        "descripcion": "Teclado funcional para computador de escritorio.",
        "categoria": "tecnologia",
        "estado": "Reservado",
        "icono": "⌨️",
    },
]


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
def listar_objetos(request: Request):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/objetos.html",
        context=_contexto_usuario(request, objetos=OBJETOS_DEMO),
    )


@router.get("/publicar")
def mostrar_publicar(request: Request):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(request),
    )


@router.post("/publicar")
async def publicar_objeto(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    imagen: UploadFile | None = File(None),
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
            ),
            status_code=400,
        )

    nombre_archivo = imagen.filename if imagen and imagen.filename else "sin imagen"

    return templates.TemplateResponse(
        request=request,
        name="usuario/publicar.html",
        context=_contexto_usuario(
            request,
            mensaje=(
                f"Objeto '{nombre}' publicado correctamente. "
                f"Archivo recibido: {nombre_archivo}."
            ),
        ),
    )


@router.get("/mensajes")
def listar_mensajes(request: Request):
    respuesta = _redirigir_si_no_hay_sesion(request)

    if respuesta:
        return respuesta

    return templates.TemplateResponse(
        request=request,
        name="usuario/mensajes.html",
        context=_contexto_usuario(request, mensajes=[]),
    )
