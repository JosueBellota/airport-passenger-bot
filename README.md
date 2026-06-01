# Proyecto Robótica – Roberto (Airport Passenger Bot)

## Descripción

Este proyecto utiliza **ROS 2 Jazzy Jalisco** para crear un robot guía para aeropuertos denominado "Roberto". Implementa navegación autónoma, evasión de obstáculos mediante LiDAR, visión artificial para seguimiento de personas y una interfaz web de control.

**Autores:** Maria Algora, Meryame Ait Boumlik, Christopher Yoris, Josué Bellota.

---

## Estructura del Proyecto (Linux Workspace)

El proyecto está organizado en paquetes de ROS 2 dentro del espacio de trabajo `josuebellota-airport-passenger-bot`:

```text
josuebellota-airport-passenger-bot/
├── roberto/                  # Metapaquete (scripts de ejecución rápida)
├── roberto_gesture_detection/# Detección de gestos para llamar al robot
├── roberto_lidar/            # Detección y evasión de obstáculos con LiDAR
├── roberto_mundo/            # Entornos de simulación Gazebo, mundos y modelos (C++)
├── roberto_nav_punto/        # Localización, seguimiento simple y vision_server
├── roberto_nav_ruta/         # Navegación Nav2 con waypoints y rutas
├── roberto_person_detection/ # Detección de personas mediante visión
└── web_roberto/              # Backend (Node.js) y Frontend de la interfaz de usuario
```

---

## Requisitos e Instalación

### 1. Requisitos del Sistema
* **SO:** Ubuntu 24.04 LTS (Noble Numbat)
* **ROS 2:** Jazzy Jalisco
* **Dependencias:** Python ≥ 3.12, Node.js, Gazebo Sim, ROS 2 Bridge.

### 2. Compilación e Instalación Limpia
Desde la raíz de tu workspace de ROS 2:
```bash
# Limpiar e instalar/compilar paquetes específicos (ejemplo roberto_nav_punto)
cd ~/josuebellota-airport-passenger-bot
rm -rf build/ install/ log/
colcon build --symlink-install
source install/setup.bash
```

### 3. Configuración del Entorno Virtual (Facial/Backend)
Para evitar conflictos de librerías, el componente de visión requiere un entorno virtual:
```bash
cd web_roberto/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install opencv-python cvbridge3 rclpy flask
```

### 4. Servidor Web
```bash
cd web_roberto
npm install
npm start
```

---

## Guía de Uso (Ejecución por Terminales)

Sigue este orden para iniciar el sistema completo en la simulación:

### 🎥 Terminal 1: Simulador Gazebo
Carga el mundo del aeropuerto y los sensores de Roberto.
```bash
source install/setup.bash
export DISPLAY=:0
export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch roberto_mundo roberto.launch.py
```

### 🔗 Terminal 2: GZ ↔ ROS 2 Bridge
Habilita el flujo de la cámara hacia ROS 2.
```bash
ros2 run ros_gz_bridge parameter_bridge /camera/image_raw/compressed@sensor_msgs/msg/CompressedImage[gz.msgs.Image --ros-args -r /camera/image_raw/compressed:=/camera/image_raw/compressed
```

### 📺 Terminal 3: Visor de Imagen (rqt)
Para monitorear el feed de video (necesario para activar el flujo).
```bash
export ROS_DISABLE_SHM=1
ros2 run rqt_image_view rqt_image_view
# Seleccionar: /camera/image_raw/compressed
```

### 📸 Terminal 4: Vision Server (Flask)
Servidor de streaming para la interfaz web.
```bash
export ROS_DISABLE_SHM=1
source install/setup.bash
ros2 run roberto_nav_punto vision_server
```

### 🕸️ Terminal 5: Rosbridge (WebSockets)
Comunicación entre el Frontend web y ROS 2.
```bash
source install/setup.bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### 🤖 Terminal 6: Seguimiento y Lógica
Activa el nodo de seguimiento o navegación activa.
```bash
source install/setup.bash
ros2 run roberto_nav_punto simple_follower
```

---

## Diagnóstico y Herramientas
* **Listar tópicos:** `ros2 topic list`
* **Ver nodos:** `ros2 node list`
* **Eco de cámara:** `ros2 topic echo /camera/image_raw/compressed`

---
*Nota: Este README ha sido consolidado para reflejar la estructura y comandos validados en el entorno de desarrollo Linux (WSL/VM).*
