/*
- Valida campos del formulario
- Envía el input a la API mediante una petición
- Redirige a otra página / muestra mensaje de error

Autor: Maria ALgora
*/

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formularioIngreso');
    const emailInput = document.getElementById('correoElectronico');
    const passwordInput = document.getElementById('contrasena');
    const contenedorCorreo = document.getElementById('contenedorCorreo');
    const contenedorContrasena = document.getElementById('contenedorContrasena');
    const mensajeErrorCorreo = document.getElementById('mensajeErrorCorreo');
    const mensajeErrorContrasena = document.getElementById('mensajeErrorContrasena');
    const togglePassword = document.getElementById('alternarContrasena');
    const ojoIcono = document.getElementById('ojoIcono');
    const botonIngreso = document.getElementById('botonIngreso');

    // URL de tu API
    const API_URL = '/api/login';

    // Mostrar/ocultar contrasena
    let passwordVisible = false;
    togglePassword.addEventListener('click', function () {
        passwordVisible = !passwordVisible;
        if (passwordVisible) {
            passwordInput.type = 'text';
            ojoIcono.innerHTML = `
                <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" stroke="currentColor" stroke-width="1.4"/>
                <circle cx="12" cy="12" r="2.4" stroke="currentColor" stroke-width="1.4"/>
                <path d="M21 3L3 21" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            `;
        } else {
            passwordInput.type = 'password';
            ojoIcono.innerHTML = `
                <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" stroke="currentColor" stroke-width="1.4"/>
                <circle cx="12" cy="12" r="2.4" stroke="currentColor" stroke-width="1.4"/>
            `;
        }
    });

    function validarEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function limpiarErrores() {
        contenedorCorreo.classList.remove('error');
        contenedorContrasena.classList.remove('error');
        mensajeErrorCorreo.classList.remove('show');
        mensajeErrorContrasena.classList.remove('show');
        mensajeErrorCorreo.textContent = '';
        mensajeErrorContrasena.textContent = '';
    }

    function errorCorreo(mensaje) {
        contenedorCorreo.classList.add('error');
        mensajeErrorCorreo.textContent = mensaje;
        mensajeErrorCorreo.classList.add('show');
    }

    function errorContrasena(mensaje) {
        contenedorContrasena.classList.add('error');
        mensajeErrorContrasena.textContent = mensaje;
        mensajeErrorContrasena.classList.add('show');
    }

    function validarFormulario() {
        limpiarErrores();

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        let valido = true;

        if (email === '') {
            errorCorreo('El correo electronico es obligatorio');
            valido = false;
        } else if (!validarEmail(email)) {
            errorCorreo('Introduce un correo valido (ejemplo: usuario@dominio.com)');
            valido = false;
        }

        if (password === '') {
            errorContrasena('La contrasena es obligatoria');
            valido = false;
        } else if (password.length < 4) {
            errorContrasena('La contrasena debe tener al menos 4 caracteres');
            valido = false;
        } else if (password.length > 20) {
            errorContrasena('La contrasena no puede tener mas de 20 caracteres');
            valido = false;
        }

        return valido;
    }

    function mostrarErrorGeneral(mensaje) {
        let errorGeneral = document.getElementById('errorGeneral');
        if (!errorGeneral) {
            errorGeneral = document.createElement('div');
            errorGeneral.id = 'errorGeneral';
            errorGeneral.style.cssText = `
                background: #fee2e2;
                color: #c44c4c;
                padding: 10px;
                border-radius: 10px;
                margin-top: 15px;
                font-size: 13px;
                text-align: center;
                border: 1px solid #fecaca;
            `;
            form.appendChild(errorGeneral);
        }
        errorGeneral.textContent = mensaje;
        errorGeneral.style.display = 'block';

        setTimeout(() => {
            errorGeneral.style.display = 'none';
        }, 5000);
    }

    function ocultarErrorGeneral() {
        const errorGeneral = document.getElementById('errorGeneral');
        if (errorGeneral) {
            errorGeneral.style.display = 'none';
        }
    }

    // Enviar formulario a la API
    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        ocultarErrorGeneral();

        if (validarFormulario()) {
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            const recordarme = document.getElementById('recordarme').checked;

            if (recordarme) {
                localStorage.setItem('usuarioRecordado', email);
            } else {
                localStorage.removeItem('usuarioRecordado');
            }

            const textoOriginal = botonIngreso.textContent;
            botonIngreso.textContent = 'Validando...';
            botonIngreso.disabled = true;

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (data.success) {
                    const check = await fetch('/api/dashboard', {
                        credentials: 'include'
                    });

                    if (check.ok) {
                        window.location.href = '/tecnico/dashboard.html';
                    } else {
                        mostrarErrorGeneral('No autorizado');
                    }
                } else {
                    if (data.message === 'Usuario no encontrado') {
                        errorCorreo('Usuario no registrado');
                    } else if (data.message === 'Contraseña incorrecta') {
                        errorContrasena('Contraseña incorrecta');
                    } else {
                        mostrarErrorGeneral(data.message || 'Error al iniciar sesion');
                    }
                }

            } catch (error) {
                console.error('Error de conexion:', error);
                mostrarErrorGeneral('Error de conexion con el servidor');
            } finally {
                botonIngreso.textContent = textoOriginal;
                botonIngreso.disabled = false;
            }
        }
    });

    // Limpiar error al escribir
    emailInput.addEventListener('input', function () {
        contenedorCorreo.classList.remove('error');
        mensajeErrorCorreo.classList.remove('show');
        mensajeErrorCorreo.textContent = '';
        ocultarErrorGeneral();
    });

    passwordInput.addEventListener('input', function () {
        contenedorContrasena.classList.remove('error');
        mensajeErrorContrasena.classList.remove('show');
        mensajeErrorContrasena.textContent = '';
        ocultarErrorGeneral();
    });

    // Enlace "¿Olvido su contrasena?"
    document.getElementById('enlaceOlvidaste').addEventListener('click', function (e) {
        e.preventDefault();
        alert('Funcionalidad de recuperacion de contrasena');
    });

    // Cargar usuario recordado
    const usuarioRecordado = localStorage.getItem('usuarioRecordado');
    if (usuarioRecordado) {
        emailInput.value = usuarioRecordado;
        document.getElementById('recordarme').checked = true;
    }
});