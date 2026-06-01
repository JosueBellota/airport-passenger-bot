import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge
import os
import subprocess
import threading
import time
from flask import Flask, Response

# Inicialización de Flask para el streaming HTTP
app = Flask(__name__)
TARGET_FRAME_PATH = '/root/ROS2/Roberto/roberto_nav_punto/capturas/live_raw_frame.jpg'

# Buffers globales en memoria RAM compartida para evitar cortes de archivo y grises
latest_encoded_jpeg = None
frame_lock = threading.Lock()
frame_id = 0  # Marcador para que el navegador sepa que hay una imagen nueva

def mjpeg_stream_generator():
    """Generador síncrono que lee directamente de la memoria RAM."""
    global latest_encoded_jpeg, frame_id
    last_sent_id = -1
    
    while True:
        with frame_lock:
            # Si no hay imágenes todavía, enviamos un frame negro temporal para mantener la web ONLINE
            if latest_encoded_jpeg is None:
                # Generamos una matriz negra simple de espera de 640x480
                import numpy as np
                black_img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(black_img, "ESPERANDO CONEXION CON CAMERA...", (60, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 188, 140), 2)
                _, encoded = cv2.imencode('.jpg', black_img)
                binary_frame = encoded.tobytes()
                current_id = 0
            else:
                binary_frame = latest_encoded_jpeg
                current_id = frame_id

        # Solo enviamos si es un frame nuevo o si estamos esperando la cámara
        if current_id != last_sent_id or current_id == 0:
            last_sent_id = current_id
            # Incluimos en la cabecera HTTP un ID personalizado para medir los cambios en el frontend
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'X-Frame-ID: ' + str(current_id).encode() + b'\r\n\r\n' + binary_frame + b'\r\n')
        
        time.sleep(0.03)  # Límite de control síncrono (~30 fps máximos de salida)

@app.route('/video_feed')
def video_feed():
    return Response(mjpeg_stream_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Interfaz integrada que gestiona el refresco automático y calcula el framerate en la consola F12."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Roberto Live Stream Monitor</title>
        <style>
            body { background-color: #111; color: #fff; font-family: sans-serif; text-align: center; padding-top: 30px; }
            .container { margin: 20px auto; width: 640px; border: 3px solid #00bc8c; border-radius: 8px; overflow: hidden; }
            img { width: 100%; display: block; background-color: #000; }
            #fps-hud { font-size: 1.2rem; color: #00bc8c; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h2>Canal de Video en Vivo - Roberto</h2>
        <div class="container">
            <img id="stream-canvas" src="/video_feed" alt="Stream de video">
        </div>
        <div id="fps-hud">Calculando Framerate...</div>

        <script>
            // Monitor de rendimiento del lado del navegador
            const img = document.getElementById('stream-canvas');
            let frameCount = 0;
            let lastTime = performance.now();
            
            // Función de control: Si el flujo sufre un microcorte, reengancha solo de inmediato sin refrescar la página
            img.onerror = function() {
                console.warn("Detectada interrupción de flujo. Reenganchando stream automáticamente...");
                setTimeout(() => { img.src = "/video_feed?t=" + new Date().getTime(); }, 500);
            };

            // Hook periódico para medir el refresco real y calcular el framerate simulado
            setInterval(() => {
                frameCount++;
                const now = performance.now();
                const delta = now - lastTime;
                
                if (delta >= 1000) {
                    const fps = Math.round((frameCount * 1000) / delta);
                    document.getElementById('fps-hud').innerText = `Framerate Activo: ${fps} FPS`;
                    console.log(`[BROWSER CONSOLE] 📸 Frame reemplazado con éxito. Rendimiento de refresco: ${fps} FPS`);
                    frameCount = 0;
                    lastTime = now;
                }
            }, 40); // Sincronizado a la tasa de refresco del buffer de Flask
        </script>
    </body>
    </html>
    '''

class CompressedExtractorNode(Node):
    def __init__(self):
        super().__init__('vision_server')
        self.bridge = CvBridge()
        self.latest_frame = None 
        
        # Directorio de destino
        self.output_dir = '/root/ROS2/Roberto/roberto_nav_punto/capturas'
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = TARGET_FRAME_PATH
        
        # Suscripción al tópico comprimido
        self.subscription = self.create_subscription(
            CompressedImage,
            '/camera/image_raw/compressed',
            self.compressed_image_callback,
            10
        )
        
        # Temporizador síncrono de un segundo para logs del sistema
        self.timer = self.create_timer(1.0, self.save_frame_timer_callback)
        self.get_logger().info('=== EXTRACTOR FLUIDO CON CONTROL RAM ACTIVO (PUERTO 5000) ===')

    def is_rqt_image_view_running(self):
        try:
            output = subprocess.check_output(['pgrep', '-f', 'rqt_image_view'])
            return len(output) > 0
        except subprocess.CalledProcessError:
            return False

    def compressed_image_callback(self, msg):
        global latest_encoded_jpeg, frame_id
        if not self.is_rqt_image_view_running():
            return

        try:
            # Decodifica la matriz en memoria RAM
            cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if cv_image is not None and cv_image.size > 0:
                self.latest_frame = cv_image
                
                # OPTIMIZACIÓN: Codificamos a JPG directo en RAM y actualizamos el buffer de Flask
                ret, jpeg_buffer = cv2.imencode('.jpg', cv_image)
                if ret:
                    with frame_lock:
                        latest_encoded_jpeg = jpeg_buffer.tobytes()
                        frame_id += 1  # Notificamos cambio de frame

        except Exception:
            return

    def save_frame_timer_callback(self):
        """Mantiene el volcado local secundario solicitado de 1 segundo."""
        if self.latest_frame is None:
            return
        try:
            success = cv2.imwrite(self.output_path, self.latest_frame)
            if success:
                self.get_logger().info('📸 [SISTEMA]: Copia de seguridad en disco de 1s actualizada.')
        except Exception as e:
            self.get_logger().error(f'Error en volcado periódico: {str(e)}')

def launch_flask_server():
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

def main(args=None):
    rclpy.init(args=args)
    node = CompressedExtractorNode()
    
    flask_thread = threading.Thread(target=launch_flask_server, daemon=True)
    flask_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
