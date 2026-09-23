from fastapi import APIRouter
from app.database.database import SessionLocal
from app.models.usuario import Usuario

router = APIRouter(prefix="/admin", tags=["Administrador"])

@router.get("/usuarios")
def listar_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        return [
            {
                "id": u.id,
                "nombre": u.nombre,
                "email": u.email,
                "rol": u.rol,
                "activo": u.activo
            }
            for u in usuarios
        ]
    finally:
        db.close()
