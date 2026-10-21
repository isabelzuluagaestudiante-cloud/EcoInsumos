from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario import Usuario
from app.models.carrito import Carrito
from app.models.compra import Compra
from app.models.productos import Producto
from app.models.mensaje import Mensaje


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
    whatsapp: str = Form(...),
    db: Session = Depends(get_db),
):
    nombre = nombre.strip()
    email = email.strip().lower()
    password = password.strip()
    whatsapp = "".join(caracter for caracter in whatsapp.strip() if caracter.isdigit() or caracter == "+")

    if not nombre or not email or not password or not whatsapp:
        return _error_response(400, "Todos los campos son obligatorios.")

    if len(whatsapp.replace("+", "")) < 7 or len(whatsapp.replace("+", "")) > 15:
        return _error_response(400, "Ingresa un número de WhatsApp válido.")

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
        whatsapp=whatsapp,
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


@router.post("/cambiar-password")
def cambiar_password(
    request: Request,
    password_actual: str = Form(...),
    password_nueva: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.get(Usuario, request.session.get("usuario_id"))
    if not usuario:
        return _error_response(401, "Tu sesión ha terminado.")
    if usuario.password != password_actual:
        return _error_response(400, "La contraseña actual no es correcta.")
    if len(password_nueva.strip()) < 8:
        return _error_response(400, "La nueva contraseña debe tener al menos 8 caracteres.")
    usuario.password = password_nueva.strip()
    db.commit()
    return JSONResponse(content={"ok": True, "mensaje": "Contraseña actualizada correctamente."})


@router.post("/eliminar-cuenta")
def eliminar_cuenta(
    request: Request,
    password_actual: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario_id = request.session.get("usuario_id")
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        return _error_response(401, "Tu sesión ha terminado.")
    if usuario.password != password_actual:
        return _error_response(400, "La contraseña no es correcta.")

    db.query(Carrito).filter(Carrito.usuario_id == usuario_id).delete()
    db.query(Compra).filter(Compra.comprador_id == usuario_id).delete()
    db.query(Mensaje).filter(
        (Mensaje.remitente_id == usuario_id) | (Mensaje.destinatario_id == usuario_id)
    ).delete(synchronize_session=False)
    db.query(Producto).filter(Producto.vendedor_id == usuario_id).update({"vendedor_id": None})
    db.delete(usuario)
    db.commit()
    request.session.clear()
    return JSONResponse(content={"ok": True, "mensaje": "Cuenta eliminada correctamente.", "redirect_url": "/"})
