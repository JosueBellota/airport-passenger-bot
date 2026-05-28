import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import signal

class GestureDetector(Node):
    """
    Nodo ROS2 que detecta gestos de la mano para controlar un robot TurtleBot3.

    Funcionalidad:
    - Detecta el pulgar extendido con el resto de dedos cerrados (punio).
    - Publica comandos de velocidad al robot usando TwistStamped.
    - Visualiza en ventana pequeña el estado actual de la deteccion.

    Comportamiento:
    - Pulgar extendido + punio cerrado -> robot avanza hacia adelante.
    - Mano cerrada (punio) o sin mano -> robot se detiene.
    - La velocidad de avance es configurable mediante parametro ROS2.

    Estrategia:
    - Usa MediaPipe HandLandmarker para deteccion de landmarks de la mano.
    - Calcula distancias entre puntos clave para determinar si los dedos estan cerrados.
    - Publica comandos solo cuando hay cambio de estado para evitar spam.
    - Timer principal ejecuta el bucle de deteccion a 15 Hz.

    Autor: Maria Algora
    """

    def __init__(self):
        """
        Inicializa el nodo gestor de gestos.

        Configura:
        - Publicadores para comandos de velocidad y mensajes de gesto.
        - Parametro de velocidad ajustable en tiempo real.
        - Camara V4L2 con resolucion reducida para optimizacion.
        - Detector de manos MediaPipe con modelo preentrenado.
        - Timer para el bucle principal de procesamiento.
        - Manejador de senales para cierre gracioso.
        """
        super().__init__('gesture_detector')

        # Publicadores
        self.pub_cmd = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.pub_gesture = self.create_publisher(String, '/gesture_cmd', 10)

        # Parametros configurables (valor por defecto 0.5 m/s)
        self.declare_parameter('approach_speed', 0.5)
        self.approach_speed = self.get_parameter('approach_speed').get_parameter_value().double_value
        
        # FORZAR velocidad si es 0 o None
        if self.approach_speed <= 0:
            self.approach_speed = 0.5
            self.set_parameters([rclpy.parameter.Parameter('approach_speed', rclpy.Parameter.Type.DOUBLE, 0.5)])
            self.get_logger().warn('Velocidad invalida (0). Forzando a 0.5 m/s')

        # Configuracion de camara
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            self.get_logger().error('No se pudo abrir la camara')
            return

        # Modelo MediaPipe
        model_path = self.get_model_path()
        if not os.path.exists(model_path):
            self.get_logger().error(f'Modelo no encontrado: {model_path}')
            return

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=model_path,
                delegate=python.BaseOptions.Delegate.CPU
            ),
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        # Timer principal (15 Hz)
        self.timer = self.create_timer(0.066, self.loop)

        # Variables de estado
        self.thumb_extended = False
        self.last_thumb_state = False
        self.moving = False
        self.call_count = 0
        self.window_created = False

        # Manejo de senales
        signal.signal(signal.SIGINT, self.signal_handler)

        # Log de inicio
        self.get_logger().info('Gesture Detector iniciado correctamente')
        self.get_logger().info(f'Velocidad configurada: {self.approach_speed} m/s')
        self.get_logger().info('Pulgar extendido con puno cerrado -> Robot avanza')
        self.get_logger().info('Puno cerrado o sin mano -> Robot se detiene')

    def signal_handler(self, sig, frame):
        """
        Maneja la senal SIGINT (Ctrl+C) para detener el robot y cerrar el nodo.

        Args:
            sig: Numero de la senal recibida
            frame: Frame actual de ejecucion
        """
        self.stop_robot()
        rclpy.shutdown()

    def get_model_path(self):
        """
        Busca el archivo del modelo MediaPipe en ubicaciones predefinidas.

        Returns:
            str: Ruta absoluta al archivo del modelo o nombre por defecto si no se encuentra.
        """
        possible_paths = [
            os.path.join(os.path.expanduser('~'), 'turtlebot3_ws', 'src', 'roberto_gesture_detection', 'hand_landmarker.task'),
            'hand_landmarker.task',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return 'hand_landmarker.task'

    def is_thumb_extended_with_fist(self, hand_landmarks):
        """
        Detecta si el pulgar esta extendido y los demas dedos estan cerrados (punio).

        Utiliza landmarks de MediaPipe para calcular distancias entre puntas y bases
        de cada dedo. Umbrales empiricos determinan si cada dedo esta extendido o cerrado.

        Args:
            hand_landmarks: Lista de landmarks de la mano detectados por MediaPipe.

        Returns:
            bool: True si el pulgar esta extendido y los otros dedos cerrados, False en caso contrario.
        """
        if not hand_landmarks:
            return False

        lm = hand_landmarks[0]

        # Landmarks del pulgar
        thumb_tip = lm[4]
        thumb_mcp = lm[2]

        # Landmarks de los otros dedos
        index_tip = lm[8]
        index_mcp = lm[5]
        middle_tip = lm[12]
        middle_mcp = lm[9]
        ring_tip = lm[16]
        ring_mcp = lm[13]
        pinky_tip = lm[20]
        pinky_mcp = lm[17]

        # Verificar si el pulgar esta extendido (separado de su base)
        thumb_distance = np.sqrt((thumb_tip.x - thumb_mcp.x)**2 + (thumb_tip.y - thumb_mcp.y)**2)
        thumb_extended = thumb_distance > 0.08

        # Verificar si los otros dedos estan cerrados (punta cerca de la base)
        index_closed = np.sqrt((index_tip.x - index_mcp.x)**2 + (index_tip.y - index_mcp.y)**2) < 0.06
        middle_closed = np.sqrt((middle_tip.x - middle_mcp.x)**2 + (middle_tip.y - middle_mcp.y)**2) < 0.06
        ring_closed = np.sqrt((ring_tip.x - ring_mcp.x)**2 + (ring_tip.y - ring_mcp.y)**2) < 0.06
        pinky_closed = np.sqrt((pinky_tip.x - pinky_mcp.x)**2 + (pinky_tip.y - pinky_mcp.y)**2) < 0.06

        fingers_closed = index_closed and middle_closed and ring_closed and pinky_closed

        return thumb_extended and fingers_closed

    def start_robot(self):
        """
        Publica un comando de velocidad lineal para mover el robot hacia adelante.

        Solo actua si el robot no esta ya en movimiento. El comando incluye timestamp
        y frame_id necesario para TwistStamped.
        """
        # Asegurar que la velocidad no sea 0
        current_speed = self.get_parameter('approach_speed').get_parameter_value().double_value
        if current_speed <= 0:
            current_speed = 0.5
            self.get_logger().warn('Velocidad 0 detectada, usando 0.5 m/s')
        
        if not self.moving:
            cmd = TwistStamped()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.header.frame_id = "base_link"
            cmd.twist.linear.x = current_speed
            self.pub_cmd.publish(cmd)
            self.moving = True
            self.get_logger().info(f'Robot avanzando: {current_speed} m/s')

    def stop_robot(self):
        """
        Publica un comando de velocidad cero para detener el robot.

        Solo actua si el robot esta actualmente en movimiento.
        """
        if self.moving:
            cmd = TwistStamped()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.header.frame_id = "base_link"
            cmd.twist.linear.x = 0.0
            self.pub_cmd.publish(cmd)
            self.moving = False
            self.get_logger().info('Robot detenido')

    def create_window(self):
        """
        Crea la ventana de visualizacion OpenCV si no existe.

        Configura una ventana pequena de 400x300 pixeles para mostrar
        el estado actual de la deteccion de gestos.
        """
        if not self.window_created:
            cv2.namedWindow("Gesture", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Gesture", 400, 300)
            self.window_created = True

    def loop(self):
        """
        Bucle principal de procesamiento ejecutado por el timer (15 Hz).

        Realiza las siguientes tareas:
        1. Actualiza el parametro de velocidad en tiempo real.
        2. Captura frame de la camara.
        3. Detecta landmarks de la mano con MediaPipe.
        4. Verifica si el gesto (pulgar extendido + punio) esta presente.
        5. Publica comandos de movimiento cuando el estado del gesto cambia.
        6. Muestra informacion visual en ventana OpenCV.
        """
        # Actualizar velocidad desde parametro ROS2
        param_speed = self.get_parameter('approach_speed').get_parameter_value().double_value
        if param_speed > 0:
            self.approach_speed = param_speed
        else:
            self.approach_speed = 0.5  # Velocidad por defecto si el parametro es 0

        # Capturar frame
        ret, frame = self.cap.read()
        if not ret:
            return

        # Preprocesamiento
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Deteccion de landmarks
        try:
            results = self.landmarker.detect_for_video(
                mp_image,
                int(self.get_clock().now().nanoseconds / 1e6)
            )
        except Exception:
            return

        # Analisis del gesto
        self.thumb_extended = False
        if results.hand_landmarks:
            self.thumb_extended = self.is_thumb_extended_with_fist(results.hand_landmarks)

        # Control del robot (publicar solo en cambio de estado)
        if self.thumb_extended and not self.last_thumb_state:
            self.start_robot()
            self.call_count += 1
            gesture_msg = String()
            gesture_msg.data = "call_robot"
            self.pub_gesture.publish(gesture_msg)
            self.get_logger().info(f'Gesto detectado #{self.call_count}')

        elif not self.thumb_extended and self.last_thumb_state:
            self.stop_robot()
            gesture_msg = String()
            gesture_msg.data = "stop_robot"
            self.pub_gesture.publish(gesture_msg)

        self.last_thumb_state = self.thumb_extended

        # Visualizacion en ventana
        try:
            self.create_window()

            if self.thumb_extended:
                cv2.putText(frame, 'THUMB', (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f'MOV {self.approach_speed}', (10, 55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            elif results.hand_landmarks:
                cv2.putText(frame, 'FIST', (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, 'STOP', (10, 55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            else:
                cv2.putText(frame, 'NO HAND', (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            cv2.putText(frame, f'#{self.call_count}', (frame.shape[1]-40, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Gesture", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # Tecla ESC para salir
                self.stop_robot()
                rclpy.shutdown()
        except Exception:
            pass

    def __del__(self):
        """
        Destructor que libera recursos de camara y ventanas OpenCV.
        """
        self.stop_robot()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


def main(args=None):
    """
    Funcion principal que inicia el nodo ROS2 y ejecuta el bucle de procesamiento.

    Inicializa el sistema ROS2, crea una instancia del nodo GestureDetector,
    y mantiene el nodo en ejecucion hasta recibir una senal de interrupcion.

    Args:
        args: Argumentos de linea de comandos (opcional).
    """
    rclpy.init(args=args)
    node = GestureDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_robot()
        node.get_logger().info('Cerrando Gesture Detector...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()