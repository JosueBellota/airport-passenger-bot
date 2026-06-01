import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

class ObstacleDetectionNode(Node):
    """
    Nodo ROS2 para detección de obstáculos usando LiDAR.

    Este nodo:
    - Se suscribe a '/scan'.
    - Detecta obstáculos usando distancia mínima.
    - Publica un STRING en '/obstacle_detected'.

    Estrategia:
    - Filtra valores infinitos.
    - Usa la distancia mínima para detección rápida.

    Autor: Christopher Yoris, Maria Algora
    """

    def __init__(self):
        super().__init__('obstacle_detection_node')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.publisher = self.create_publisher(String, '/obstacle_detected', 10)

        self.threshold = 0.2
        self.get_logger().info('Obstacle Detection Node started')

    def scan_callback(self, msg):
        valid_ranges = [r for r in msg.ranges if r != float('inf')]

        if not valid_ranges:
            return

        min_distance = min(valid_ranges)

        msg_out = String()

        if min_distance < self.threshold:
            self.get_logger().warn(
                f'⚠️ Obstacle detected at {min_distance:.2f} m'
            )
            msg_out.data = "DANGER"

        else:
            self.get_logger().info(
                f'Clear path: {min_distance:.2f} m'
            )
            msg_out.data = "CLEAR"

        self.publisher.publish(msg_out)

def main(args=None):
    """
    Inicializa ROS, ejecuta el nodo y maneja el cierre seguro.
    """
    rclpy.init(args=args)
    node = ObstacleDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()