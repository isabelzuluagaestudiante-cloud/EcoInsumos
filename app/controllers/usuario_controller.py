from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/usuario",
    tags=["Usuario"]
)


# ==========================================
# REGISTRO DE USUARIO
# ==========================================

@router.post("/registro")
def registrar_usuario(
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Limpiar información
    nombre = nombre.strip()
    email = email.strip().lower()

    # Verificar correo existente
    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado."
        )

    # Crear usuario
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

    # Después de registrarse va directamente
    # a la vista del usuario
    return RedirectResponse(
        url="/usuario/inicio",
        status_code=303
    )


# ==========================================
# INICIO DE SESIÓN
# ==========================================

@router.post("/login")
def iniciar_sesion(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    email = email.strip().lower()

    # Buscar usuario
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

    # Verificar contraseña
    if usuario.password != password:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Verificar que esté activo
    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="El usuario está inactivo"
        )

    # Guardar información en sesión
    request.session["usuario_id"] = usuario.id
    request.session["nombre"] = usuario.nombre
    request.session["rol"] = usuario.rol

    # ======================================
    # REDIRECCIÓN SEGÚN EL ROL
    # ======================================

    if usuario.rol == "admin":
        return RedirectResponse(
            url="/admin/inicio",
            status_code=303
        )

    return RedirectResponse(
        url="/usuario/inicio",
        status_code=303
    )