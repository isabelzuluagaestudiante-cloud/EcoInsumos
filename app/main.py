from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine

from app.controllers.auth_controller import router as auth_router
from app.controllers.usuario_controller import router as usuario_router
from app.controllers.admin_controller import router as admin_router


# Crear tablas
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="EcoInsumos - MVC"
)


# =========================
# ARCHIVOS ESTÁTICOS
# =========================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# =========================
# TEMPLATES
# =========================

templates = Jinja2Templates(
    directory="app/views"
)


# =========================
# ROUTERS
# =========================

app.include_router(auth_router)

app.include_router(usuario_router)

app.include_router(admin_router)


# =========================
# INDEX
# =========================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )