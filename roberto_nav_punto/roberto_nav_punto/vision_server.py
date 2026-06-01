import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import os
import subprocess

class StreamRawExtractorNode(Node):
    def __init__(self):
        super().__init__('vision_server')
        self.bridge = CvBridge()
        
        # Directorio de destino definitivo
        self.output_dir = '/root/ROS2/Roberto/roberto_nav_punto/capturas'
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = os.path.join(self.output_dir, 'live_raw_frame.jpg')
        
        # Suscripción directa al tópico crudo de la imagen
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.get_logger().info('=== EXTRACTOR CRUDO /CAMERA/IMAGE_RAW ACTIVO ===')

    def is_rqt_image_view_running(self):
        """Comprueba si rqt_image_view está activo."""
        try:
            output = subprocess.check_output(['pgrep', '-f', 'rqt_image_view'])
            return len(output) > 0
        except subprocess.CalledProcessError:
            return False

    def image_callback(self, msg):
        # Condición solicitada: rqt_image_view debe estar ejecutándose
        if not self.is_rqt_image_view_running():
            return

        try:
            # MANEJO DE ERRORES DIRECTO: 
            # Convertimos usando 'passthrough' para extraer la matriz exacta que tiene el tópico
            # sin forzar conversiones de color (bgr8/rgb8) que hagan saltar las aserciones de OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            
            if cv_image is None:
                return

            # Si la imagen viene en escala de grises o formato nativo de simulación,
            # lo volcamos directamente al disco duro sobreescribiendo el archivo.
            success = cv2.imwrite(self.output_path, cv_image)
            if success:
                self.get_logger().info('📸 [VOLCADO DIRECTO]: Frame guardado desde el tópico de la cámara.')

        except Exception as e:
            # Si ocurre cualquier anomalía física con el buffer de bytes, se ignora de forma segura
            return

def main(args=None):
    rclpy.init(args=args)
    node = StreamRawExtractorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
