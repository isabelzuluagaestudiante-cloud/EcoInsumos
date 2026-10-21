// ==========================================
// ECOINSUMOS - MODALES
// ==========================================

window.ecoToast = function (mensaje, tipo = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        container.setAttribute("aria-live", "polite");
        document.body.appendChild(container);
    }

    const icono = tipo === "success" ? "check" : tipo === "error" ? "message" : "box";
    const toast = document.createElement("div");
    toast.className = "toast " + tipo;
    toast.innerHTML = '<span class="toast-icon"><svg class="ui-icon" aria-hidden="true"><use href="/static/icons.svg#' + icono + '"></use></svg></span><span class="toast-text"></span><button class="toast-close" type="button" aria-label="Cerrar notificación">×</button>';
    toast.querySelector(".toast-text").textContent = mensaje;
    container.appendChild(toast);

    const cerrar = () => {
        toast.classList.add("is-leaving");
        window.setTimeout(() => toast.remove(), 220);
    };
    toast.querySelector(".toast-close").addEventListener("click", cerrar);
    window.setTimeout(cerrar, 4200);
};

window.alert = function (mensaje) {
    window.ecoToast(String(mensaje), "info");
};

document.addEventListener("DOMContentLoaded", function () {


    // ======================================
    // ELEMENTOS
    // ======================================

    const loginOverlay = document.getElementById("loginOverlay");
    const registerOverlay = document.getElementById("registerOverlay");

    const openLogin = document.getElementById("openLogin");
    const openRegister = document.getElementById("openRegister");
    const openRegister2 = document.getElementById("openRegister2");

    const closeLogin = document.getElementById("closeLogin");
    const closeRegister = document.getElementById("closeRegister");

    const toRegister = document.getElementById("toRegister");
    const toLogin = document.getElementById("toLogin");

    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    const loginMessage = document.getElementById("loginMessage");
    const registerMessage = document.getElementById("registerMessage");


    // ======================================
    // ABRIR LOGIN
    // ======================================

    if (openLogin) {

        openLogin.addEventListener("click", function () {

            loginOverlay.classList.remove("hidden");

            registerOverlay.classList.add("hidden");

            limpiarMensaje(loginMessage);

        });

    }


    // ======================================
    // ABRIR REGISTRO
    // ======================================

    function abrirRegistro() {

        registerOverlay.classList.remove("hidden");

        loginOverlay.classList.add("hidden");

        limpiarMensaje(registerMessage);

    }


    if (openRegister) {

        openRegister.addEventListener(
            "click",
            abrirRegistro
        );

    }


    if (openRegister2) {

        openRegister2.addEventListener(
            "click",
            abrirRegistro
        );

    }


    // ======================================
    // CERRAR LOGIN
    // ======================================

    if (closeLogin) {

        closeLogin.addEventListener("click", function () {

            loginOverlay.classList.add("hidden");

        });

    }


    // ======================================
    // CERRAR REGISTRO
    // ======================================

    if (closeRegister) {

        closeRegister.addEventListener("click", function () {

            registerOverlay.classList.add("hidden");

        });

    }


    // ======================================
    // LOGIN -> REGISTRO
    // ======================================

    if (toRegister) {

        toRegister.addEventListener("click", function () {

            abrirRegistro();

        });

    }


    // ======================================
    // REGISTRO -> LOGIN
    // ======================================

    if (toLogin) {

        toLogin.addEventListener("click", function () {

            registerOverlay.classList.add("hidden");

            loginOverlay.classList.remove("hidden");

            limpiarMensaje(loginMessage);

        });

    }


    // ======================================
    // CERRAR AL HACER CLICK FUERA
    // ======================================

    if (loginOverlay) {

        loginOverlay.addEventListener("click", function (event) {

            if (event.target === loginOverlay) {

                loginOverlay.classList.add("hidden");

            }

        });

    }


    if (registerOverlay) {

        registerOverlay.addEventListener("click", function (event) {

            if (event.target === registerOverlay) {

                registerOverlay.classList.add("hidden");

            }

        });

    }


    // ======================================
    // REGISTRO
    // ======================================

    if (registerForm) {

        registerForm.addEventListener(
            "submit",
            registrarUsuario
        );

    }


    async function registrarUsuario(event) {

        event.preventDefault();


        const formData = new FormData(registerForm);


        mostrarMensaje(
            registerMessage,
            "Registrando usuario...",
            "info"
        );


        try {

            const response = await fetch(
                "/auth/registro",
                {
                    method: "POST",
                    body: formData
                }
            );


            const data = await response.json();


            if (!response.ok || !data.ok) {

                mostrarMensaje(
                    registerMessage,
                    data.mensaje || "No fue posible registrar el usuario.",
                    "error"
                );

                return;

            }


            // ==================================
            // REGISTRO CORRECTO
            // ==================================

            mostrarMensaje(
                registerMessage,
                data.mensaje,
                "success"
            );


            registerForm.reset();


            // Después de 1.5 segundos
            // abrir login

            setTimeout(function () {

                registerOverlay.classList.add("hidden");

                loginOverlay.classList.remove("hidden");

                mostrarMensaje(
                    loginMessage,
                    "Cuenta creada. Ahora puedes iniciar sesión.",
                    "success"
                );

            }, 1500);


        } catch (error) {

            console.error(error);

            mostrarMensaje(
                registerMessage,
                "Error de conexión con el servidor.",
                "error"
            );

        }

    }


    // ======================================
    // LOGIN
    // ======================================

    if (loginForm) {

        loginForm.addEventListener(
            "submit",
            iniciarSesion
        );

    }


    async function iniciarSesion(event) {

        event.preventDefault();


        const formData = new FormData(loginForm);


        mostrarMensaje(
            loginMessage,
            "Iniciando sesión...",
            "info"
        );


        try {

            const response = await fetch(
                "/auth/login",
                {
                    method: "POST",
                    body: formData
                }
            );


            const data = await response.json();


            if (!response.ok || !data.ok) {

                mostrarMensaje(
                    loginMessage,
                    data.mensaje || "No fue posible iniciar sesión.",
                    "error"
                );

                return;

            }


            // ==================================
            // LOGIN CORRECTO
            // ==================================

            mostrarMensaje(
                loginMessage,
                "Bienvenido, " + data.usuario,
                "success"
            );


            console.log(
                "Usuario:",
                data.usuario
            );

            console.log(
                "Rol:",
                data.rol
            );


            // ==================================
            // REDIRECCIÓN SEGÚN ROL
            // ==================================

            setTimeout(function () {

                if (data.rol === "admin") {

                    window.location.href =
                        "/admin";

                } else {

                    window.location.href =
                        "/usuario";

                }

            }, 1000);


        } catch (error) {

            console.error(error);

            mostrarMensaje(
                loginMessage,
                "Error de conexión con el servidor.",
                "error"
            );

        }

    }


    // ======================================
    // MOSTRAR MENSAJE
    // ======================================

    function mostrarMensaje(
        elemento,
        mensaje,
        tipo
    ) {

        if (!elemento) {
            return;
        }


        elemento.textContent = mensaje;

        elemento.classList.remove(
            "hidden",
            "error",
            "success",
            "info"
        );


        elemento.classList.add(tipo);

    }


    // ======================================
    // LIMPIAR MENSAJE
    // ======================================

    function limpiarMensaje(elemento) {

        if (!elemento) {
            return;
        }


        elemento.textContent = "";

        elemento.classList.add("hidden");

        elemento.classList.remove(
            "error",
            "success",
            "info"
        );

    }

    // ======================================
    // NAV TOGGLE (HAMBURGUESA) - responsive
    // ======================================

    const hamburgers = document.querySelectorAll('.hamburger');

    if (hamburgers.length) {

        hamburgers.forEach(function (btn) {

            btn.addEventListener('click', function () {

                const container = btn.closest('.nav-container');

                if (!container) return;

                const expanded = btn.getAttribute('aria-expanded') === 'true';

                btn.setAttribute('aria-expanded', String(!expanded));

                container.classList.toggle('open');

            });

            // Cerrar menú al pulsar un enlace
            const links = document.querySelectorAll('.nav-links a');

            links.forEach(function (a) {
                a.addEventListener('click', function () {
                    const cnt = a.closest('.nav-container');
                    if (!cnt) return;
                    cnt.classList.remove('open');
                    const hb = cnt.querySelector('.hamburger');
                    if (hb) hb.setAttribute('aria-expanded', 'false');
                });
            });

        });

    }

    // Menú de cuenta: evita navegar a una respuesta JSON al cambiar datos.
    document.querySelectorAll(".account-form").forEach(function (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            const esEliminacion = form.classList.contains("account-delete");
            if (esEliminacion && !window.confirm("¿Eliminar tu cuenta definitivamente? Esta acción no se puede deshacer.")) {
                return;
            }

            try {
                const response = await fetch(form.action, { method: "POST", body: new FormData(form) });
                const data = await response.json();
                if (!response.ok || !data.ok) {
                    window.ecoToast(data.mensaje || "No fue posible completar la operación.", "error");
                    return;
                }
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                    return;
                }
                form.reset();
                window.ecoToast(data.mensaje, "success");
            } catch (error) {
                window.ecoToast("Error de conexión con el servidor.", "error");
            }
        });
    });

    // Sincroniza la insignia numérica del carrito en todas las vistas de usuario.
    const enlacesCarrito = document.querySelectorAll('.nav-links a[href="/carrito/"]');
    if (enlacesCarrito.length) {
        fetch('/carrito/contador')
            .then((respuesta) => respuesta.ok ? respuesta.json() : { cantidad: 0 })
            .then((datos) => enlacesCarrito.forEach((enlace) => {
                let contador = enlace.querySelector('.cart-count');
                if (!contador) {
                    contador = document.createElement('span');
                    contador.className = 'cart-count';
                    enlace.appendChild(contador);
                }
                contador.textContent = datos.cantidad;
                contador.setAttribute('aria-label', datos.cantidad + ' artículos en el carrito');
            }))
            .catch(() => {});
    }

});
