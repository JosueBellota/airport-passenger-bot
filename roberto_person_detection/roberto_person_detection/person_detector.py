import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge, CvBridgeError
import cv2
import os
from rclpy.qos import qos_profile_sensor_data

"""
Autor: Mery
Sprint : 3
Descripción: Nodo de detección de personas utilizando OpenCV y Haar Cascades.
"""

class PersonDetector(Node):
    """
    Nodo de ROS 2 para la detección de personas en tiempo real utilizando OpenCV.
    
    Este nodo se suscribe a un flujo de imágenes, utiliza un clasificador Haar Cascade
    para identificar figuras humanas y publica un booleano indicando la presencia 
    de una persona.
    """
    def __init__(self):
        """
        Inicializa el nodo, configura suscriptores, publicadores y carga el modelo Haar Cascade.
        """
        super().__init__('person_detector')
        self.bridge = CvBridge()

        
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data
        )

        # Publisher 
        self.publisher = self.create_publisher(Bool, '/person_detected', 10)

        # Absolute path for ROS2 Jazzy / Ubuntu 24.04[cite: 1]
        cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_fullbody.xml'
        
        # Fallback if the system path differs
        if not os.path.exists(cascade_path):
            cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'

        self.classifier = cv2.CascadeClassifier(cascade_path)
        
        if self.classifier.empty():
            self.get_logger().error(f"Failed to load classifier from: {cascade_path}")
        else:
            self.get_logger().info(f"Classifier loaded from: {cascade_path}")

    def image_callback(self, msg):
        """
        Procesa cada frame recibido de la cámara.
        
        Convierte el mensaje de ROS a formato OpenCV, realiza la detección en escala 
        de grises y visualiza los resultados en una ventana local.

        Args:
            msg (sensor_msgs.msg.Image): Mensaje de imagen entrante desde la cámara.
        """
        try:
            # Convert ROS2 Image to OpenCV (bgr8)[cite: 2]
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        # Grayscale conversion for the Haar Cascade[cite: 1]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect people using methods from the notebooks[cite: 1]
        boxes = self.classifier.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3)
        person_detected = len(boxes) > 0

        # Draw visual feedback[cite: 1]
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Person', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Publish detection status
        out_msg = Bool()
        out_msg.data = bool(person_detected)
        self.publisher.publish(out_msg)

        # Display the result in real-time[cite: 2]
        cv2.imshow("Roberto Detection View", frame)
        cv2.waitKey(1)

def main(args=None):
    """
    Punto de entrada principal para ejecutar el nodo PersonDetector.
    """
    rclpy.init(args=args)
    node = PersonDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()