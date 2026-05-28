const translations = {
    "es": {
        "subtitle": "Robot guía y transporte de equipaje",
        "welcome": "Bienvenido al sistema de transporte automático",
        "selectLang": "Selecciona tu idioma",
        "startBtn": "Comenzar",
        "techTooltip": "Acceso Técnico"
    },
    "en": {
        "subtitle": "Guide and luggage transport robot",
        "welcome": "Welcome to the automatic transport system",
        "selectLang": "Select your language",
        "startBtn": "Start",
        "techTooltip": "Technical Access"
    },
    "de": {
        "subtitle": "Führer- und Gepäcktransportroboter",
        "welcome": "Willkommen im automatischen Transportsystem",
        "selectLang": "Wähle deine Sprache",
        "startBtn": "Beginnen",
        "techTooltip": "Technischer Zugang"
    },
    "fr": {
        "subtitle": "Robot guide et transport de bagages",
        "welcome": "Bienvenue dans le système de transport automatique",
        "selectLang": "Sélectionnez votre langue",
        "startBtn": "Commencer",
        "techTooltip": "Accès Technique"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const langBtns = document.querySelectorAll('.lang-btn');
    const subtitle = document.getElementById('subtitle');
    const welcome = document.getElementById('welcome');
    const selectLang = document.getElementById('select-lang');
    const startBtn = document.getElementById('start-btn');
    const techBtn = document.getElementById('tech-btn');

    // Función para aplicar idiomas y persistir
    const applyLang = (lang) => {
        subtitle.textContent = translations[lang].subtitle;
        welcome.textContent = translations[lang].welcome;
        selectLang.textContent = translations[lang].selectLang;
        startBtn.textContent = translations[lang].startBtn;
        techBtn.setAttribute('title', translations[lang].techTooltip);
        techBtn.setAttribute('aria-label', translations[lang].techTooltip);
        
        localStorage.setItem('lang', lang);
    };

    // Inicializar con el último idioma guardado (o español)
    let currentLang = localStorage.getItem('lang') || 'es';
    applyLang(currentLang);
    
    // Marcar botón activo
    langBtns.forEach(btn => {
        if(btn.getAttribute('data-lang') === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
        
        btn.addEventListener('click', () => {
            langBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const lang = btn.getAttribute('data-lang');
            applyLang(lang);
        });
    });

    // Redirección al siguiente menú
    startBtn.addEventListener('click', () => {
        window.location.href = 'maletas/maletas.html';
    });

    // Botón Técnico Oculto
    techBtn.addEventListener('click', () => {
        window.location.href = '/tecnico/login/login.html';
    });
});
