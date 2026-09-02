from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/auth",
    tags=["Autenticacion"]
)


def _error_response(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "mensaje": mensaje,
            "detail": mensaje,
        },
    )


@router.post("/registro")
def registrar_usuario(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    nombre = nombre.strip()
    email = email.strip().lower()
    password = password.strip()

    if not nombre or not email or not password:
        return _error_response(400, "Todos los campos son obligatorios.")

    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    if usuario_existente:
        return _error_response(400, "El correo electronico ya esta registrado.")

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password=password,
        rol="usuario",
        activo=True,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return JSONResponse(
        content={
            "ok": True,
            "mensaje": "Usuario registrado correctamente.",
            "usuario": nuevo_usuario.nombre,
            "rol": nuevo_usuario.rol,
        }
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    password = password.strip()

    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    if not usuario or usuario.password != password:
        return _error_response(401, "Correo o contrasena incorrectos.")

    if not usuario.activo:
        return _error_response(403, "El usuario esta inactivo.")

    request.session.clear()
    request.session["usuario_id"] = usuario.id
    request.session["nombre"] = usuario.nombre
    request.session["rol"] = usuario.rol

    return JSONResponse(
        content={
            "ok": True,
            "mensaje": "Inicio de sesion correcto.",
            "usuario": usuario.nombre,
            "rol": usuario.rol,
            "redirect_url": "/admin" if usuario.rol == "admin" else "/usuario",
        }
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(url="/", status_code=303)
