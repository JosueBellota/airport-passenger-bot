import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from rclpy.qos import qos_profile_sensor_data
"""
Autor: Mery
Sprint : 3
Descripción: Nodo publicador de imágenes estáticas para pruebas de visión.
"""

class ImagePublisher(Node):
    """
    Nodo de ROS 2 encargado de cargar una imagen local y publicarla continuamente.
    
    Este nodo es útil para realizar pruebas de depuración (debugging) en algoritmos 
    de visión computacional sin necesidad de tener una cámara física conectada.
    """
    def __init__(self):
        """
        Inicializa el nodo 'image_publisher', carga la imagen desde el sistema 
        de archivos y configura un temporizador para la publicación.
        """
        super().__init__('image_publisher')
        self.publisher = self.create_publisher(Image, '/camera/image_raw', qos_profile_sensor_data)
        self.bridge = CvBridge()

        # Path to your test image
        image_path = '/home/mery/person.jpg' # change when needed
        
        if not os.path.exists(image_path):
            self.get_logger().error(f"File not found: {image_path}")
            self.image = None
        else:
            self.image = cv2.imread(image_path)

        # Publish at 10Hz
        self.timer = self.create_timer(0.1, self.publish_frame)
        
    def publish_frame(self):
        """
        Callback del temporizador que convierte la imagen de OpenCV a un mensaje 
        de ROS y lo publica en el tópico correspondiente.
        """
        if self.image is not None:
            msg = self.bridge.cv2_to_imgmsg(self.image, encoding='bgr8')
            self.publisher.publish(msg)

def main(args=None):
    """
    Punto de entrada para la ejecución del nodo publicador.
    """
    rclpy.init(args=args)
    node = ImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()