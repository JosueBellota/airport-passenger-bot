import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from flask import Flask, Response

# Configuración de Flask
app = Flask(__name__)
bridge = CvBridge()

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # El topic que activamos con el bridge
            self.listener_callback,
            10)
        self.current_frame = None

    def listener_callback(self, data):
        # Convertimos el mensaje de ROS a una imagen de OpenCV
        self.current_frame = bridge.imgmsg_to_cv2(data, "bgr8")

# Instancia global del nodo
rclpy.init()
camera_node = CameraSubscriber()

def generate_frames():
    while True:
        # Si el nodo ha recibido una imagen
        if camera_node.current_frame is not None:
            # Codificamos la imagen como JPG
            ret, buffer = cv2.imencode('.jpg', camera_node.current_frame)
            frame = buffer.tobytes()
            # Formato necesario para streaming MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Procesamos un poco de ROS para que no se bloquee
        rclpy.spin_once(camera_node, timeout_sec=0.01)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Ejecutamos Flask en el puerto 5000
    app.run(host='0.0.0.0', port=5000, threaded=True)