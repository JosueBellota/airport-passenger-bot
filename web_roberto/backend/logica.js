/**
 * @file logica.js
 * @description Módulo de gestión de base de datos para el proyecto "Roberto".
 * Este archivo centraliza todas las operaciones CRUD y la lógica de persistencia 
 * utilizando MySQL y promesas. Incluye la gestión de telemetría, eventos de sistema, 
 * registro de misiones (interacciones) y validación segura de técnicos.
 * * @authors Maria, Mery, Chris
 * @version 1.0.0
 * @project Roberto 
 */
const mysql = require('mysql2/promise');
const bcrypt = require('bcrypt');

// Configuración de MySQL local apuntando a la base de datos "Roberto"
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'Roberto',
    port: 3306,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});
/**
 * Verifica la conexión inicial con la base de datos Roberto.
 * Imprime un mensaje en consola si la conexión es exitosa o el error correspondiente.
 * @author Chris
 */
async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log('Conexión a DB Roberto (MySQL) exitosa.');
        connection.release();
    } catch (err) {
        console.error('Error de conexión DB Roberto:', err.message);
    }
}
testConnection();

/**
 * Obtiene todas las zonas registradas en la base de datos.
 * @author Mery
 * @returns {Promise<Array>} Lista de objetos de zona.
 */
async function getZonas() {
    const [rows] = await pool.query('SELECT * FROM Zona');
    return rows;
}


/**
 * Obtiene una zona por su ID.
 * @author Mery
 * @param {number} id ID de la zona.
 * @returns {Promise<object|undefined>} Objeto de la zona encontrada o undefined.
 */
async function getZonaById(id) {
    const [rows] = await pool.query('SELECT * FROM Zona WHERE ZonaID = ?', [id]);
    return rows[0];
}

/**
 * Obtiene todas las zonas con coordenadas (para renderizado en mapa).
 * @author Mery
 * @returns {Promise<Array>} Lista de zonas con ID, Nombre y coordenadas PosX, PosY.
 */
async function getAllZonas() {
    // Agregamos PosX y PosY a la consulta para que el mapa pueda dibujar el punto rojo
    const [rows] = await pool.query('SELECT ZonaID, Nombre, PosX, PosY FROM Zona');
    return rows;
}

/**
 * Obtiene todos los robots registrados en el sistema.
 * @author Mery
 * @returns {Promise<Array>} Lista de objetos de robot.
 */
async function getRobots() {
    const [rows] = await pool.query('SELECT * FROM Robot');
    return rows;
}

/**
 * Obtiene los eventos recientes del sistema.
 * @param {number} [robotId] ID opcional para filtrar eventos de un robot específico.
 * @returns {Promise<Array>} Últimos 10 eventos ordenados por fecha.
 */
async function getEventos(robotId) {
    let query = 'SELECT * FROM Evento';
    const params = [];
    if (robotId) {
        query += ' WHERE RobotID = ?';
        params.push(robotId);
    }
    query += ' ORDER BY FechaHora DESC LIMIT 10';
    const [rows] = await pool.query(query, params);
    return rows;
}

/**
 * Registra un evento de conexión/desconexión del robot.
 * @param {number} robotId ID del robot
 * @param {string} status Estado ("connected" | "disconnected")
 * @returns {Promise<void>}
 */
async function logConnectionEvent(robotId, status) {
    const tipoEvento = status === 'connected' ? 'Inicio Sistema' : 'Error de Comunicación';
    const desc = status === 'connected' ? 'Robot conectado a interfaz' : 'Robot desconectado de interfaz';

    await pool.query(
        'INSERT INTO Evento (RobotID, TipoEvento, Descripcion, Gravedad) VALUES (?, ?, ?, ?)',
        [robotId, tipoEvento, desc, status === 'connected' ? 'Notificación' : 'Advertencia']
    );

    if (status === 'connected') {
        await pool.query('UPDATE Robot SET UltimaComunicacion = NOW(), EstadoID = 1 WHERE RobotID = ?', [robotId]);
    } else {
        await pool.query('UPDATE Robot SET UltimaComunicacion = NOW(), EstadoID = 3 WHERE RobotID = ?', [robotId]);
    }
}

/**
 * Inserta una posición del robot en la base de datos.
 * @param {number} robotId ID del robot
 * @param {number} x Posición X
 * @param {number} y Posición Y
 * @returns {Promise<void>}
 */
async function insertPosition(robotId, x, y) {
    try {
        const [result] = await pool.query(
            'INSERT INTO PosicionRobot (RobotID, PosX, PosY, FechaHora) VALUES (?, ?, ?, NOW())',
            [robotId, x, y]
        );
        console.log(`DB Saved: ID ${result.insertId} | x: ${x.toFixed(3)}, y: ${y.toFixed(3)}`);
    } catch (err) {
        // This will tell us if the table name is wrong or a column is missing
        console.error('DATABASE ERROR:', err.message);
    }
}

/**
 * Valida credenciales de un técnico.
 * Si la contraseña está en texto plano, la migra automáticamente a bcrypt.
 * @author Maria Algora
 * @param {string} email Email del técnico
 * @param {string} password Contraseña proporcionada
 * @returns {Promise<{success: boolean, message?: string, usuario?: object}>}
 */
