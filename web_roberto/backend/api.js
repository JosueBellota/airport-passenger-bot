/**
 * @file api.js
 * @description Definición de rutas de la API REST para el proyecto "Roberto".
 * Este módulo actúa como intermediario entre la interfaz web, el sistema ROS 2 
 * y la base de datos MySQL, gestionando la navegación, telemetría y autenticación.
 * @authors Maria, Mery, Chris
 * @version 1.0.0
 */
const express = require('express');
const router = express.Router();
const logica = require('./logica');
const rosClient = require('./rosClient');

/**
 * @route GET /api/position
 * @description Obtiene la última posición conocida del robot (X, Y) desde la memoria de ROS.
 * @author Mery
 */
router.get('/position', (req, res) => {
    res.json(rosClient.getLatestPosition());
});

/**
 * @route GET /api/goal
 * @description Retorna las coordenadas del objetivo (Goal) actual al que se dirige el robot.
 * @author Mery
 */
router.get('/goal', (req, res) => {
    res.json(rosClient.getCurrentGoal());
});

/**
 * @route GET /api/zonas
 * @description Recupera la lista completa de zonas con sus IDs y nombres.
 * @author Mery
 */
router.get('/zonas', async (req, res) => {
    try {
        const zonas = await logica.getAllZonas();
        res.json(zonas);
    } catch (err) {
        res.status(500).json({ error: 'Failed to load zonas' });
    }
});

/**
 * @route POST /api/sendGoal
 * @description Envía una orden de movimiento al robot basada en el ID de una zona.
 * @param {number} zonaId - ID de la zona de destino.
 * @author Mery
 */
router.post('/sendGoal', async (req, res) => {
    const { zonaId } = req.body;

    try {
        const zona = await logica.getZonaById(zonaId);

        if (!zona) {
            return res.status(404).json({ error: 'Zona not found' });
        }

        rosClient.sendGoal(zona.PosX, zona.PosY);

        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: 'Failed to send goal' });
    }
});


/**
 * @route GET /api/destinos
 * @description Obtiene y organiza las zonas por categorías (puertas, comida, ocio, etc.)
 * para ser mostradas en el menú de navegación del cliente.
 * @author Chris
 */
router.get('/destinos', async (req, res) => {
    try {
        const zonas = await logica.getZonas();
        
        const destinationMap = {};
        
        // Mapeamos los Tipos de la BD a las IDs quemadas en el frontend que usaban los SVGs.
        // Opcional: También podríamos pasar todo de forma directa
        const typeKeys = {
            'Puerta': 'puertas',
            'Comida': 'comida',
            'Ocio': 'ocio',
            'Salida': 'salida'
        };

        for (const z of zonas) {
            const key = typeKeys[z.TipoZona] || z.TipoZona.toLowerCase();
            
            if (!destinationMap[key]) {
                destinationMap[key] = [];
            }
            
            destinationMap[key].push({
                id: z.ZonaID.toString(),
                name: z.Nombre, // Ej. "Puerta 12"
                subtitle: z.TipoZona, 
                // Usando valores fijos temporales ya que Roberto.sql no tiene distancias ni tiempo; 
                // Se podría calcular más adelante por coordenadas (PosX, PosY)
                time: 'Calculando...',
                dist: Math.round(Math.sqrt(z.PosX*z.PosX + z.PosY*z.PosY)) + 'm'
            });
        }

        res.json({ success: true, data: { destinations: destinationMap } });
    } catch (error) {
        console.error('[API] Error obteniendo destinos:', error);
        res.status(500).json({ success: false, message: 'Database error' });
    }
});

/**
 * @route GET /api/robots
 * @description Obtiene el listado de robots y su estado actual de conexión.
 */
router.get('/robots', async (req, res) => {
    try {
        const robots = await logica.getRobots();
        res.json({ success: true, data: { robots } });
    } catch (error) {
        console.error('[API] Error obteniendo robots:', error);
        res.status(500).json({ success: false, message: 'Database error' });
    }
});

/**
 * @route POST /api/navigate
 * @description Inicia un proceso de navegación simulada.
 * @author Mery
 */
