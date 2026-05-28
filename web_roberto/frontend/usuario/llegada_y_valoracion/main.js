/**
 * @file main.js
 * @description Gestión de la interfaz de valoración del servicio.
 * Permite al usuario calificar su experiencia mediante un sistema de estrellas
 * y enviar los datos de la misión junto con comentarios a la base de datos.
 * @author Mery
 * @version 1.0.0
 */
let rating = 0;

// ==========================================
// 1. CARGAR DATOS REALES AL ABRIR LA PÁGINA
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  // Recuperar datos guardados por la pantalla anterior (navigation.js)
  const destName = sessionStorage.getItem('currentDestinationName') || "Destino";
  const durationSecs = parseInt(sessionStorage.getItem('tripDuration')) || 0;
  const distance = sessionStorage.getItem('tripDistance') || "--";

  // Formatear duración (de segundos a formato MM:SS)
  const mins = Math.floor(durationSecs / 60);
  const secs = durationSecs % 60;
  const timeFormatted = `${mins}:${secs.toString().padStart(2, '0')}`;

  // Inyectar los valores reales en el HTML, sustituyendo los Mocks
  const terminalEl = document.querySelector('.terminal');
  if (terminalEl) terminalEl.innerHTML = `<span>⌂</span> ${destName}`;
  
  const duracionEl = document.getElementById('duracion');
  if (duracionEl) duracionEl.textContent = timeFormatted;

  const distanciaEl = document.getElementById('distancia');
  if (distanciaEl) distanciaEl.textContent = `${distance}m`;
});

/**
 * Configura los eventos de interacción para el sistema de estrellas.
 * Al hacer clic, actualiza la variable global 'rating' y la apariencia visual.
 * @author Mery
 */
const stars = document.querySelectorAll("#stars span");

stars.forEach(star => {
  star.addEventListener("click", () => {
    rating = parseInt(star.dataset.value);
    stars.forEach((s, idx) => {
      s.classList.toggle("active", idx < rating);
    });
  });
});

/**
 * Gestiona el envío del formulario de feedback.
 * Valida la entrada, recopila los datos de la interacción y los envía a la API.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
document.getElementById("finalizar").addEventListener("click", async () => {
if (rating === 0) {
    alert("Por favor, selecciona una puntuación.");
    return;
  }

  const comentario = document.getElementById("comentario").value;
  const interaccionId = sessionStorage.getItem('currentInteraccionId');
  
  // Recuperar datos en caso de que tengamos que forzar el guardado
  const durationSecs = parseInt(sessionStorage.getItem('tripDuration')) || 0;
  const destId = sessionStorage.getItem('currentDestinationId') || 1;

  try {
    if (interaccionId) {
        // FLUJO NORMAL: Tenemos el ID, solo actualizamos las estrellas (PUT)
        const data = {
            interaccionId: parseInt(interaccionId),
            valoracion: rating,
            comentario: comentario || null
        };

        const res = await fetch("/api/interaccion/valorar", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        
        await res.json();
        
    } else {
        // PLAN B DE EMERGENCIA: Si no hay ID, creamos todo el registro de golpe (POST)
        const dataEmergencia = {
            robotId: 1,
            zonaActualId: 3, // Usamos un ID de zona seguro (como en tu código original)
            zonaDestinoId: parseInt(destId),
            duracion: durationSecs,
            valoracion: rating,
            comentario: comentario || null
        };

        // Reutilizamos tu endpoint original que guardaba todo junto si hiciera falta
        // Si no tienes /api/valoracion, usa la lógica de inserción completa
        await fetch("/api/interaccion/llegada", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dataEmergencia)
        }).then(res => res.json()).then(async data => {
            if(data.success && data.id) {
                await fetch("/api/interaccion/valorar", {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        interaccionId: parseInt(data.id),
                        valoracion: rating,
                        comentario: comentario || null
                    })
                });
            }
        });
    }

    // Termine como termine, agradecemos al usuario y lo mandamos al inicio
    alert("Servicio finalizado. ¡Gracias por tu feedback!");
    sessionStorage.clear(); // Limpiamos la memoria del viaje
    window.location.href = '../index.html'; 

  } catch (error) {
    console.error("Error BD:", error);
    // Si hay error, no bloqueamos al pasajero
    alert("Servicio finalizado (Modo offline). ¡Gracias por tu feedback!");
    sessionStorage.clear();
    window.location.href = '../seleccion_destino/index.html';
  }
});