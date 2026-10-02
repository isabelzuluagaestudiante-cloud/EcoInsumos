# EcoInsumos - Esquema de Colores

## Guía de Colores y Clases CSS

### 📋 Colores Principales

| Elemento | Color | Código | Uso |
|----------|-------|--------|-----|
| Primario (Azul) | Azul | #2563EB | Logo, botones principales, enlaces |
| Verde (Éxito) | Verde | #10B981 | Agregar al carrito, etiquetas positivas |
| Naranja (Alerta) | Naranja | #F59E0B | Ofertas, descuentos, promociones |
| Rojo (Peligro) | Rojo | #EF4444 | Alertas, eliminación |
| Texto Principal | Gris Oscuro | #172033 | Títulos, texto principal |
| Texto Secundario | Gris Medio | #4B5563 | Descripción, texto normal |
| Fondo General | Blanco | #FFFFFF | Fondo general y tarjetas |
| Fondo Alternado | Gris Claro | #F3F4F6 | Secciones alternas |

---

## 🎨 Clases CSS por Funcionalidad

### Botones

```html
<!-- Botón Azul (Crear cuenta, Iniciar sesión) -->
<button class="btn-primary"> o class="btn-blue"> Crear cuenta </button>

<!-- Botón Verde (Agregar al carrito) -->
<button class="btn-green"> o class="btn-success"> Agregar al carrito </button>

<!-- Botón Naranja (Oferta, Promoción) -->
<button class="btn-orange"> o class="btn-warning"> Oferta </button>

<!-- Botón Rojo (Peligro) -->
<button class="btn-red"> o class="btn-danger"> Eliminar </button>
```

### Etiquetas/Badges

```html
<!-- Etiqueta Verde (Nuevo, Disponible) -->
<span class="tag-disponible"> Disponible </span>
<span class="badge-success"> Nuevo </span>

<!-- Etiqueta Naranja (Descuento, Promoción) -->
<span class="tag-descuento"> -20% </span>
<span class="tag-promocion"> Oferta </span>

<!-- Etiqueta Azul (General) -->
<span class="tag-general"> Categoría </span>
<span class="badge-primary"> Info </span>
```

### Fondos de Secciones

```html
<!-- Sección Alternada (Fondo Gris) -->
<section class="section-alternate"> ... </section>
<div class="alternate-bg"> ... </div>
```

### Texto de Énfasis

```html
<!-- Textos de Color -->
<p class="text-primary"> Texto en azul </p>
<p class="text-success"> Texto en verde </p>
<p class="text-warning"> Texto en naranja </p>
<p class="text-danger"> Texto en rojo </p>

<!-- Fondos de Color -->
<div class="bg-primary"> ... </div>
<div class="bg-success"> ... </div>
<div class="bg-warning"> ... </div>
<div class="bg-danger"> ... </div>
```

### Precio de Productos

```html
<!-- Precio Normal -->
<span class="price"> $120 </span>
<span class="product-price"> $85.50 </span>

<!-- Precio Anterior (Tachado) -->
<span class="price-old"> $150 </span>
```

---

## 📐 Variables CSS Disponibles

```css
:root {
    --primary-color: #2563EB;      /* Azul */
    --success-color: #10B981;      /* Verde */
    --warning-color: #F59E0B;      /* Naranja */
    --danger-color: #EF4444;       /* Rojo */
    
    --text-color: #172033;         /* Gris Oscuro */
    --text-light: #4B5563;         /* Gris Medio */
    
    --background-color: #FFFFFF;   /* Blanco */
    --background-alternate: #F3F4F6; /* Gris Claro */
}
```

---

## 🎯 Ejemplos de Uso

### Tarjeta de Producto

```html
<article class="card">
    <img src="producto.jpg" alt="Producto">
    <span class="badge-success"> Nuevo </span>
    <h3> Producto Destacado </h3>
    <p> Descripción del producto </p>
    
    <div style="display: flex; gap: 10px; justify-content: space-between;">
        <span class="price"> $99.99 </span>
        <button class="btn-green"> Agregar al carrito </button>
    </div>
</article>
```

### Sección con Fondo Alternativo

```html
<section class="section-alternate">
    <h2> Promociones Especiales </h2>
    <div>
        <span class="tag-promocion"> Oferta </span>
        <price class="price"> $59.99 </price>
    </div>
</section>
```

### Botones en Encabezado

```html
<header>
    <div class="brand-mark"> EI </div>
    <span> EcoInsumos </span>
    <nav>
        <a href="/login" class="btn-primary"> Iniciar sesión </a>
        <a href="/register" class="btn-blue"> Crear cuenta </a>
    </nav>
</header>
```

---

## ✅ Checklist de Aplicación

- [ ] Encabezado con logo azul (#2563EB)
- [ ] Botones "Iniciar sesión" y "Crear cuenta" en azul (#2563EB)
- [ ] Fondo general blanco (#FFFFFF)
- [ ] Títulos en gris oscuro (#172033)
- [ ] Texto normal en gris medio (#4B5563)
- [ ] Tarjetas blancas con bordes suaves
- [ ] Precios en azul (#2563EB)
- [ ] Etiquetas "Nuevo" y "Disponible" en verde (#10B981)
- [ ] Etiquetas "Descuento" en naranja (#F59E0B)
- [ ] Botón "Agregar al carrito" en verde (#10B981)
- [ ] Botón "Oferta" en naranja (#F59E0B)
- [ ] Secciones alternas con fondo gris (#F3F4F6)
