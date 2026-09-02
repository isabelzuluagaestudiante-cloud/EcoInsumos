from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.carrito import Carrito

router = APIRouter(prefix="/carrito", tags=["carrito"])
templates = Jinja2Templates(directory="app/views")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def ver_carrito(request: Request, db: Session = Depends(get_db)):
    items = db.query(Carrito).all()
    return templates.TemplateResponse(
        "usuario/carrito.html",
        {"request": request, "items": items},
    )