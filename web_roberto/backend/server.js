const express = require('express');
const cors = require('cors');
const path = require('path');
const apiRoutes = require('./api');
const rosClient = require('./rosClient');
const sessionMiddleware = require('./session');

rosClient.init();

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(sessionMiddleware);

// Montar las rutas API
app.use('/api', apiRoutes);

// Servir la carpeta frontend completa estáticamente
// Esto expone /usuario/... y /tecnico/... directamente.
app.use(express.static(path.join(__dirname, '../frontend')));

// Redirigir la raíz directamente a la vista de usuario principal (pasajero)
app.get('/', (req, res) => {
    res.redirect('/usuario/index.html');
});

// Configurar server para escuchar en 0.0.0.0 como especificado
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor Express Local ejecutándose en http://localhost:${PORT}`);
    console.log(`Sirviendo archivos estáticos desde frontend/`);
});
