/**
 * @file main.js
 * @description Controlador del Frontend para el panel del técnico del robot "Roberto".
 * Gestiona la visualización del mapa mediante ROS2D, la telemetría suavizada (LERP),
 * la navegación interactiva y el filtrado avanzado del historial de misiones.
 * @authors Maria, Mery, Chris
 * @version 1.0.0
 */
 
// -----------------------------
// ESTADO GLOBAL
// -----------------------------
let allZonas = [];
let currentGoal = null;
let currentPos = { x: 0, y: 0 };
let targetPos = null; // This now represents the REAL ROS position

// Marker references for global access
let robotMarker, goalMarker, robotLayer;

window.onload = () => {
    // -----------------------------
    // ROS CONNECTION
    // -----------------------------
    const ros = new ROSLIB.Ros({
        url: `ws://${window.location.hostname}:9090`
    });

    ros.on('connection', () => console.log('Connected to ROS Bridge'));
    ros.on('error', (error) => console.error('ROS error:', error));

    // -----------------------------
    // VIEWER SETUP
    // -----------------------------
    const mapDiv = document.getElementById('map-canvas');
    const viewer = new ROS2D.Viewer({
        divID: 'map-canvas',
        width: mapDiv.clientWidth || 600,
        height: mapDiv.clientHeight || 400
    });

    // -----------------------------
    // MAP CLIENT
    // -----------------------------
    const gridClient = new ROS2D.OccupancyGridClient({
        ros: ros,
        rootObject: viewer.scene
    });

    // -----------------------------
    // UNIFIED ROBOT LAYER
    // -----------------------------
    robotLayer = new createjs.Container();
    viewer.scene.addChild(robotLayer);

    // Blue Robot Marker
    robotMarker = new createjs.Shape();
    robotMarker.graphics.beginFill("blue").drawCircle(0, 0, 5);
    robotMarker.scaleX = robotMarker.scaleY = 0.03;
    robotLayer.addChild(robotMarker);

    // Red Goal Marker
    goalMarker = new createjs.Shape();
    goalMarker.graphics.beginFill("red").drawCircle(0, 0, 5);
    goalMarker.scaleX = goalMarker.scaleY = 0.03; 
    goalMarker.visible = false;
    robotLayer.addChild(goalMarker);

    // -----------------------------
    // MAP EVENT
    // -----------------------------
    gridClient.on('change', () => {
        console.log("Map Grid Received");
        viewer.scaleToDimensions(
            gridClient.currentGrid.width,
            gridClient.currentGrid.height
        );
        viewer.shift(
            gridClient.currentGrid.pose.position.x,
            gridClient.currentGrid.pose.position.y
        );
        // Start position tracking once map is ready
        initRobotPosition();
    });

/**
 * @description Realiza una petición al backend para obtener la posición actual del robot.
 * Actualiza la variable global targetPos con las coordenadas (x, y) reales.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
    async function fetchTelemetry() {
        try {
            const res = await fetch('/api/position');
            const data = await res.json();
            
            // If the backend has a real AMCL pose, set it as the target
            if (data && data.x !== undefined && !isNaN(data.x)) {
                targetPos = { 
                    x: parseFloat(data.x), 
                    y: parseFloat(data.y) 
                };
            }
        } catch (err) {
            console.warn("Telemetry fetch error:", err);
        }
    }

    // Poll the backend for the real /amcl_pose every 100ms
    setInterval(fetchTelemetry, 100);

/**
 * @description Actualiza la posición de los marcadores (robot y meta) en el canvas.
 * Aplica la inversión del eje Y para transformar coordenadas ROS a coordenadas de píxeles.
 * @author Mery
 * @returns {void}
 */
    function updateVisuals() {
        if (!isNaN(currentPos.x) && !isNaN(currentPos.y)) {
            robotMarker.x = currentPos.x;
            robotMarker.y = -currentPos.y; // ROS Y-flip
        }

        if (currentGoal && !isNaN(currentGoal.x) && !isNaN(currentGoal.y)) {
            goalMarker.visible = true;
            goalMarker.x = currentGoal.x;
            goalMarker.y = -currentGoal.y; // ROS Y-flip
        } else {
            goalMarker.visible = false;
        }
    }

/**
 * @description Sincroniza la posición inicial del marcador visual con la posición 
 * real del robot al cargar la página o el mapa para evitar saltos visuales.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
    async function initRobotPosition() {
        try {
            const res = await fetch('/api/position');
            const data = await res.json();
            if (data && data.x !== undefined) {
                currentPos.x = parseFloat(data.x);
                currentPos.y = parseFloat(data.y);
                targetPos = { x: currentPos.x, y: currentPos.y };
                updateVisuals();
            }
        } catch (err) {
            console.error("Init pos error:", err);
        }
    }

    // -----------------------------
    // SMOOTH MOVEMENT ENGINE (LERP)
    // -----------------------------
    setInterval(() => {
        if (!targetPos) return;

        // Calculate distance to the REAL robot position
        const dx = targetPos.x - currentPos.x;
        const dy = targetPos.y - currentPos.y;

        // Smoothly slide the dot toward the actual telemetry coordinates
        // Using 0.1 (10%) for a balanced smoothness
        if (Math.abs(dx) > 0.0001 || Math.abs(dy) > 0.0001) {
            currentPos.x += dx * 0.1;
            currentPos.y += dy * 0.1;
            updateVisuals();
        }
    }, 50);

    // -----------------------------
    // BATTERY UPDATE
    // -----------------------------
    setInterval(() => {
        fetch('/api/robots')
            .then(res => res.json())
            .then(resData => {
                if (resData.success && resData.data.robots.length) {
                    const batteryStat = document.querySelector('.battery-status span');
                    if (batteryStat) {
                        batteryStat.textContent = `${resData.data.robots[0].Bateria}%`;
                    }
                }
            })
            .catch(() => {});
    }, 1000);
};

/**
 * @description Gestiona el envío de un nuevo objetivo de navegación.
 * Obtiene coordenadas de la zona, actualiza la UI y notifica al backend/Nav2.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
window.sendGoal = async function () {
    const zonaSelect = document.getElementById('zonaSelect');
    const zonaId = zonaSelect.value;
    const selectedZona = allZonas.find(z => z.ZonaID == zonaId);

    if (!selectedZona) return;

    const valX = parseFloat(selectedZona.PosX);
    const valY = parseFloat(selectedZona.PosY);

    if (isNaN(valX) || isNaN(valY)) {
        console.error("Zone coordinates are invalid (NaN):", selectedZona);
        return;
    }

    // Set destination marker visually
    currentGoal = { x: valX, y: valY };

    console.log(`Goal set to: ${selectedZona.Nombre} at (${valX}, ${valY})`);

    // Immediate UI Update for the Red Dot
    if (goalMarker) {
        goalMarker.visible = true;
        goalMarker.x = valX;
        goalMarker.y = -valY;
    }

    // Inform Backend (which publishes to /goal_pose)
    await fetch('/api/sendGoal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zonaId })
    });
};

/**
 * @description Recupera la lista de zonas desde la base de datos y rellena 
 * el selector de destinos en la interfaz de usuario.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
async function loadZonas() {
    try {
        const res = await fetch('/api/zonas');
        allZonas = await res.json();
        
        const select = document.getElementById('zonaSelect');
        if (!select) return;

        select.innerHTML = '<option value="">Seleccionar destino...</option>';
        allZonas.forEach(z => {
            const option = document.createElement('option');
            option.value = z.ZonaID;
            option.textContent = z.Nombre;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Load Zones error:", err);
    }
}

loadZonas();

//login
document.addEventListener('DOMContentLoaded', async () => {
    const res = await fetch('/api/dashboard', {
        credentials: 'include'
    });

    if (!res.ok) {
        window.location.href = '/tecnico/login/login.html';
    }
});

// Logout
document.getElementById("confirmLogout").addEventListener("click", async () => {
    try {
        await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (err) {
        console.warn(err);
    }

    window.location.href = '/usuario/index.html';
});


//------------------------------------------------------- */

/* --- HISTORIAL FUNCIONAL START --- */



let fullHistoryData = []; 
/**
 * @description Actualiza la interfaz del historial consultando la API. 
 * Gestiona tanto la vista previa como la tabla completa del modal.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
async function updateHistoryUI() {
    try {
        const response = await fetch('/api/historial'); 
        fullHistoryData = await response.json();

        // 1. Render Dashboard Preview
        renderPreview(fullHistoryData.slice(0, 4));

        // 2. Render Modal Table (apply current filters)
        applyFilters();

    } catch (error) {
        console.error("Error al cargar el historial:", error);
    }
}


/**
 * @description Pobla dinámicamente los elementos <select> de los filtros en el modal 
 * con los nombres de robots y zonas extraídos de la base de datos.
 * @author Mery
 * @async
 * @returns {Promise<void>}
 */
async function populateFilters() {
    try {
        // Cargar nombres de Robots
        const resRobots = await fetch('/api/robots/names');
        const robotNames = await resRobots.json();
        const robotSelect = document.getElementById('filter-robot');
        if (robotSelect) {
            robotSelect.innerHTML = '<option value="">Robot</option>' + 
                robotNames.map(name => `<option value="${name}">${name}</option>`).join('');
        }

        // Cargar nombres de Zonas (Usamos la misma lista para Zona Actual y Destino)
        const resZonas = await fetch('/api/zonas/names');
        const zonaNames = await resZonas.json();
        
        const zonaActualSelect = document.getElementById('filter-zona');
        if (zonaActualSelect) {
            zonaActualSelect.innerHTML = '<option value="">Zona actual</option>' + 
                zonaNames.map(name => `<option value="${name}">${name}</option>`).join('');
        }

        const destinoSelect = document.getElementById('filter-destino');
        if (destinoSelect) {
            destinoSelect.innerHTML = '<option value="">Destino</option>' + 
                zonaNames.map(name => `<option value="${name}">${name}</option>`).join('');
        }
    } catch (err) {
        console.error("Error populating filters:", err);
    }
}

/**
 * @description Cambia la página activa del historial y solicita un nuevo renderizado de la tabla.
 * @author Mery
 * @param {number} page - Índice de la página de destino.
 * @param {number} totalPages - Cantidad máxima de páginas disponibles.
 * @returns {void}
 */
window.changePage = (page, totalPages) => {
    if (page < 1 || page > totalPages) return; // Seguridad para no salir de rango
    currentPage = page;
    
    // Volvemos a aplicar filtros (esto llamará a renderTable con la nueva página)
    applyFilters(); 
};


function renderPreview(data) {
    const previewList = document.getElementById('history-preview-list');
    if (!previewList) return;
    previewList.innerHTML = data.map(log => `
        <div class="history-item-row">
            <div class="history-text-group">
                <span class="history-route-title">${log.Robot} → ${log.Destino}</span>
                <span class="history-sub-detail">
                    <i class="ph ph-clock"></i> ${Math.floor(log.Duracion / 60)}m ${log.Duracion % 60}s
                </span>
            </div>
            <div class="star-gold">${'★'.repeat(log.Valoracion)}${'☆'.repeat(5-log.Valoracion)}</div>
        </div>
    `).join('');
}

function applyFilters() {

    const robotFilter = document.getElementById('filter-robot').value;
    const destinoFilter = document.getElementById('filter-destino').value;
    const zonaFilter = document.getElementById('filter-zona').value;
    const valoracionFilter = document.getElementById('filter-valoracion').value;
    const dateFilter = document.getElementById('filter-date').value;

    const filtered = fullHistoryData.filter(log => {
        const matchRobot = robotFilter === "" || log.Robot === robotFilter;
        const matchDestino = destinoFilter === "" || log.Destino === destinoFilter;
        const matchZona = zonaFilter === "" || log.ZonaActual === zonaFilter;
        const matchValor = valoracionFilter === "" || log.Valoracion == valoracionFilter;
        // Lógica para la fecha
        let matchDate = true;
        if (dateFilter !== "") {
            const logDate = new Date(log.FechaHora).toISOString().split('T')[0];
            matchDate = logDate === dateFilter;
        }

        return matchRobot && matchDestino &&matchZona   &&matchValor && matchDate;
    });

    renderTable(filtered);
}
/**
 * @description Exporta el historial de interacciones almacenado a un archivo .csv.
 * @author Mery
 * @returns {void}
 */
window.exportToCSV = () => {
    if (fullHistoryData.length === 0) return;
    
    // Convert filtered data to CSV string
    const headers = ["ID,Robot,Zona Actual,Destino,Fecha,Duracion,Valoracion,Comentario"];
    const rows = fullHistoryData.map(log => 
        `${log.InteraccionID},${log.Robot},${log.ZonaActual},${log.Destino},${log.FechaHora},${log.Duracion},${log.Valoracion},"${log.Comentario || ''}"`
    );
    
    const csvContent = "data:text/csv;charset=utf-8," + headers.concat(rows).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "historial_roberto.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
/* --- LÓGICA DE PAGINACIÓN DINÁMICA --- */
let currentPage = 1;
const rowsPerPage = 10;
/**
 * @description Genera los controles de paginación (números y flechas) calculando 
 * el total de páginas necesarias para el conjunto de datos actual.
 * @author Mery
 * @param {number} totalItems - Número total de registros filtrados.
 * @returns {void}
 */
function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / rowsPerPage);
    const container = document.getElementById('pagination-controls');
    if (!container) return;

    if (totalPages <= 1) {
        container.innerHTML = ''; 
        return;
    }

    // Botón Izquierdo
    let html = `<i class="ph ph-caret-left" onclick="changePage(${currentPage - 1}, ${totalPages})" style="cursor:pointer"></i>`;
    
    // Números de página
    for (let i = 1; i <= totalPages; i++) {
        html += `<span class="page-num ${i === currentPage ? 'active' : ''}" onclick="changePage(${i}, ${totalPages})">${i}</span>`;
    }
    
    // Botón Derecho
    html += `<i class="ph ph-caret-right" onclick="changePage(${currentPage + 1}, ${totalPages})" style="cursor:pointer"></i>`;
    
    container.innerHTML = html;
}
/**
 * @description Renderiza las filas de la tabla de historial basándose en los datos 
 * filtrados y el índice de la página actual.
 * @author Mery
 * @param {Array<Object>} data - Lista de interacciones a mostrar.
 * @returns {void}
 */
