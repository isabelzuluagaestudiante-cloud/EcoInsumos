"""
Script para agregar datos de prueba a la base de datos
Ejecutar: python seed_data.py
"""

from app.database.database import SessionLocal, Base, engine
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.models.productos import Producto
from app.models.carrito import Carrito

# Crear todas las tablas si no existen
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verificar si ya existen datos
    if db.query(Categoria).count() == 0:
        print("✅ Inserting sample categories...")
        categorias = [
            Categoria(nombre="Escritorio", descripcion="Artículos para el escritorio y oficina"),
            Categoria(nombre="Escolar", descripcion="Materiales y útiles escolares"),
            Categoria(nombre="Electrónica", descripcion="Dispositivos y accesorios electrónicos"),
            Categoria(nombre="Muebles", descripcion="Muebles y decoración"),
        ]
        db.add_all(categorias)
        db.commit()
        print(f"✅ {len(categorias)} categorías agregadas")
    else:
        print("ℹ️  Las categorías ya existen")

    # Agregar productos de prueba
    if db.query(Producto).count() == 0:
        print("✅ Inserting sample products...")
        cat_escritorio = db.query(Categoria).filter_by(nombre="Escritorio").first()
        cat_escolar = db.query(Categoria).filter_by(nombre="Escolar").first()
        
        productos = [
            Producto(
                nombre="Escritorio de madera",
                descripcion="Escritorio en perfecto estado",
                categoria_id=cat_escritorio.id if cat_escritorio else 1,
                precio=50000
            ),
            Producto(
                nombre="Set de lápices",
                descripcion="Lápices de colores, 24 unidades",
                categoria_id=cat_escolar.id if cat_escolar else 2,
                precio=15000
            ),
        ]
        db.add_all(productos)
        db.commit()
        print(f"✅ {len(productos)} productos agregados")
    else:
        print("ℹ️  Los productos ya existen")

    print("\n✅ Datos de prueba cargados exitosamente")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