router.post('/navigate', async (req, res) => {
    const { destination_id } = req.body;
    console.log(`[API Navigation] Navegación iniciada hacia destino ID: ${destination_id}`);
    res.json({ success: true, message: 'Navegación simulada localmente (Robot avisado).' });
});
/**
 * @route POST /api/valoracion
 * @description Registra el feedback de un usuario sobre una interacción con el robot.
 * @author Mery
 */
/**
 * @route POST /api/valoracion
 * @description Registra el feedback de un usuario sobre una interacción con el robot.
 * @author Mery
 */
router.post('/valoracion', async (req, res) => {
    try {
        const {
            robotId,
            zonaActualId,
            zonaDestinoId,
            duracion,
            valoracion,
            comentario
        } = req.body;

        res.json({ success: true, message: 'Valoración recibida' });

    } catch (error) {
        console.error('[API] Error guardando la valoración:', error);
        res.status(500).json({ success: false, message: 'Database error' });
    }
});

// PUT /api/interaccion/valorar -> Actualiza el registro final con estrellas y comentario
router.put('/interaccion/valorar', async (req, res) => {
    try {
        const { interaccionId, valoracion, comentario } = req.body;
        
        if (!interaccionId || !valoracion) {
            return res.status(400).json({ 
                success: false, 
                message: 'Faltan datos (interaccionId o valoracion)' 
            });
        }

        await logica.updateInteraccion(interaccionId, valoracion, comentario);
        
        res.json({ 
            success: true, 
            message: 'Valoración actualizada correctamente en la BD' 
        });

    } catch (error) {
        console.error('[API] Error actualizando valoración:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Database error' 
        });
    }
});

// POST /api/interaccion/llegada -> Guarda el trayecto al llegar (sin valoración)
router.post('/interaccion/llegada', async (req, res) => {
    try {
        const { robotId, zonaActualId, zonaDestinoId, duracion } = req.body;
        
        const id = await logica.insertInteraccion({
            robotId,
            zonaActualId,
            zonaDestinoId,
            duracion,
            valoracion: null,
            comentario: null
        });

        res.json({ success: true, id });
    } catch (error) {
        console.error('[API] Error guardando llegada:', error);
        res.status(500).json({ success: false, message: 'Database error' });
    }
});

// POST /api/interaccion/llegada -> Guarda el trayecto al llegar (sin valoración)
router.post('/interaccion/llegada', async (req, res) => {
    try {
        const { robotId, zonaActualId, zonaDestinoId, duracion } = req.body;
        
        const id = await logica.insertInteraccion({
            robotId,
            zonaActualId,
            zonaDestinoId,
            duracion,
            valoracion: null,
            comentario: null
        });

        res.json({ success: true, id });
    } catch (error) {
        console.error('[API] Error guardando llegada:', error);
        res.status(500).json({ success: false, message: 'Database error' });
    }
});

// PUT /api/interaccion/valorar -> Actualiza el registro final con estrellas y comentario
router.put('/interaccion/valorar', async (req, res) => {
    try {
        const { interaccionId, valoracion, comentario } = req.body;
        
        if (!interaccionId || !valoracion) {
            return res.status(400).json({ success: false, message: 'Faltan datos' });
        }

        await logica.updateInteraccion(interaccionId, valoracion, comentario);
        res.json({ success: true, message: 'Valoración actualizada correctamente' });
    } catch (error) {
        console.error('[API] Error actualizando valoración:', error);
        res.status(500).json({ success: false });
    }
});

/**
 * @route POST /api/robot/status
 * @description Registra eventos de conexión y desconexión del robot en la DB.
 * @author Chris
 */
router.post('/robot/status', async (req, res) => {
    const { robotId, status } = req.body;
    try {
        await logica.logConnectionEvent(robotId || 1, status);
        res.json({ success: true, message: 'Status logged in backend DB successfully.' });
    } catch (error) {
        console.error('[API] Error saving robot status:', error);
        res.status(500).json({ success: false, message: 'Database logging error' });
    }
});
/**
 * @route GET /api/historial
 * @description Obtiene el historial completo de interacciones detalladas.
 * @author Mery
 */
router.get('/historial', async (req, res) => {
    try {
        const historial = await logica.getInteracciones();
        res.json(historial);
    } catch (err) {
        console.error('[API] Error obteniendo historial:', err);
        res.status(500).json({ success: false, error: 'Failed to load history' });
    }
});
/**
 * @route GET /api/robots/names
 * @description Retorna un array simple con los nombres de los robots para filtros.
 * @author Mery
 */