async function validarCredenciales(email, password) {
    try {
        const query = 'SELECT TecnicoID, Nombre, Email, Contrasena FROM Tecnico WHERE Email = ?';
        const [rows] = await pool.query(query, [email]);

        if (!rows || rows.length === 0) {
            return { success: false, message: 'Usuario no encontrado' };
        }

        const tecnico = rows[0];
        let passwordMatch = false;

        if (tecnico.Contrasena.startsWith('$2')) {
            // Contraseña hasheada
            passwordMatch = await bcrypt.compare(password, tecnico.Contrasena);
        } else {
            // Texto plano (migración)
            passwordMatch = tecnico.Contrasena === password;

            if (passwordMatch) {
                const saltRounds = 10;
                const hashed = await bcrypt.hash(password, saltRounds);

                const updateQuery = 'UPDATE Tecnico SET Contrasena = ? WHERE TecnicoID = ?';
                await pool.query(updateQuery, [hashed, tecnico.TecnicoID]);

                console.log(`Contraseña del usuario ${tecnico.Email} migrada a hash.`);
            }
        }

        if (!passwordMatch) {
            return { success: false, message: 'Contraseña incorrecta' };
        }

        return {
            success: true,
            usuario: {
                id: tecnico.TecnicoID,
                nombre: tecnico.Nombre,
                email: tecnico.Email
            }
        };

    } catch (error) {
        console.error('Error en validarCredenciales:', error);
        return { success: false, message: 'Error interno del servidor' };
    }
}
/**
 * Registra una nueva interacción completada por el robot.
 * @author Mery
 * @param {object} data Objeto con IDs de robot/zonas, duración, valoración y comentarios.
 * @returns {Promise<number>} ID de la interacción insertada.
 */
async function insertInteraccion(data) {
    const {
        robotId,
        zonaActualId,
        zonaDestinoId,
        duracion,
        valoracion,
        comentario
    } = data;

    const query = `
        INSERT INTO Interaccion
        (RobotID, ZonaActualID, ZonaDestinoID, FechaHora, Duracion, Valoracion, Comentario)
        VALUES (?, ?, ?, NOW(), ?, ?, ?)
    `;

    const [result] = await pool.query(query, [
        robotId,
        zonaActualId,
        zonaDestinoId,
        duracion,
        valoracion,
        comentario
    ]);

    return result.insertId;
}
/**
 * Obtiene el historial de interacciones del robot.
 * Realiza un JOIN para transformar IDs en nombres legibles (Robot y Zonas).
 * @author Mery
 * @returns {Promise<Array>} Lista de interacciones con nombres de zonas y robots
 */
async function getInteracciones() {
    const query = `
        SELECT 
            i.InteraccionID, 
            r.Nombre AS Robot, 
            z1.Nombre AS ZonaActual, 
            z2.Nombre AS Destino, 
            i.FechaHora, 
            i.Duracion, 
            i.Valoracion, 
            i.Comentario
        FROM Interaccion i
        JOIN Robot r ON i.RobotID = r.RobotID
        JOIN Zona z1 ON i.ZonaActualID = z1.ZonaID
        JOIN Zona z2 ON i.ZonaDestinoID = z2.ZonaID
        ORDER BY i.FechaHora DESC;
    `;
    const [rows] = await pool.query(query);
    return rows;
}
/**
 * Obtiene solo los nombres de los robots para los filtros.
 * @author Mery
 * @returns {Promise<Array>}
 */
async function getRobotNames() {
    const [rows] = await pool.query('SELECT DISTINCT Nombre FROM Robot');
    return rows;
}

/**
 * Obtiene los nombres de las zonas (para Zona Actual y Destino).
 * @author Mery
 * @returns {Promise<Array>}
 */
async function getZonaNames() {
    const [rows] = await pool.query('SELECT DISTINCT Nombre FROM Zona');
    return rows;
}

/**
 * Actualiza una interacción existente con la valoración final y el comentario.
 */
async function updateInteraccion(interaccionId, valoracion, comentario) {
    const query = `
        UPDATE Interaccion 
        SET Valoracion = ?, Comentario = ? 
        WHERE InteraccionID = ?
    `;
    await pool.query(query, [valoracion, comentario, interaccionId]);
}

/**
 * Obtiene todos los eventos con el nombre del robot y su estado.
 */
async function getEventosConEstado() {
    const query = `
        SELECT e.*, r.Nombre AS RobotNombre 
        FROM Evento e
        JOIN Robot r ON e.RobotID = r.RobotID
        ORDER BY e.FechaHora DESC
    `;
    const [rows] = await pool.query(query);
    return rows;
}

/**
 * Resuelve una incidencia: Actualiza el Evento directamente sin usar tablas extra (Prototipo).
 * Añade la nota del técnico al final del mensaje original.
 */
async function resolverEvento(eventoId, tecnicoId, accion) {
    // Texto que se añadirá al mensaje existente en la base de datos
    const notaResolucion = `\n\n[Resuelto por Técnico ${tecnicoId}]: ${accion}`;

    const query = `
        UPDATE Evento 
        SET Estado = 'Cerrado', 
            CerradaEn = NOW(),
            Mensaje = CONCAT(Mensaje, ?)
        WHERE EventoID = ?
    `;
    
    await pool.query(query, [notaResolucion, eventoId]);
}

module.exports = {
    pool,
    getZonas,
    getRobots,
    getEventos,
    logConnectionEvent,
    insertPosition,
    getZonaById,
    getAllZonas,
    validarCredenciales,
    insertInteraccion,
    getInteracciones,
    getRobotNames,
    getZonaNames,
    updateInteraccion,
    getEventosConEstado,
    resolverEvento      
};
