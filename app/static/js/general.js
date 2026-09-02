// ==========================================
// ECOINSUMOS - MODALES
// ==========================================

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

});