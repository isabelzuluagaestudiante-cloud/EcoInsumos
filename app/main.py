import os
from pathlib import Path

from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, SessionLocal, engine, actualizar_esquema
from app.models.categoria import Categoria
from app.models.productos import Producto
from app.models.carrito import Carrito
from app.models.compra import Compra
from app.models.mensaje import Mensaje
from app.models.intercambio import SolicitudIntercambio
from app.models.usuario import Usuario
from app.controllers.auth_controller import router as auth_router
from app.controllers.usuario_controller import router as usuario_router
from app.controllers.admin_controller import router as admin_router
from app.controllers.categoria_controller import router as categoria_router
from app.controllers.carrito_controller import router as carrito_router

BASE_DIR = Path(__file__).resolve().parent.parent

Base.metadata.create_all(bind=engine)
actualizar_esquema()


def sembrar_categorias() -> None:
    db = SessionLocal()
    try:
        if not db.query(Categoria).first():
            db.add_all([
                Categoria(nombre="Oficina", descripcion="Artículos para el trabajo y la oficina.", imagen="categoria-oficina-ia.png"),
                Categoria(nombre="Escolar", descripcion="Útiles y materiales educativos.", imagen="categoria-escolar-ia.png"),
                Categoria(nombre="Arte", descripcion="Materiales para crear.", imagen="categoria-arte-ia.png"),
                Categoria(nombre="Tecnología", descripcion="Equipos y accesorios tecnológicos.", imagen="categoria-tecnologia-ia.png"),
            ])
            db.commit()
    finally:
        db.close()


sembrar_categorias()


def sembrar_productos_demo() -> None:
    """Crea un catálogo mínimo de demostración sin duplicarlo en cada inicio."""
    db = SessionLocal()
    try:
        vendedor = db.query(Usuario).filter(Usuario.email == "vendedor.demo@ecoinsumos.local").first()
        if not vendedor:
            vendedor = Usuario(
                nombre="Tienda Eco Demo", email="vendedor.demo@ecoinsumos.local",
                password="demo-segura-2026", whatsapp="+573001112233", rol="usuario", activo=True,
            )
            db.add(vendedor)
            db.flush()

        categorias = {categoria.nombre: categoria for categoria in db.query(Categoria).all()}
        imagenes_categoria = {
            "Oficina": "categoria-oficina-ia.png", "Escolar": "categoria-escolar-ia.png",
            "Arte": "categoria-arte-ia.png", "Tecnología": "categoria-tecnologia-ia.png",
        }
        for nombre, imagen in imagenes_categoria.items():
            if nombre in categorias:
                categorias[nombre].imagen = imagen
        productos = [
            ("Organizador de escritorio", "Organizador metálico reutilizado, ideal para lápices y clips.", 18000, "Oficina", "organizador-escritorio-ia.png"),
            ("Set de marcadores escolares", "Marcadores en buen estado para proyectos y tareas.", 12000, "Escolar", "marcadores-escolares-ia.png"),
            ("Cuaderno de apuntes", "Cuaderno con hojas disponibles para una segunda oportunidad.", 6000, "Escolar", "categoria-escolar-ia.png"),
            ("Regla metálica", "Regla resistente de 30 cm para estudio u oficina.", 5000, "Oficina", "categoria-oficina-ia.png"),
            ("Portalápices reciclado", "Portalápices elaborado con material reutilizado.", 8000, "Arte", "categoria-arte-ia.png"),
            ("Mouse USB funcional", "Mouse con cable, probado y listo para usar.", 15000, "Tecnología", "categoria-tecnologia-ia.png"),
        ]
        for nombre, descripcion, precio, categoria, imagen in productos:
            existente = db.query(Producto).filter(Producto.nombre == nombre).first()
            if existente and not existente.imagen:
                existente.imagen = imagen
            elif categoria in categorias and not existente:
                db.add(Producto(
                    nombre=nombre, descripcion=descripcion, precio=precio,
                    categoria_id=categorias[categoria].id, vendedor_id=vendedor.id,
                    imagen=imagen, disponible=True,
                ))
        db.commit()
    finally:
        db.close()


sembrar_productos_demo()

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