function renderTable(data) {
    const tableBody = document.getElementById('full-history-table-body');
    const stats = document.getElementById('table-stats');
    if (!tableBody) return;

    const total = data.length;

    // --- LÓGICA DE RECORTAR DATOS (Slicing) ---
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = data.slice(start, end); // Solo toma las 10 filas de esta página

    if (total === 0) {
        tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px;">No se encontraron resultados</td></tr>`;
        if (stats) stats.innerText = "No hay interacciones";
        return;
    }

    // Dibujar las filas recortadas
    tableBody.innerHTML = paginatedData.map(log => `
        <tr>
            <td>${log.InteraccionID}</td>
            <td><strong>${log.Robot}</strong></td>
            <td>${log.ZonaActual}</td>
            <td>${log.Destino}</td>
            <td style="font-size: 0.85rem;">${new Date(log.FechaHora).toLocaleString()}</td>
            <td>${Math.floor(log.Duracion / 60)}m ${log.Duracion % 60}s</td>
            <td><span class="star-gold">${'★'.repeat(log.Valoracion)}${'☆'.repeat(5-log.Valoracion)}</span></td>
            <td style="color: #6b7280; font-size: 0.85rem;">${log.Comentario || 'Sin comentarios'}</td>
        </tr>
    `).join('');

    // Actualizar texto de estadísticas dinámicamente
    if (stats) {
        stats.innerText = `Mostrando ${start + 1} a ${Math.min(end, total)} de ${total} interacciones`;
    }

    renderPagination(total);
}
/**
 * @description Resetea todos los valores de los filtros a su estado inicial.
 * @author Mery
 * @returns {void}
 */
