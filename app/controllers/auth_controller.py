from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

templates = Jinja2Templates(
    directory="app/views"
)


# =========================
# MOSTRAR REGISTRO
# =========================

@router.get("/registro", response_class=HTMLResponse)
def mostrar_registro(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="auth/registro.html",
        context={
            "request": request
        }
    )


# =========================
# REGISTRAR USUARIO
# =========================

@router.post("/registro", response_class=HTMLResponse)
def registrar_usuario(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    nombre = nombre.strip()
    email = email.strip().lower()

    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    if usuario_existente:

        return templates.TemplateResponse(
            request=request,
            name="auth/registro.html",
            context={
                "request": request,
                "error": "El correo electrónico ya está registrado."
            },
            status_code=400
        )

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password=password,
        rol="usuario",
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return templates.TemplateResponse(
        request=request,
        name="auth/registro.html",
        context={
            "request": request,
            "mensaje": "Usuario registrado correctamente."
        }
    )


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    # Usuario no encontrado
    if not usuario:

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Contraseña incorrecta
    if usuario.password != password:

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Usuario inactivo
    if not usuario.activo:

        raise HTTPException(
            status_code=403,
            detail="El usuario está inactivo"
        )

    # =========================
    # REDIRECCIÓN POR ROL
    # =========================

    if usuario.rol == "admin":

        return RedirectResponse(
            url="/admin/inicio",
            status_code=303
        )

    else:

        return RedirectResponse(
            url="/usuario/inicio",
            status_code=303
        )