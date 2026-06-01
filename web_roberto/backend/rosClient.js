/**
 * @file rosClient.js
 * @description Cliente de ROS 2 para el backend del proyecto "Roberto".
 * Gestiona la conexión con el ROS Bridge, escucha la localización (AMCL) 
 * y publica objetivos de navegación (Goals). Incluye lógica de filtrado
 * para la persistencia de telemetría en la base de datos.
 * @authors Maria, Mery, Chris
 * @version 1.0.0
 */
const ROSLIB = require('roslib');
const logica = require('./logica');

let latestPosition = { x: 0, y: 0, timestamp: new Date().toISOString() };
let lastInsertedPos = { x: 0, y: 0 }; 
let lastInsertTime = 0;
let currentGoal = null;
let rosInstance = null;
let goalTopic = null;
/**
 * Inicializa la conexión real con ROS Bridge y configura los suscriptores y publicadores.
 */
function init() {
    console.log('🔗 Conectando a ROS Bridge en ws://localhost:9090...');
    
    rosInstance = new ROSLIB.Ros({
        url: 'ws://localhost:9090'
    });

    rosInstance.on('connection', () => {
        console.log('✅ Conectado a ROS Bridge exitosamente.');
        // Registramos el evento de conexión en la base de datos
        logica.logConnectionEvent(1, 'connected').catch(e => console.error('Error loggeando conexión:', e));
    });

    rosInstance.on('error', (error) => {
        console.error('❌ Error de conexión ROS Bridge:', error);
    });

    rosInstance.on('close', () => {
        console.warn('⚠️ Conexión a ROS Bridge cerrada.');
        logica.logConnectionEvent(1, 'disconnected').catch(e => console.error('Error loggeando desconexión:', e));
    });

    // Suscripción a la pose del robot (AMCL)
    const poseTopic = new ROSLIB.Topic({
        ros: rosInstance,
        name: '/amcl_pose',
        messageType: 'geometry_msgs/msg/PoseWithCovarianceStamped'
    });

    poseTopic.subscribe((message) => {
        latestPosition.x = message.pose.pose.position.x;
        latestPosition.y = message.pose.pose.position.y;
        latestPosition.timestamp = new Date().toISOString();
        
        // Throttling para no saturar la base de datos (cada 2s o si se movió > 5cm)
        const now = Date.now();
        const dist = Math.sqrt(
            Math.pow(latestPosition.x - lastInsertedPos.x, 2) + 
            Math.pow(latestPosition.y - lastInsertedPos.y, 2)
        );

        if (now - lastInsertTime > 2000 && dist > 0.05) {
            logica.insertPosition(1, latestPosition.x, latestPosition.y);
            lastInsertedPos = { x: latestPosition.x, y: latestPosition.y };
            lastInsertTime = now;
        }
    });

    // Publicador para enviar metas al robot (Nav2)
    goalTopic = new ROSLIB.Topic({
        ros: rosInstance,
        name: '/goal_pose',
        messageType: 'geometry_msgs/msg/PoseStamped'
    });
}
/**
 * Retorna la última posición almacenada en memoria del robot.
 * @returns {object} Objeto con x, y y timestamp.
 * @author Mery
 */
function getLatestPosition() {
    return latestPosition;
}

/**
 * Retorna el objetivo de navegación actual.
 * @returns {object|null}
 * @author Mery
 */
function getCurrentGoal() {
    return currentGoal;
}
/**
 * Envía una nueva meta de navegación al robot.
 * @author Mery
 * @param {number} x - Coordenada X en el mapa de ROS.
 * @param {number} y - Coordenada Y en el mapa de ROS.
 */
function sendGoal(x, y) {
    if (!rosInstance || !goalTopic) {
        console.error("❌ Cannot send goal: ROS not connected");
        return;
    }

    currentGoal = {
        x: x,
        y: y,
        timestamp: new Date().toISOString()
    };

    const goalMessage = new ROSLIB.Message({
        header: {
            stamp: { sec: 0, nsec: 0 },
            frame_id: 'map' 
        },
        pose: {
            position: { x: x, y: y, z: 0 },
            orientation: { x: 0, y: 0, z: 0, w: 1.0 }
        }
    });

    goalTopic.publish(goalMessage);
    console.log(`🎯 Goal published to ROS: x=${x}, y=${y}`);
}

function getNavigationStatus() {
    if (!currentGoal) {
        return { active: false, arrived: false };
    }

    // Calcular distancia actual al objetivo
    const dx = currentGoal.x - latestPosition.x;
    const dy = currentGoal.y - latestPosition.y;
    const currentDistance = Math.sqrt(dx * dx + dy * dy);

    // Calcular progreso (0 a 100)
    let progress = 0;
    if (initialDistance > 0) {
        progress = 100 - ((currentDistance / initialDistance) * 100);
        progress = Math.max(0, Math.min(100, progress)); // Limitar entre 0 y 100
    }

    // Calcular ETA (Tiempo estimado) - Evita dividir por 0
    let eta = 0;
    if (currentSpeed > 0.05) { 
        eta = currentDistance / currentSpeed;
    }

    // TRIGGER DE LLEGADA (Margen de 0.15m exacto al de simple_follower.py)
    const isArrived = currentDistance <= 0.15;
    
    if (isArrived) {
        currentGoal = null; // Reseteamos la misión al llegar
    }

    return {
        active: true,
        arrived: isArrived,
        progress: Math.round(progress),
        speed: currentSpeed,
        eta_seconds: eta,
        distance_remaining: currentDistance
    };
}

module.exports = {
    init,
    getLatestPosition,
    getCurrentGoal,
    sendGoal,
    getNavigationStatus
};
