import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import subprocess
import time
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity

class SynchronousFollower(Node):
    def __init__(self):
        super().__init__('simple_follower')
        
        self.get_logger().info('=== INICIALIZANDO CONFIGURACIÓN INTEGRADA CON AUTOPUENTE ===')
        
        self.world_name = 'mini_terminal_final'
        
        # ---------------------------------------------------------------------
        # LANZAMIENTO DEL PUENTE DE SERVICIO (GZ <-> ROS 2)
        # ---------------------------------------------------------------------
        # Forzamos la creación del puente para el servicio set_pose nativamente
        bridge_cmd = [
            'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
            f'/world/{self.world_name}/set_pose@ros_gz_interfaces/srv/SetEntityPose'
        ]
        self.get_logger().info('Abriendo puente de comunicación para SetEntityPose...')
        self.bridge_process = subprocess.Popen(bridge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Esperamos un instante a que el proceso del puente se asiente en el sistema
        time.sleep(1.5)

        # Publicador de velocidad para Roberto
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Suscriptor a la odometría del robot
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        
        # Cliente para mover a la persona en Gazebo
        self.set_pose_client = self.create_client(SetEntityPose, f'/world/{self.world_name}/set_pose')
        
        self.get_logger().info(f'Verificando disponibilidad del canal: /world/{self.world_name}/set_pose')
        while not self.set_pose_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('El puente se está sincronizando... Reintentando enlace con Gazebo...')

        # Definición de la entidad de la persona
        self.person_entity = Entity(name='persona_prueba_bobeye', type=Entity.MODEL)
        
        # Lógica de la patrulla de la persona (Waypoints)
        self.waypoints = [[0.0, 3.5], [0.0, -3.5]]
        self.current_wp_idx = 0
        self.person_x, self.person_y = -1.5, 0.0
        self.person_speed = 0.04
        
        # Parámetros de control de seguimiento posterior
        self.target_distance = 1.8
        self.linear_k = 0.6
        self.angular_k = 2.0
        
        self.robot_x = -2.0
        self.robot_y = -0.5
        self.robot_yaw = 0.0
        
        self.log_counter = 0
        
        # Un único timer para gestionar la patrulla de la persona y el control síncrono
        self.timer = self.create_timer(0.05, self.sync_loop)
        self.get_logger().info('=== ¡SISTEMA ENLAZADO Y OPERATIVO DE FORMA SÍNCRONA! ===')

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        
        # Convertimos el cuaternión a ángulo Yaw
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    def sync_loop(self):
        self.log_counter += 1
        
        # 1. MOVER A LA PERSONA EN EL MUNDO VIA SERVICIO PUENTEADO
        target_x, target_y = self.waypoints[self.current_wp_idx]
        dx_p = target_x - self.person_x
        dy_p = target_y - self.person_y
        dist_p = math.hypot(dx_p, dy_p)

        if dist_p < 0.2:
            self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
            self.get_logger().info(f'Persona cambiando de rumbo hacia Waypoint {self.current_wp_idx}')
        else:
            person_yaw = math.atan2(dy_p, dx_p)
            self.person_x += self.person_speed * math.cos(person_yaw)
            self.person_y += self.person_speed * math.sin(person_yaw)

            req_set = SetEntityPose.Request()
            req_set.entity = self.person_entity
            req_set.pose.position.x = self.person_x
            req_set.pose.position.y = self.person_y
            req_set.pose.position.z = 0.0
            req_set.pose.orientation.z = math.sin(person_yaw / 2.0)
            req_set.pose.orientation.w = math.cos(person_yaw / 2.0)
            self.set_pose_client.call_async(req_set)

        # 2. CALCULAR SEGUIMIENTO DE ROBERTO RESPECTO A LA PERSONA
        dx = self.person_x - self.robot_x
        dy = self.person_y - self.robot_y
        distance = math.hypot(dx, dy)
        
        target_angle = math.atan2(dy, dx)
        
        # Error angular de la cámara trasera (robot_yaw - pi)
        error_angle = target_angle - self.robot_yaw - math.pi
        error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))
        
        cmd_msg = Twist()
        
        if abs(error_angle) > 0.02:
            cmd_msg.angular.z = self.angular_k * error_angle
        
        error_dist = distance - self.target_distance
        if abs(error_dist) > 0.05:
            cmd_msg.linear.x = -self.linear_k * error_dist
        
        # Límites de velocidad de seguridad por hardware simulado
        cmd_msg.linear.x = max(min(cmd_msg.linear.x, 0.4), -0.4)
        cmd_msg.angular.z = max(min(cmd_msg.angular.z, 0.8), -0.8)
        
        self.cmd_vel_pub.publish(cmd_msg)
        
        if self.log_counter % 40 == 0:
            self.get_logger().info(f'[TRACKING OK]: Objetivo a {distance:.2f}m | Guiando base trasera...')

def main(args=None):
    rclpy.init(args=args)
    node = SynchronousFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    # Al cerrar con Ctrl+C cerramos de forma limpia el puente secundario para no dejar procesos zombis
    node.get_logger().info('Cerrando procesos del nodo de navegación...')
    node.bridge_process.terminate()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
