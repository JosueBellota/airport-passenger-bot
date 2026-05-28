// main.js - Interfaz del Pasajero (Roberto)
const UI_TRANSLATIONS = {
    es: {
        titleCat: "Selecciona tu destino",
        subtitleCat: "Elige la categoría a la que deseas ir",
        titleSub: "Selecciona tu destino específico",
        subtitleSub: "Elige a dónde quieres ir dentro de esta zona",
        summaryDest: "DESTINO SELECCIONADO",
        dist: "Distancia",
        time: "Tiempo estimado",
        btnContinue: "Continuar",
        btnSending: "Enviando comando...",
        navigating: "Iniciando navegación...",
        // Categorías
        cat_puertas: { name: "Puerta 1-21", sub: "Vuelos internacionales" },
        cat_comida: { name: "Comida", sub: "Restaurantes" },
        cat_ocio: { name: "Ocio", sub: "Tiendas y compras" },
        cat_salida: { name: "Salida", sub: "Salida principal" },
        wordGate: "Puerta",
        sub_embarque: "Embarque",
        sub_embarqueVip: "Embarque VIP",
        // T09 - Navegación en curso
        navTitle: "Roberto está en camino",
        navSubtitle: "Sigue al robot hasta tu destino",
        liveData: "DATOS EN VIVO",
        navSpeed: "Velocidad",
        navDistLeft: "Distancia restante",
        navEta: "Tiempo Estimado",
        navProg: "Progreso",
        navWarning: "Por favor, mantente cerca de Roberto durante el trayecto"
    },
    en: {
        titleCat: "Select your destination",
        subtitleCat: "Choose the category you want to go to",
        titleSub: "Select specific destination",
        subtitleSub: "Choose where you want to go within this area",
        summaryDest: "SELECTED DESTINATION",
        dist: "Distance",
        time: "Estimated time",
        btnContinue: "Continue",
        btnSending: "Sending command...",
        navigating: "Starting navigation...",
        cat_puertas: { name: "Gate 1-21", sub: "International flights" },
        cat_comida: { name: "Food", sub: "Restaurants" },
        cat_ocio: { name: "Leisure", sub: "Shops & Shopping" },
        cat_salida: { name: "Exit", sub: "Main exit" },
        wordGate: "Gate",
        sub_embarque: "Boarding",
        sub_embarqueVip: "VIP Boarding"
    }
};

// Datos base para iconos y estructura de categorías [cite: 392, 459]
const MOCK_CATEGORIES = [
    {
        id: 'puertas',
        svgIcon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.2-1.1.6 0 .1 0 .3.1.4l5.3 4.3L5 15H2l1.5 3.5L7 22v-3l3.5-4.1 4.3 5.3c.1.1.3.2.4.1.4-.2.7-.6.6-1.1z"/></svg>',
        time: '3 min', dist: '350m'
    },
    {
        id: 'comida',
        svgIcon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 10-2-2 2-2 2 2z"/><path d="m12 14-2-2 2-2 2 2z"/><path d="m6 18-2-2 2-2 2 2z"/><path d="m3 21 8-8"/><path d="m21 3-8 8"/></svg>', 
        time: '2 min', dist: '280m'
    },
    {
        id: 'ocio',
        svgIcon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        time: '4 min', dist: '420m'
    },
    {
        id: 'salida',
        svgIcon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>',
        time: '2 min', dist: '180m'
    }
];

// Generador de tarjetas dinámicas
function renderCards(gridId, items, onClickCallback) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '';

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'dest-card';
        card.dataset.id = item.id;
        
        card.innerHTML = `
            <div class="active-indicator"></div>
            <div class="card-top">
                <div class="card-icon">${item.svgIcon || ''}</div>
            </div>
            <h3 class="card-title">${item.name}</h3>
            <p class="card-subtitle">${item.subtitle}</p>
            <div class="card-meta" style="margin-top: 1rem;">
                <div class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    <span>${item.time}</span>
                </div>
                <div class="meta-dot"></div>
                <div class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    <span>${item.dist}</span>
                </div>
            </div>
        `;
        card.addEventListener('click', () => onClickCallback(card, item));
        grid.appendChild(card);
    });
}

function applyLanguage() {
    const lang = localStorage.getItem('lang') || 'es';
    const t = UI_TRANSLATIONS[lang] || UI_TRANSLATIONS['es'];
    
    const elements = {
        'title-text': t.titleCat,
        'subtitle-text': t.subtitleCat,
        'summary-label': t.summaryDest,
        'summary-dist-label': t.dist,
        'summary-time-label': t.time,
        'navigation-text': t.navigating
    };

    for (let id in elements) {
        const el = document.getElementById(id);
        if (el) el.textContent = elements[id];
    }

    const continueBtn = document.getElementById('continue-btn');
    if (continueBtn && continueBtn.querySelector('span')) {
        continueBtn.querySelector('span').textContent = t.btnContinue;
    }

    return t;
}

// ------------------------------------
// Vista de Categorías (index / destination)
// ------------------------------------
function initCategoriesView() {
    const t = applyLanguage();
    const gridId = 'categories-grid';
    if (!document.getElementById(gridId)) return;

    const translatedCategories = MOCK_CATEGORIES.map(cat => ({
        ...cat,
        name: t[`cat_${cat.id}`].name,
        subtitle: t[`cat_${cat.id}`].sub
    }));

    renderCards(gridId, translatedCategories, (card, item) => {
        window.location.href = `subcategory.html?cat=${item.id}`;
    });
}

