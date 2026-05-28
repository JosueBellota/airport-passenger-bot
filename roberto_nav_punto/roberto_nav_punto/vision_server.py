"""
Autor: Chris
Descripción: Servidor de Streaming de Vídeo. 
Este script actúa como un puente (Bridge) que recibe imágenes de ROS 2, 
las convierte a formato JPEG y las sirve a través de un servidor Flask 
para que puedan verse en cualquier navegador web.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from flask import Flask, Response
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

bridge = CvBridge()
camera_node = None

class CameraSubscriber(Node):
    """
    Nodo de ROS 2 que se suscribe al tópico de la cámara.
    
    Mantiene en memoria el último frame recibido para que el servidor 
    web pueda consultarlo en cualquier momento.
    """
    def __init__(self):
        """
        Inicializa el nodo y el suscriptor al flujo de imagen cruda.
        """
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
        self.current_frame = None

    def listener_callback(self, data):
        """
        Transforma la imagen de ROS a un formato compatible con OpenCV (BGR8).
        
        Args:
            data (sensor_msgs.msg.Image): Datos de la imagen de ROS.
        """
        self.current_frame = bridge.imgmsg_to_cv2(data, "bgr8")

def generate_frames():
    """
    Generador de frames para el streaming HTTP.
    
    Codifica el frame actual de OpenCV a JPEG de forma continua para 
    crear un flujo de video (MJPEG).
    
    Yields:
        bytes: Frame codificado en formato multipart/x-mixed-replace.
    """
    global camera_node
    while True:
        if camera_node is not None and camera_node.current_frame is not None:
            ret, buffer = cv2.imencode('.jpg', camera_node.current_frame)
            if ret:
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Pausa de 30ms (~30 FPS) para no congelar la CPU. 
        # ¡Y ya NO usamos spin_once aquí!
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    """
    Ruta de Flask que sirve el flujo de video.
    
    Returns:
        Response: Respuesta HTTP con el tipo de contenido multipart.
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# --- NUEVA FUNCIÓN: Mantiene a ROS 2 vivo en el fondo ---
def ros2_spin_thread():
    """
    Función encargada de mantener vivo el proceso de ROS 2.
    
    Se ejecuta en un hilo separado para que rclpy.spin() no bloquee 
    la ejecución del servidor Flask.
    """
    global camera_node
    rclpy.init()
    camera_node = CameraSubscriber()
    rclpy.spin(camera_node) # Esto se queda girando infinitamente de forma segura
    camera_node.destroy_node()
    rclpy.shutdown()

def main(args=None):
    """
    Punto de entrada principal. 
    Inicia el hilo de ROS 2 y arranca el servidor web de Flask.
    """
    # 1. Arrancamos ROS 2 en un "hilo" invisible
    ros_thread = threading.Thread(target=ros2_spin_thread, daemon=True)
    ros_thread.start()
    
    # 2. Arrancamos Flask en el frente
    print("Iniciando Servidor de Visión en el puerto 5000...")
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    main()