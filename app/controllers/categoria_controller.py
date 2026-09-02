from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.categoria import Categoria

router = APIRouter(prefix="/categorias", tags=["categorias"])
templates = Jinja2Templates(directory="app/views")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_categorias(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse(
        "usuario/categorias.html",
        {"request": request, "categorias": categorias},
    )