# EcoInsumos - FastAPI MVC

Arquitectura MVC sencilla con:
- FastAPI
- SQLAlchemy
- SQLite
- Usuario y administrador
- Registro e inicio de sesión

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Desde la carpeta raíz:

```bash
python -m uvicorn app.main:app --reload
```

Abrir:
http://127.0.0.1:8000/docs

## Arquitectura

- models/: modelos de datos
- views/: páginas HTML
- controllers/: lógica de las rutas
- database/: conexión a la base de datos
- static/: CSS y recursos estáticos

Nota: este es un esqueleto académico. Para producción se debe añadir hash de contraseñas, JWT/sesiones, validación de roles y configuración segura.


python -m uvicorn app.main:app --reload