import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import math
import subprocess
import time
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity

class SynchronousFollower(Node):
    def __init__(self):
        super().__init__('simple_follower')
        
        self.get_logger().info('=== CONFIGURACIÓN DE ALTA VELOCIDAD Y EVITACIÓN DE COLISIONES ===')
        
        self.world_name = 'mini_terminal_final'
        
        # Lanzamiento automático del puente posicional
        bridge_cmd = [
            'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
            f'/world/{self.world_name}/set_pose@ros_gz_interfaces/srv/SetEntityPose'
        ]
        self.bridge_process = subprocess.Popen(bridge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)

        # Publicador adaptado a TwistStamped
        self.cmd_vel_pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.set_pose_client = self.create_client(SetEntityPose, f'/world/{self.world_name}/set_pose')
        
        while not self.set_pose_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('Sincronizando canales con Gazebo...')

        self.person_entity = Entity(name='persona_prueba_bobeye', type=Entity.MODEL)
        
        # Waypoints fijos de la terminal
        self.waypoints = [[0.0, 3.5], [0.0, -3.5]]
        self.current_wp_idx = 0
        self.person_x, self.person_y = -1.5, 0.0
        
        # AJUSTE: Persona más lenta para no perderla
        self.person_speed = 0.02
        
        # AJUSTE: Distancia objetivo reducida a 1 metro
        self.target_distance = 1.0
        
        # AJUSTE: Ganancias sintonizadas más altas para que el robot sea más rápido
        self.linear_k = 1.2
        self.angular_k = 3.5
        
        self.robot_x = -2.0
        self.robot_y = -0.5
        self.robot_yaw = 0.0
        
        # Estado inicial
        self.state = 'ENGAGING'
        self.log_counter = 0
        
        self.timer = self.create_timer(0.05, self.sync_loop)
        self.get_logger().info('=== [ESTADO INITIAL]: ENGAGING - ENFOCANDO Y AJUSTANDO A 1 METRO ===')

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    def sync_loop(self):
        self.log_counter += 1
        
        # Calcular vectores relativos
        dx = self.person_x - self.robot_x
        dy = self.person_y - self.robot_y
        distance = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)
        
        error_angle = target_angle - self.robot_yaw - math.pi
        error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))
        
        error_dist = distance - self.target_distance

        # Gestión de la Máquina de Estados
        if self.state == 'ENGAGING':
            person_yaw = 3.1416
            # El robot se acopla rápido a 1 metro. Tolerancia de enganche optimizada
            if abs(error_dist) < 0.10 and abs(error_angle) < 0.08:
                self.state = 'PATROLLING'
                self.get_logger().info('=== [CAMBIO DE ESTADO]: PATROLLING - DISTANCIA DE 1M FIJADA ===')
        
        elif self.state == 'PATROLLING':
            target_x, target_y = self.waypoints[self.current_wp_idx]
            dx_p = target_x - self.person_x
            dy_p = target_y - self.person_y
            dist_p = math.hypot(dx_p, dy_p)

            if dist_p < 0.2:
                self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
                self.get_logger().info(f'Persona cambiando de rumbo hacia Waypoint {self.current_wp_idx}')
            
            person_yaw = math.atan2(dy_p, dx_p)
            self.person_x += self.person_speed * math.cos(person_yaw)
            self.person_y += self.person_speed * math.sin(person_yaw)

        # Enviar actualización de la persona
        req_set = SetEntityPose.Request()
        req_set.entity = self.person_entity
        req_set.pose.position.x = self.person_x
        req_set.pose.position.y = self.person_y
        req_set.pose.position.z = 0.0
        req_set.pose.orientation.z = math.sin(person_yaw / 2.0)
        req_set.pose.orientation.w = math.cos(person_yaw / 2.0)
        self.set_pose_client.call_async(req_set)

        # CONSTRUCCIÓN DE VELOCIDAD CON CONTROL ANTICOLISIÓN MAP LOCAL
        cmd_msg = TwistStamped()
        cmd_msg.header.stamp = self.get_clock().now().to_msg()
        cmd_msg.header.frame_id = 'base_footprint'
        
        # El giro es prioritario para mantener la cabeza en la cámara siempre
        if abs(error_angle) > 0.02:
            cmd_msg.twist.angular.z = self.angular_k * error_angle
            
        if abs(error_dist) > 0.04:
            cmd_msg.twist.linear.x = -self.linear_k * error_dist

        # Lógica preventiva de colisión (Límites estructurales de los cuartos de la terminal)
        # Si el robot retrocede hacia los muros norte/sur de las habitaciones (Y > 3.8 o Y < -3.8 o X < -3.8)
        if cmd_msg.twist.linear.x < 0: # Si va marcha atrás
            if self.robot_x < -3.6 or self.robot_y > 3.6 or self.robot_y < -3.6:
                self.get_logger().warn('[COLISIÓN PREVENIDA]: Muro detectado cerca de la base posterior.')
                cmd_msg.twist.linear.x = 0.0 # Congela el avance lineal para proteger el robot pero mantiene el giro

        # Límites dinámicos elevados (Robot más rápido)
        cmd_msg.twist.linear.x = max(min(cmd_msg.twist.linear.x, 0.7), -0.7)
        cmd_msg.twist.angular.z = max(min(cmd_msg.twist.angular.z, 1.5), -1.5)
        
        self.cmd_vel_pub.publish(cmd_msg)
        
        if self.log_counter % 40 == 0:
            self.get_logger().info(f'[{self.state}] Distancia Real: {distance:.2f}m | Giro de Cámara: {error_angle:.2f} rad')

def main(args=None):
    rclpy.init(args=args)
    node = SynchronousFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Terminando procesos de navegación...')
        node.bridge_process.terminate()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