window.clearAllFilters = () => {
    document.getElementById('filter-robot').value = "";
    document.getElementById('filter-destino').value = "";
    document.getElementById('filter-zona').value = "";
    document.getElementById('filter-valoracion').value = "";
    if(document.getElementById('filter-date')) document.getElementById('filter-date').value = "";
    renderTable(fullHistoryData);
};

window.openHistoryModal = () => {
    document.getElementById('historyModal').style.display = 'flex';
};

window.closeHistoryModal = () => {
    document.getElementById('historyModal').style.display = 'none';
};

// Listen for changes on all filters
document.addEventListener('change', (e) => {
    if (e.target.id && e.target.id.startsWith('filter-')) {
        applyFilters();
    }
});

// INITIAL LOAD
document.addEventListener('DOMContentLoaded', () => {
    populateFilters(); // Llena los dropdowns desde la base de datos
    updateHistoryUI(); // Carga los datos de la tabla
});

/* --- LÓGICA DE INCIDENCIAS --- */
let todasLasIncidencias = [];
let estadoFiltroIncidencias = 'Abierto'; // <-- Cambiado a Abierto

window.toggleIncidenciasPanel = () => {
    const panel = document.getElementById('panel-incidencias');
    panel.classList.toggle('open');
    if(panel.classList.contains('open')) actualizarIncidencias();
};

