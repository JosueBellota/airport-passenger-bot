#!/usr/bin/env python3

"""
Autor: Mery
Descripción: Nodo de seguimiento de objetivos (Goal Follower). 
Calcula la velocidad necesaria para que el robot se desplace desde su 
posición actual (AMCL) hasta el destino marcado en la web.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from geometry_msgs.msg import TwistStamped, PoseWithCovarianceStamped, PoseStamped
import math

class WebGoalFollower(Node):
    """
    Nodo encargado de la navegación reactiva.
    
    Escucha la posición del robot y el objetivo deseado, calculando errores 
    de distancia y ángulo para publicar comandos de velocidad (TwistStamped).
    """
    def __init__(self):
        """
        Inicializa el nodo, configura QoS para compatibilidad con Jazzy 
        y define suscriptores, publicadores y el bucle de control.
        """
        super().__init__('web_goal_follower')

        # --- QoS Profile for AMCL Compatibility ---
        # AMCL in Jazzy often uses Best Effort. If the subscriber is 
        # set to Reliable, it will never receive data.
        qos_amcl = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
            durability=DurabilityPolicy.VOLATILE
        )

        # Publishers
        # Gazebo Harmonic/Jazzy requires TwistStamped (with Header)
        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        
        # Subscribers
        self.create_subscription(
            PoseWithCovarianceStamped, 
            '/amcl_pose', 
            self.pose_callback, 
            qos_amcl)
        
        self.create_subscription(
            PoseStamped, 
            '/goal_pose', 
            self.goal_callback, 
            10)
        
        # State Variables
        self.current_pos = None
        self.current_yaw = 0.0
        self.goal_pos = None
        
        # Timer for the control loop (10Hz)
        self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('🚀 Web Goal Follower (TwistStamped + BestEffort QoS) Started')

    def pose_callback(self, msg):
        """ 
        Recibe la posición y orientación actual desde AMCL.
        Convierte los cuaterniones a ángulo Euler (Yaw) para facilitar los cálculos.

        Args:
            msg (PoseWithCovarianceStamped): Mensaje de pose con covarianza.
        """
        if self.current_pos is None:
            self.get_logger().info('✅ First position received! Robot is now localized.')
        
        self.current_pos = msg.pose.pose.position
        
        # Convert Quaternion to Euler Yaw (Rotation around Z axis)
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def goal_callback(self, msg):
        """ 
        Recibe el destino seleccionado desde la interfaz Web de Roberto.

        Args:
            msg (PoseStamped): Posición objetivo en el mapa.
        """
        self.goal_pos = msg.pose.position
        self.get_logger().info(f'🎯 New Web Goal: x={self.goal_pos.x:.2f}, y={self.goal_pos.y:.2f}')

    def control_loop(self):
        """
        Bucle de control principal (P-Controller).
        Calcula la distancia y el ángulo hacia el objetivo y publica /cmd_vel.
        """
        # 1. Check if we have both position and a destination
        if self.current_pos is None:
            self.get_logger().info('Waiting for /amcl_pose... (Check QoS or Initial Pose)', throttle_duration_sec=5.0)
            return
        
        if self.goal_pos is None:
            return

        # 2. Calculate Distance and Direction
        dx = self.goal_pos.x - self.current_pos.x
        dy = self.goal_pos.y - self.current_pos.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Angle from robot to goal
        angle_to_goal = math.atan2(dy, dx)
        # Difference between robot heading and goal direction
        angle_error = angle_to_goal - self.current_yaw
        
        # Normalize angle to keep it between [-pi, pi]
        while angle_error > math.pi: angle_error -= 2.0 * math.pi
        while angle_error < -math.pi: angle_error += 2.0 * math.pi

        # 3. Create the TwistStamped Message
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # 4. Simple Proportional Control Logic
        if distance > 0.15: # Stop within 15cm of target
            
            # If the robot is facing the wrong way, rotate in place first
            if abs(angle_error) > 0.6: 
                msg.twist.linear.x = 0.0
                msg.twist.angular.z = 0.5 if angle_error > 0 else -0.5
            else:
                # Face toward goal while moving forward
                msg.twist.linear.x = min(0.22, distance * 0.4) # Max speed 0.22 m/s
                msg.twist.angular.z = angle_error * 1.2        # Turning speed
            
            self.cmd_pub.publish(msg)
        else:
            # Arrival: Send 0 velocity and clear goal
            self.cmd_pub.publish(msg) 
            self.get_logger().info('✅ Destination reached. Stopping.')
            self.goal_pos = None

def main(args=None):
    """
    Punto de entrada para ejecutar el seguidor de objetivos.
    """
    rclpy.init(args=args)
    node = WebGoalFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()