router.get('/robots/names', async (req, res) => {
    try {
        const robots = await logica.getRobotNames();
        // Mapeamos para enviar un array simple de strings: ["Roberto1", "Roberto2"]
        const names = robots.map(r => r.Nombre);
        res.json(names);
    } catch (err) {
        res.status(500).json({ success: false, message: 'Error al obtener nombres de robots' });
    }
});

/**
 * @route GET /api/zonas/names
 * @description Retorna un array simple con los nombres de las zonas para filtros.
 * @author Mery
 */
router.get('/zonas/names', async (req, res) => {
    try {
        const zonas = await logica.getZonaNames();
        // Enviamos ["Puerta 12", "Restaurante B", ...]
        const names = zonas.map(z => z.Nombre);
        res.json(names);
    } catch (err) {
        res.status(500).json({ success: false, message: 'Error al obtener nombres de zonas' });
    }
});
/**
 * @route POST /api/login
 * @description Autentica a un técnico y crea una sesión activa.
 * @author Maria Algora
 */
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({
            success: false,
            message: 'Email y contraseña son obligatorios'
        });
    }

    try {
        const result = await logica.validarCredenciales(email, password);

        if (!result.success) {
            return res.status(401).json(result);
        }

        console.log(`Login correcto: ${email}`);

        req.session.usuario = {
            id: result.usuario.id,
            email: result.usuario.email,
            nombre: result.usuario.nombre || null
        };


        res.json({
            success: true,
            message: 'Login correcto',
            usuario: req.session.usuario
        });

    } catch (error) {
        console.error('Error en login:', error);
        res.status(500).json({
            success: false,
            message: 'Error interno del servidor'
        });
    }
});
/**
 * @route GET /api/dashboard
 * @description Verifica si hay una sesión activa y retorna los datos del técnico.
 */
router.get('/dashboard', (req, res) => {
    if (!req.session.usuario) {
        return res.status(401).json({
            success: false,
            message: 'No autorizado'
        });
    }

    res.json({
        success: true,
        usuario: req.session.usuario
    });
});
/**
 * @route POST /api/logout
 * @description Finaliza la sesión actual del técnico.
 */
router.post('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).json({
                success: false,
                message: 'Error al cerrar sesión'
            });
        }

        res.json({
            success: true,
            message: 'Sesión cerrada'
        });
    });
});

/**
 * @route GET /api/eventos
 * @description Obtiene todas las incidencias (eventos) del sistema.
 */
router.get('/eventos', async (req, res) => {
    try {
        const eventos = await logica.getEventosConEstado();
        res.json(eventos);
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error al obtener eventos' });
    }
});

/**
 * @route POST /api/eventos/resolver
 * @description Registra una acción de mantenimiento y cierra la incidencia.
 */
router.post('/eventos/resolver', async (req, res) => {
    const { eventoId, accion } = req.body;
    const tecnicoId = req.session.usuario ? req.session.usuario.id : 1; 

    try {
        await logica.resolverEvento(eventoId, tecnicoId, accion);
        res.json({ success: true, message: 'Incidencia resuelta' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error al resolver' });
    }
});

// --- Rutas de Reconocimiento Facial ---
const facialLogic = require('./facial_logic');

router.post('/facial/process', async (req, res) => {
    try {
        const result = await facialLogic.processImages();
        res.json({ success: true, output: result });
    } catch (err) {
        res.status(500).json({ success: false, error: err });
    }
});

router.post('/facial/train', async (req, res) => {
    try {
        const result = await facialLogic.trainModel();
        res.json({ success: true, output: result });
    } catch (err) {
        res.status(500).json({ success: false, error: err });
    }
});

router.post('/facial/open', async (req, res) => {
    try {
        const result = await facialLogic.openFaceApp();
        res.json({ success: true, output: result });
    } catch (err) {
        res.status(500).json({ success: false, error: err });
    }
});

router.post('/facial/verify', async (req, res) => {
    try {
        const { image } = req.body;
        const result = await facialLogic.verifyFrame(image);
        res.json({ success: true, results: result });
    } catch (err) {
        res.status(500).json({ success: false, error: err });
    }
});

module.exports = router;
