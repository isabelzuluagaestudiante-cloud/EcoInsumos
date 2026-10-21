(() => {
    const clave = "ecoinsumos-theme";
    const preferido = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    const aplicar = (tema) => {
        document.documentElement.dataset.theme = tema;
        document.querySelectorAll("[data-theme-toggle]").forEach((boton) => {
            const oscuro = tema === "dark";
            const icono = boton.querySelector("use");
            if (icono) icono.setAttribute("href", "/static/icons.svg#" + (oscuro ? "sun" : "moon"));
            boton.setAttribute("aria-pressed", String(oscuro));
            boton.setAttribute("aria-label", oscuro ? "Activar modo día" : "Activar modo noche");
            boton.title = oscuro ? "Activar modo día" : "Activar modo noche";
        });
    };
    aplicar(localStorage.getItem(clave) || preferido);
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-theme-toggle]").forEach((boton) => {
            boton.addEventListener("click", () => {
                const nuevoTema = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
                localStorage.setItem(clave, nuevoTema);
                aplicar(nuevoTema);
            });
        });
    });
})();