// ------------------------------------
// Vista de Subcategorías (Selección unificada con API) [cite: 443, 445, 467]
// ------------------------------------
async function initSubcategoryView() {
    const t = applyLanguage();
    let selectedDestination = null;

    try {
        // Obtener destinos reales de la API [cite: 445]
        const res = await fetch('/api/destinos');
        const data = await res.json();
        
        if (data.success) {
            const urlParams = new URLSearchParams(window.location.search);
            let cat = urlParams.get('cat') || 'puertas';
            
            // Asignar iconos de MOCK a los datos de la DB para la visualización
            const categoryIcons = MOCK_CATEGORIES.reduce((acc, c) => ({...acc, [c.id]: c.svgIcon}), {});
            const items = (data.data.destinations[cat] || []).map(d => ({
                ...d,
                svgIcon: categoryIcons[cat] || categoryIcons['puertas']
            }));

            renderCards('destinations-grid', items, (cardElement, itemData) => {
                document.querySelectorAll('.dest-card').forEach(c => c.classList.remove('active'));
                cardElement.classList.add('active');
                selectedDestination = itemData;

                document.getElementById('summary-dest-name').textContent = itemData.name;
                document.getElementById('summary-dest-dist').textContent = itemData.dist;
                document.getElementById('summary-dest-time').textContent = itemData.time;
                document.getElementById('summary-bar').classList.remove('hidden');
                document.getElementById('continue-btn').disabled = false;
            });
        }
    } catch (e) {
        console.error("Error cargando destinos:", e);
    }

    // Lógica de envío de objetivo (Punto A a Punto B) [cite: 158, 445, 468, 469]
    const continueBtn = document.getElementById('continue-btn');
    if (continueBtn) {
        continueBtn.addEventListener('click', async () => {
            if (!selectedDestination) return;

            try {
                continueBtn.querySelector('span').textContent = t.btnSending;
                
                const response = await fetch('/api/sendGoal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ zonaId: selectedDestination.id })
                });

                const result = await response.json();

                if (result.success) {
                    sessionStorage.setItem('currentDestinationName', selectedDestination.name);
                    // Guardamos el ID real de la base de datos
                    sessionStorage.setItem('currentDestinationId', selectedDestination.id);
                    const overlay = document.getElementById('navigation-overlay');
                    if(overlay) overlay.classList.add('active');
                    
                    setTimeout(() => {
                        window.location.href = '../nav_en_curso/navigation.html'; 
                    }, 2000);
                }
            } catch (error) {
                console.error('Error iniciando navegación:', error);
            }
        });
    }
}

// ------------------------------------
// Navegación en Curso (T09) [cite: 471, 472, 473]
// ------------------------------------
function initNavigationView() {
    const t = applyLanguage();

    const setText = (id, text) => { if(document.getElementById(id)) document.getElementById(id).textContent = text; };
    setText('nav-title-text', t.navTitle);
    setText('nav-subtitle-text', t.navSubtitle);
    setText('nav-live-text', t.liveData);
    setText('label-dist', t.navDistLeft);
    setText('label-time', t.navEta);
    setText('label-prog', t.navProg);
    setText('nav-warning-text', t.navWarning);
    setText('nav-destination-name', sessionStorage.getItem('currentDestinationName') || "Destino");
    // Guardar el momento en el que empieza el viaje
    const startTime = Date.now();

    const progressInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/navigation/status');
            const data = await response.json();

            if (!data.active) return;

            // Actualización visual de progreso y telemetría [cite: 273, 473]
            const trackFill = document.getElementById('track-fill');
            const robotMarker = document.getElementById('robot-marker');
            if(trackFill) trackFill.style.width = `${data.progress}%`;
            if(robotMarker) robotMarker.style.left = `${data.progress}%`;

            setText('nav-percentage', `${data.progress}%`);
            setText('nav-speed', `${data.speed.toFixed(1)} m/s`);
            setText('nav-dist', `${data.distance_remaining.toFixed(1)} m`);

            const eta = document.getElementById('nav-eta');
            if (eta && data.eta_seconds > 0) {
                const mins = Math.floor(data.eta_seconds / 60);
                const secs = Math.floor(data.eta_seconds % 60);
                eta.innerText = `${mins}:${secs.toString().padStart(2, '0')} min`;
            }

            // Trigger de llegada automática [cite: 477]
            if (data.arrived) {
                clearInterval(progressInterval);
                // Calcular duración real del viaje en segundos
                const durationSecs = Math.floor((Date.now() - startTime) / 1000);
                const destId = sessionStorage.getItem('currentDestinationId');

                // 1. Guardar la interacción hasta la duración (Valoración nula de momento)
                const res = await fetch('/api/interaccion/llegada', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        robotId: 1, // Suponiendo el Robot 1
                        zonaActualId: 1, // Simulando que sale del inicio
                        zonaDestinoId: destId,
                        duracion: durationSecs
                    })
                });

                const resData = await res.json();
                
                // 2. Guardamos el ID que nos da la BD para usarlo en la pantalla final
                if (resData.success) {
                    sessionStorage.setItem('currentInteraccionId', resData.id);
                }

                // 3. Saltar a la pantalla de valoración con la ruta correcta
                window.location.href = '../llegada_y_valoracion/llegada.html';
                window.location.href = 'llegada.html'; 
            }
        } catch (error) {
            console.error("Error en telemetría:", error);
        }
    }, 500);
}