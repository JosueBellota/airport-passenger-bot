import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import subprocess
import time
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity

class DemoEstableEjeX(Node):
    def __init__(self):
        super().__init__('simple_follower')
        
        self.get_logger().info('=== SISTEMA INTEGRADO ANTIVUELCO Y ESTABILIZACIÓN ANGULAR ===')
        
        self.world_name = 'mini_terminal_final'
        
        bridge_cmd = [
            'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
            f'/world/{self.world_name}/set_pose@ros_gz_interfaces/srv/SetEntityPose'
        ]
        self.bridge_process = subprocess.Popen(bridge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)

        self.cmd_vel_pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.set_pose_client = self.create_client(SetEntityPose, f'/world/{self.world_name}/set_pose')
        
        while not self.set_pose_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('Conectando canales con Gazebo...')

        self.person_entity = Entity(name='persona_prueba_bobeye', type=Entity.MODEL)
        
        # Vaivén acotado en X (Plaza central)
        self.center_x = -1.0
        self.person_x = -1.0
        self.person_y = 0.0
        self.amplitude = 1.3
        
        # AJUSTE: Persona más lenta para transiciones suaves
        self.person_speed = 0.010
        self.moving_forward = True
        
        # Control optimizado para evitar volcar
        self.target_distance = 0.5
        self.linear_k = 1.8
        self.angular_k = 1.5  # Amortiguado para evitar sobre-oscilación
        
        self.robot_x = -2.0
        self.robot_y = -0.5
        self.robot_yaw = 0.0
        
        self.laser_ranges = []
        self.collision_detected = False
        
        self.state = 'ENGAGING'
        self.log_counter = 0
        
        self.timer = self.create_timer(0.05, self.sync_loop)
        self.get_logger().info('=== DEMO INICIADA: AMORTIGUACIÓN ANTIVUELCO ACTIVA ===')

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    def scan_callback(self, msg):
        self.laser_ranges = msg.ranges
        num_ranges = len(msg.ranges)
        if num_ranges == 0:
            return

        # Escaneo del arco trasero
        start_idx = int(num_ranges * 0.44)
        end_idx = int(num_ranges * 0.56)
        
        min_dist_back = float('inf')
        for i in range(start_idx, end_idx):
            dist = msg.ranges[i]
            if msg.range_min < dist < msg.range_max:
                if dist < min_dist_back:
                    min_dist_back = dist
                    
        # Filtro estricto anticolisión
        if min_dist_back < 0.45:
            self.collision_detected = True
        else:
            self.collision_detected = False

    def sync_loop(self):
        self.log_counter += 1

        # 1. GESTIÓN DEL VAIVÉN DE LA PERSONA
        if self.state == 'ENGAGING':
            person_yaw = 3.1416
        else:
            if self.moving_forward:
                self.person_x += self.person_speed
                person_yaw = 0.0
                if self.person_x >= (self.center_x + self.amplitude):
                    self.moving_forward = False
            else:
                self.person_x -= self.person_speed
                person_yaw = 3.1416
                if self.person_x <= (self.center_x - self.amplitude):
                    self.moving_forward = True

        req_set = SetEntityPose.Request()
        req_set.entity = self.person_entity
        req_set.pose.position.x = self.person_x
        req_set.pose.position.y = self.person_y
        req_set.pose.position.z = 0.0
        req_set.pose.orientation.z = math.sin(person_yaw / 2.0)
        req_set.pose.orientation.w = math.cos(person_yaw / 2.0)
        self.set_pose_client.call_async(req_set)

        # 2. ALGORITMO DE CONTROL ESTABLE
        dx = self.person_x - self.robot_x
        dy = self.person_y - self.robot_y
        distance = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)
        
        error_angle = target_angle - self.robot_yaw - math.pi
        error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))
        
        error_dist = distance - self.target_distance

        if self.state == 'ENGAGING' and abs(error_dist) < 0.08 and abs(error_angle) < 0.12:
            self.state = 'PATROLLING'
            self.get_logger().info('=== ACELERACIÓN SUAVE Y SEGURO CONECTADO ===')

        cmd_msg = TwistStamped()
        cmd_msg.header.stamp = self.get_clock().now().to_msg()
        cmd_msg.header.frame_id = 'base_footprint'

        # CONTROL DE SEGURIDAD CRÍTICO (EVITAR VOLCADURA POR GIRO BRUSCO)
        if abs(error_angle) > 0.45:
            # SI EL ERROR ANGULAR ES MUY GRANDE, EL ROBOT SE QUEDA QUIETO LINEALMENTE Y SOLO GIRA
            cmd_msg.twist.linear.x = 0.0
            cmd_msg.twist.angular.z = self.angular_k * (error_angle / abs(error_angle)) * 0.6
            if self.log_counter % 20 == 0:
                self.get_logger().warn(f'[ANTIVUELCO AGILIZADO]: Rotando sobre el eje chasis. Error: {error_angle:.2f} rad')
        elif self.collision_detected:
            # Si hay un objeto del mapa cerca
            cmd_msg.twist.linear.x = 0.0
            cmd_msg.twist.angular.z = 0.5 if error_angle > 0 else -0.5
        else:
            # Si el ángulo está controlado, aplicamos persecución lineal ágil
            if abs(error_dist) > 0.02:
                cmd_msg.twist.linear.x = -self.linear_k * error_dist
            else:
                cmd_msg.twist.linear.x = 0.0

            if abs(error_angle) > 0.03:
                cmd_msg.twist.angular.z = self.angular_k * error_angle
            else:
                cmd_msg.twist.angular.z = 0.0

        # Acotación física estricta (Límites suaves para conservar el centro de gravedad)
        cmd_msg.twist.linear.x = max(min(cmd_msg.twist.linear.x, 0.5), -0.5)
        cmd_msg.twist.angular.z = max(min(cmd_msg.twist.angular.z, 0.8), -0.8)
        
        self.cmd_vel_pub.publish(cmd_msg)
        
        if self.log_counter % 40 == 0:
            self.get_logger().info(f'[{self.state}] Dist: {distance:.2f}m | Ángulo: {error_angle:.2f} rad')

def main(args=None):
    rclpy.init(args=args)
    node = DemoEstableEjeX()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Cerrando demo...')
        node.bridge_process.terminate()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
