import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import statistics
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
import threading

class ObstacleAvoidance(Node):
    """
    Nodo ROS2 que combina control teleoperado y evasión de obstáculos usando LiDAR.

    Funcionalidad:
    - Se suscribe a:
        * /cmd_vel_teleop → comandos del usuario
        * /scan → datos del LiDAR
        * /obstacle_detected → estado de peligro
    - Publica a /cmd_vel, priorizando avoidance sobre teleop.
    - Ajusta velocidad lineal y angular de forma suave según la distancia a obstáculos.
    - Previene teletransporte en simulación mediante publicación periódica y suavizado.

    Estrategia:
    - Usa mediana de valores LiDAR para robustez.
    - Bloquea teleop si hay peligro.
    - Timer central decide qué comando publicar a 10 Hz.
    - Suaviza cambios de velocidad para simulación realista.

    Autor: Maria Algora (adaptado con timer y suavizado)
    """

    def __init__(self):
        super().__init__('obstacle_avoidance')

        # Suscripciones
        self.subscription_estado = self.create_subscription(
            String, '/obstacle_detected', self.estado_callback, 10)
        self.subscription_lidar = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        self.subscription_teleop = self.create_subscription(
            Twist, '/cmd_vel_teleop', self.teleop_callback, 10)

        # Publicador único
        self.publicador_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        # Lock y comandos
        self.lock = threading.Lock()
        self.hay_peligro = False
        self.cmd_teleop = Twist()
        self.cmd_avoidance = Twist()
        self.cmd_actual = Twist()

        # Parámetros de control
        self.distancia_segura = 0.5
        self.distancia_lenta = 1.0
        self.velocidad_maxima = 0.3
        self.velocidad_giro_maxima = 0.5
        self.max_lin_accel = 0.1  # m/s^2 por ciclo
        self.max_ang_accel = 0.3  # rad/s por ciclo

        # Timer de publicación
        self.timer = self.create_timer(0.1, self.publicar_cmd)  # 10 Hz

    def estado_callback(self, msg: String):
        """Actualiza si hay peligro según nodo de detección"""
        self.hay_peligro = (msg.data == "DANGER")
        self.get_logger().info(f"[Estado] peligro = {self.hay_peligro}")

    def teleop_callback(self, msg: Twist):
        """Actualiza el comando teleop recibido"""
        with self.lock:
            self.cmd_teleop = msg

    def lidar_callback(self, msg: LaserScan):
        """Calcula comando de avoidance según LiDAR"""
        try:
            if not msg.ranges:
                self.get_logger().warn("LiDAR vacío")
                return

            distancias = [d if d not in (float('inf'), float('-inf')) else msg.range_max for d in msg.ranges]
            if len(distancias) < 10:
                self.get_logger().warn("Datos LiDAR insuficientes")
                return

            # Mediana frontal
            idx_frente = slice(len(distancias)//2 - 30, len(distancias)//2 + 30)
            mediana_frontal = statistics.median(distancias[idx_frente])

            # Velocidad lineal
            if mediana_frontal < self.distancia_segura:
                vel_lin = 0.0
                accion_lin = "Detenido"
            elif mediana_frontal < self.distancia_lenta:
                vel_lin = self.velocidad_maxima * ((mediana_frontal - self.distancia_segura) /
                                                   (self.distancia_lenta - self.distancia_segura))
                accion_lin = "Reduciendo"
            else:
                vel_lin = self.velocidad_maxima
                accion_lin = "Maxima"

            # Laterales: decide giro
            dist_izq = statistics.median(distancias[-30:])
            dist_der = statistics.median(distancias[:30])
            diff = dist_izq - dist_der
            vel_ang = max(-self.velocidad_giro_maxima, min(self.velocidad_giro_maxima, diff))
            accion_ang = "Izq" if vel_ang > 0 else "Der" if vel_ang < 0 else "Recto"

            # Guardar comando avoidance
            with self.lock:
                self.cmd_avoidance.linear.x = vel_lin
                self.cmd_avoidance.angular.z = vel_ang

            # Debug claro
            self.get_logger().info(
                f"[Avoidance] Frente={mediana_frontal:.2f} m | Vel={vel_lin:.2f} ({accion_lin}) | "
                f"Giro={vel_ang:.2f} ({accion_ang}) | Izq={dist_izq:.2f} m | Der={dist_der:.2f} m"
            )

        except statistics.StatisticsError as e:
            self.get_logger().error(f"Error estadístico: {e}")
        except Exception as e:
            self.get_logger().error(f"Error inesperado: {e}")

    def publicar_cmd(self):
        """Publica un comando a /cmd_vel suavizando cambios y priorizando avoidance"""
        with self.lock:
            # Selección de comando según prioridad
            objetivo = self.cmd_avoidance if self.hay_peligro else self.cmd_teleop

            # Suavizado lineal
            delta_lin = objetivo.linear.x - self.cmd_actual.linear.x
            if abs(delta_lin) > self.max_lin_accel:
                delta_lin = self.max_lin_accel if delta_lin > 0 else -self.max_lin_accel
            self.cmd_actual.linear.x += delta_lin

            # Suavizado angular
            delta_ang = objetivo.angular.z - self.cmd_actual.angular.z
            if abs(delta_ang) > self.max_ang_accel:
                delta_ang = self.max_ang_accel if delta_ang > 0 else -self.max_ang_accel
            self.cmd_actual.angular.z += delta_ang

            # Publicar
            self.publicador_cmd.publish(self.cmd_actual)

            # Debug intención
            tipo = "Avoidance" if self.hay_peligro else "Teleop"
            self.get_logger().info(
                f"[Publicando {tipo}] lin={self.cmd_actual.linear.x:.2f}, ang={self.cmd_actual.angular.z:.2f}"
            )


def main(args=None):
    rclpy.init(args=args)
    nodo = ObstacleAvoidance()
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()