window.filtrarIncidencias = (estado) => {
    estadoFiltroIncidencias = estado;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.getAttribute('onclick').includes(estado)));
    renderizarIncidencias();
};

async function actualizarIncidencias() {
    try {
        const res = await fetch('/api/eventos');
        const data = await res.json();
        
        // Control de errores de API
        if (!Array.isArray(data)) {
            console.error("Error de la API:", data);
            document.getElementById('lista-incidencias').innerHTML = '<p style="text-align:center; color:red;">Error de base de datos.</p>';
            return;
        }

        todasLasIncidencias = data;
        
        const abiertas = todasLasIncidencias.filter(i => i.Estado === 'Abierto').length;
        const badge = document.getElementById('badge-incidencias');
        if (badge) {
            badge.innerText = abiertas;
            badge.style.display = abiertas > 0 ? 'block' : 'none';
        }
        
        renderizarIncidencias();
    } catch (err) {
        console.error("Error al hacer fetch:", err);
        document.getElementById('lista-incidencias').innerHTML = '<p style="text-align:center; color:red;">Error de conexión.</p>';
    }
}

function renderizarIncidencias() {
    const lista = document.getElementById('lista-incidencias');
    const filtradas = todasLasIncidencias.filter(i => i.Estado === estadoFiltroIncidencias);
    
    lista.innerHTML = filtradas.map(inc => `
        <div class="incidencia-card ${(inc.Severidad && inc.Severidad.includes('Error')) ? 'severidad-alta' : ''} ${inc.Estado === 'Cerrado' ? 'resuelta' : ''}">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:5px;">
                <strong>${inc.RobotNombre || 'Robot ' + inc.RobotID}</strong>
                <span style="color:gray">${new Date(inc.FechaHora).toLocaleString()}</span>
            </div>
            <div style="font-weight:600; font-size:0.9rem;">${inc.TipoEvento}</div>
            
            <p style="font-size:0.85rem; margin:5px 0;">${inc.Mensaje}</p> 
            
            ${inc.Estado === 'Abierto' ? `
                <button class="btn-resolver" style="background:#eee; color:#333;" onclick="document.getElementById('f-${inc.EventoID}').style.display='block'; this.style.display='none'">Resolver</button>
                <div id="f-${inc.EventoID}" class="resolver-form">
                    <textarea id="t-${inc.EventoID}" placeholder="Acción realizada..."></textarea>
                    <button class="btn-resolver" onclick="confirmarResolucion(${inc.EventoID})">Confirmar</button>
                </div>
            ` : `
               <div style="font-size:0.8rem; color:#10b981; margin-top:5px;"><i class="ph ph-check-circle"></i> Cerrado el: ${new Date(inc.CerradaEn).toLocaleString()}</div>
            `}
        </div>
    `).join('') || '<p style="text-align:center; color:gray;">No hay incidencias.</p>';
}

window.confirmarResolucion = async (id) => {
    const accion = document.getElementById(`t-${id}`).value;
    if(!accion) return alert("Describe la acción");
    
    await fetch('/api/eventos/resolver', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ eventoId: id, accion })
    });
    actualizarIncidencias();
};

// Polling suave para el badge
setInterval(actualizarIncidencias, 10000);

/* --- HISTORIAL FUNCIONAL END --- */
