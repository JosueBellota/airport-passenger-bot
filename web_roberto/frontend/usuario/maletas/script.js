// ================================
// CONEXIÓN A ROS 2 (rosbridge)
// ================================

// Establece conexión WebSocket con ROS mediante rosbridge_server
const ros = new ROSLIB.Ros({
    url: "ws://localhost:9090" // Cambiar por la IP del robot si es necesario
});

// Evento: conexión establecida correctamente
ros.on('connection', () => {
    console.log("Conectado a ROS");
});

// Evento: error en la conexión
ros.on('error', (error) => {
    console.error("Error en la conexión ROS:", error);
});

// Evento: conexión cerrada
ros.on('close', () => {
    console.log("Conexión con ROS cerrada");
});


// ================================
// TOPIC DE NAVEGACIÓN
// ================================

// Topic usado para indicar la confirmación de inicio de navegación
const navTopic = new ROSLIB.Topic({
    ros: ros,
    name: "/navigation_confirmed",
    messageType: "std_msgs/Bool"
});


// ================================
// ACCIÓN: CANCELAR
// ================================

/**
 * Cancela el proceso actual de preparación.
 * Redirige al usuario a la pantalla de selección de idioma.
 */
function cancelAction() {
    window.location.href = "../index.html";
}


// ================================
// ACCIÓN: CONTINUAR / CONFIRMAR
// ================================

/**
 * Confirma la intención de iniciar la navegación.
 *
 * Flujo de ejecución:
 * 1. Publica un mensaje booleano en ROS 2 indicando confirmación
 * 2. Redirige a la pantalla de navegación (navigation.html)
 */
function continueAction() {

    // Mensaje de confirmación de navegación
    const msg = new ROSLIB.Message({
        data: true
    });

    // Publicación en el topic ROS 2
    navTopic.publish(msg);

    console.log("Navegación confirmada enviada a ROS");

    // Redirección a la pantalla de destino
    window.location.href = "../seleccion_destino/destination.html";
}