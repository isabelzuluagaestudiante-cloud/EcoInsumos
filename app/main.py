import os
from pathlib import Path

from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine, SessionLocal
from app.models.categoria import Categoria
from app.models.productos import Producto
from app.models.carrito import Carrito
from app.models.usuario import Usuario
from app.models.mensaje import Mensaje
from app.controllers.auth_controller import router as auth_router
from app.controllers.usuario_controller import router as usuario_router
from app.controllers.admin_controller import router as admin_router
from app.controllers.categoria_controller import router as categoria_router
from app.controllers.carrito_controller import router as carrito_router

BASE_DIR = Path(__file__).resolve().parent.parent

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    if db.query(Categoria).count() == 0:
        categorias_default = [
            Categoria(nombre="Escritorio", descripcion="Artículos para escritorio y oficina."),
            Categoria(nombre="Escolar", descripcion="Útiles y materiales escolares."),
            Categoria(nombre="Electrónica", descripcion="Dispositivos y accesorios electrónicos."),
            Categoria(nombre="Muebles", descripcion="Muebles y artículos del hogar."),
        ]
        db.add_all(categorias_default)
        db.commit()

app = FastAPI(title="EcoInsumos - MVC")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "ecoinsumos-dev-secret"),
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "app" / "static")),
    name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "views"))

app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(admin_router)
app.include_router(categoria_router)
app.include_router(carrito_router)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)