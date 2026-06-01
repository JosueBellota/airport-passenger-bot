#!/usr/bin/env python3
import os
import sys

# --- INYECCIÓN DINÁMICA DEL ENTORNO VIRTUAL ---
# Calculamos la ruta absoluta hacia el venv de facial_app de forma robusta
ROOT_WORKSPACE = os.path.expanduser('~/ROS2/Roberto')
VENV_SITE_PACKAGES = os.path.join(ROOT_WORKSPACE, 'web_roberto/backend/facial_app/venv/lib/python3.12/site-packages')

# Insertamos el venv al inicio del PATH de Python para dar prioridad a sus paquetes (TensorFlow, OpenCV, Flask)
if os.path.exists(VENV_SITE_PACKAGES):
    sys.path.insert(0, VENV_SITE_PACKAGES)

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, Response
from flask_cors import CORS
import threading
import time

# --- CONFIGURACIÓN DE RUTAS ---
MODELS_DIR = os.path.join(ROOT_WORKSPACE, 'web_roberto/backend/facial_app/models')
PROTO_PATH = os.path.join(MODELS_DIR, 'deploy.prototxt')
CAFFE_PATH = os.path.join(MODELS_DIR, 'res10_300x300_ssd_iter_140000.caffemodel')
MODEL_PATH = os.path.join(MODELS_DIR, 'face_classifier.h5')

app = Flask(__name__)
CORS(app)

class FaceVisionNode(Node):
    """
    Nodo de ROS 2 que integra:
    1. Suscripción a cámara (trasera).
    2. Detección de caras con OpenCV DNN.
    3. Seguimiento (Tracking) reactivo vía /cmd_vel.
    4. Streaming de video procesado vía Flask.
    """
    def __init__(self):
        super().__init__('face_vision_node')
        
        # Suscripción a la cámara trasera (configurada en el URDF/SDF)
        self.subscription = self.create_subscription(
            Image,
            '/camera_back/image_raw',
            self.listener_callback,
            10)
        
        # Publicador de comandos de velocidad
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.bridge = CvBridge()
        self.current_frame = None
        self.processed_frame = None
        
        # Cargar Modelos de Inteligencia Artificial
        try:
            self.face_net = cv2.dnn.readNetFromCaffe(PROTO_PATH, CAFFE_PATH)
            self.classifier = tf.keras.models.load_model(MODEL_PATH)
            self.get_logger().info(f'✅ Modelos cargados desde: {MODELS_DIR}')
        except Exception as e:
            self.get_logger().error(f'❌ Error crítico cargando modelos de IA: {str(e)}')
            self.face_net = None

        # Parámetros del Algoritmo de Seguimiento (Control Proporcional)
        self.target_center_x = 160.0    # Centro de la imagen (320/2)
        self.kp_yaw = 0.004             # Sensibilidad de giro
        self.kp_dist = 0.003            # Sensibilidad de avance/retroceso
        self.target_face_width = 80.0   # Tamaño de cara ideal (distancia deseada)
        
        self.get_logger().info('Face Vision & Tracking Node Listo.')

    def listener_callback(self, data):
        """
        Callback que procesa cada frame recibido de la cámara.
        Realiza la detección y calcula el comando de seguimiento.
        """
        frame = self.bridge.imgmsg_to_cv2(data, "bgr8")
        self.current_frame = frame
        
        if self.face_net is None:
            self.processed_frame = frame
            return

        h, w = frame.shape[:2]
        # Preprocesar imagen para el detector Caffe
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_net.setInput(blob)
        detections = self.face_net.forward()
        
        best_face = None
        max_confidence = 0
        
        # Buscar la cara con mayor confianza
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6: # Umbral de detección
                if confidence > max_confidence:
                    max_confidence = confidence
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    best_face = (startX, startY, endX, endY)

        twist = Twist()
        if best_face:
            (startX, startY, endX, endY) = best_face
            face_w = endX - startX
            face_center_x = startX + face_w / 2.0
            
            # Dibujar en el frame para el streaming
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(frame, f"User: {max_confidence:.2f}", (startX, startY - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
            
            # --- LÓGICA DE SEGUIMIENTO (TRACKING) ---
            # 1. Error de Giro: Centrar la cara horizontalmente
            error_x = self.target_center_x - face_center_x
            twist.angular.z = error_x * self.kp_yaw
            
            # 2. Error de Distancia: Mantenerse a una distancia fija (basada en el ancho de la cara)
            error_dist = self.target_face_width - face_w
            twist.linear.x = error_dist * self.kp_dist
            
            # Saturación de velocidad por seguridad
            twist.linear.x = float(np.clip(twist.linear.x, -0.3, 0.3))
            twist.angular.z = float(np.clip(twist.angular.z, -0.7, 0.7))
            
            self.get_logger().info(f'Tracking: v={twist.linear.x:.2f}, w={twist.angular.z:.2f}', once=False)
        else:
            # No se detecta nadie: el robot se detiene
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            
        # Publicar el comando de movimiento al robot
        self.cmd_vel_pub.publish(twist)
        self.processed_frame = frame

# --- SERVIDOR FLASK PARA STREAMING ---

global_node = None

def generate_frames():
    """Generador de frames MJPEG para la web."""
    while True:
        if global_node is not None and global_node.processed_frame is not None:
            ret, buffer = cv2.imencode('.jpg', global_node.processed_frame)
            if ret:
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.05) # ~20 FPS

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def ros2_thread():
    """Hilo para mantener vivo el nodo de ROS 2."""
    global global_node
    rclpy.init()
    global_node = FaceVisionNode()
    rclpy.spin(global_node)
    global_node.destroy_node()
    rclpy.shutdown()

def main():
    # 1. Lanzar ROS 2 en un hilo de fondo
    threading.Thread(target=ros2_thread, daemon=True).start()
    
    # 2. Lanzar Flask en el hilo principal
    print("🚀 Face Vision & Tracking Server activo en http://0.0.0.0:5000/video_feed")
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    main()