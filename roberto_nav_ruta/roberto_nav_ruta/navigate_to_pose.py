#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from math import sin, cos


"""
Nodo ROS2 para navegación directa a una pose específica usando Nav2.

Este nodo:
- Establece automáticamente la posición inicial del robot en el mapa
- Espera estabilización de AMCL 
- Navega a una única pose objetivo especificada por parámetros
- Implementa reintentos automáticos si el goal es rechazado
- Muestra feedback de distancia restante en tiempo real
- Permanece activo hasta Ctrl+C

Parámetros configurables:
- initial_x, initial_y, initial_theta: Posición INICIAL del robot
- goal_x, goal_y, goal_theta: Pose OBJETIVO final

Ejemplo:
ros2 run mi_paquete navigate_to_pose --ros-args -p initial_x:=0.0 -p goal_x:=2.0 -p goal_y:=1.5 -p goal_theta:=1.57
"""

class NavigateToPoseNode(Node):
    """
    Nodo para navegar a una pose específica usando la acción NavigateToPose de Nav2.
    """
    
    def __init__(self):
        """
        Inicializa el nodo con cliente de acción, publicador de pose inicial
        y parámetros configurables para posición inicial y objetivo.
        
        Inicia secuencia temporal automática de 2s (pose) → 8s (estabilización) → navegación.
        """
        super().__init__('navigate_to_pose')
        
        # Cliente de acción
        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
        # Publicador para posición inicial
        self.initial_pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            10
        )
        
        # Parámetros
        self.declare_parameter('goal_x', 0.5)
        self.declare_parameter('goal_y', 0.0)
        self.declare_parameter('goal_theta', 0.0)
        self.declare_parameter('initial_x', 0.0)
        self.declare_parameter('initial_y', 0.0)
        self.declare_parameter('initial_theta', 0.0)
        
        self.goal_x = self.get_parameter('goal_x').value
        self.goal_y = self.get_parameter('goal_y').value
        self.goal_theta = self.get_parameter('goal_theta').value
        self.initial_x = self.get_parameter('initial_x').value
        self.initial_y = self.get_parameter('initial_y').value
        self.initial_theta = self.get_parameter('initial_theta').value
        
        # Control de estado
        self.goal_sent = False
        self.initial_pose_sent = False
        self.retry_count = 0
        self.max_retries = 3
        
        self.get_logger().info('=' * 50)
        self.get_logger().info('Nodo NavigateToPose iniciado')
        self.get_logger().info(f'Posición inicial: ({self.initial_x}, {self.initial_y}) theta={self.initial_theta}')
        self.get_logger().info(f'Objetivo: ({self.goal_x}, {self.goal_y}) theta={self.goal_theta}')
        self.get_logger().info('=' * 50)
        
        # Timer único para inicialización
        self.init_timer = self.create_timer(2.0, self.set_initial_pose)
    
    def set_initial_pose(self):
        """
        Publica la posición inicial en /initialpose una sola vez.
        
        Usa covarianza optimizada para AMCL y programa envío del goal tras
        8 segundos de estabilización de localización.
        """
        if self.initial_pose_sent:
            return
        
        self.initial_pose_sent = True
        initial_pose = PoseWithCovarianceStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        
        initial_pose.pose.pose.position.x = self.initial_x
        initial_pose.pose.pose.position.y = self.initial_y
        initial_pose.pose.pose.position.z = 0.0
        initial_pose.pose.pose.orientation.z = sin(self.initial_theta / 2.0)
        initial_pose.pose.pose.orientation.w = cos(self.initial_theta / 2.0)
        
        initial_pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
                                        0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                        0.0, 0.0, 0.0, 0.0, 0.0, 0.25]
        
        self.initial_pose_pub.publish(initial_pose)
        self.get_logger().info('Posición inicial establecida')
        
        # Cancelar el timer de inicialización
        self.init_timer.cancel()
        
        # Esperar más tiempo para que AMCL se estabilice (8 segundos)
        self.send_timer = self.create_timer(8.0, self.send_goal)
    
    def send_goal(self):
        """
        Construye y envía el goal NavigateToPose con timeout de servidor.
        
        Convierte parámetros (x,y,theta) a PoseStamped con cuaterniones
        y configura callbacks para respuesta, resultado y feedback.
        """
        if self.goal_sent:
            return
        
        self.goal_sent = True
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = self.goal_x
        goal_msg.pose.pose.position.y = self.goal_y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.z = sin(self.goal_theta / 2.0)
        goal_msg.pose.pose.orientation.w = cos(self.goal_theta / 2.0)
        
        self.get_logger().info(f'Enviando goal a ({self.goal_x}, {self.goal_y})')
        
        # Cancelar el timer de envío
        self.send_timer.cancel()
        
        # Esperar servidor
        if not self.action_client.wait_for_server(timeout_sec=15.0):
            self.get_logger().error('Servidor /navigate_to_pose no disponible')
            return
        
        # Enviar goal
        self._send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        """
        Procesa respuesta del servidor al goal.
        
        Implementa hasta 3 reintentos automáticos cada 3s si es rechazado.
        Configura callback de resultado si es aceptado.
        """
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.retry_count += 1
                if self.retry_count <= self.max_retries:
                    self.get_logger().warn(f'Goal rechazado (intento {self.retry_count}/{self.max_retries})')
                    self.get_logger().info('Reintentando en 15 segundos...')
                    self.goal_sent = False  # Permitir reintentar
                    self.retry_timer = self.create_timer(15.0, self.send_goal)
                else:
                    self.get_logger().error(f' Goal rechazado después de {self.max_retries} intentos')
                    self.get_logger().info('Verifica que el robot esté localizado en el mapa')
                return
            
            self.get_logger().info('Goal aceptado, robot en movimiento...')
            self._get_result_future = goal_handle.get_result_async()
            self._get_result_future.add_done_callback(self.get_result_callback)
            
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
    
    def get_result_callback(self, future):
        """
        Maneja el resultado final de la navegación.
        
        Confirma llegada exitosa al objetivo y mantiene nodo activo
        para permitir nuevas navegaciones.
        """
        try:
            result = future.result().result
            self.get_logger().info('=' * 50)
            self.get_logger().info('Navegación completada exitosamente')
            self.get_logger().info(f'Llegaste al objetivo: ({self.goal_x}, {self.goal_y})')
            self.get_logger().info('=' * 50)
            self.get_logger().info('Navegación finalizada. El nodo permanece activo.')
            self.get_logger().info('Presiona Ctrl+C para cerrar')
            
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
    
    def feedback_callback(self, feedback_msg):
        """
        Muestra distancia restante al objetivo en tiempo real.
        
        Proporciona feedback continuo durante la navegación.
        """
        try:
            feedback = feedback_msg.feedback
            self.get_logger().info(f'Distancia restante: {feedback.distance_remaining:.2f} m')
        except:
            pass


def main():
    """
    Función principal que maneja inicialización ROS2, ejecución del nodo
    y shutdown limpio ante KeyboardInterrupt.
    """
    rclpy.init()
    node = NavigateToPoseNode()
    
    try:
        node.get_logger().info('Nodo ejecutándose. Esperando eventos...')
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Nodo interrumpido por el usuario')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()