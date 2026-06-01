import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
from flask import Flask, Response
import threading

# Configuración de la aplicación Flask
app = Flask(__name__)
latest_frame = None
frame_lock = threading.Lock()

def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            # Codificamos la matriz de la imagen a formato binario JPEG
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            
        # Construimos el chunk HTTP multiparte para streaming continuo (MJPEG)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

class WebVideoServerNode(Node):
    def __init__(self):
        super().__init__('web_video_server_node')
        self.bridge = CvBridge()
        
        # Suscribirse al tópico de la cámara del robot (Ajusta el nombre si usas uno diferente)
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.get_logger().info('Servidor Web de Vídeo ROS 2 inicializado.')

    def image_callback(self, msg):
        global latest_frame
        try:
            # Convertimos el mensaje de imagen ROS a una matriz BGR compatible con OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            with frame_lock:
                latest_frame = cv_image
        except Exception as e:
            self.get_logger().error(f'Error al decodificar imagen de la cámara: {str(e)}')

def run_flask():
    # Arranca Flask en el puerto 5000 escuchando en todas las interfaces de red locales de WSL
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

def main(args=None):
    rclpy.init(args=args)
    node = WebVideoServerNode()
    
    # Ejecutamos Flask en un hilo independiente para que no bloquee el "spin" de ROS 2
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
