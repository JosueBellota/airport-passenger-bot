#!/bin/bash

echo "====================================="
echo "   DETECTOR DE GESTOS - ROBERTO"
echo "====================================="
echo ""

read -p "¿Compilar con colcon? [y/n]: " build_opt

# =========================
# INSTALAR DEPENDENCIAS
# =========================
install_dependencies() {
    gnome-terminal -- bash -c "
echo 'Instalando dependencias...'

cd ~
python3 -m venv virtualenvs/rosenv
source ~/virtualenvs/rosenv/bin/activate

echo 'Instalando mediapipe, opencv-python y numpy...'
pip install mediapipe opencv-python numpy

echo 'Verificando instalación...'
pip list | grep -E 'mediapipe|opencv|numpy'

echo 'Dependencias instaladas'
exec bash
"
}

# =========================
# DESCARGAR MODELO
# =========================
download_model() {
    gnome-terminal -- bash -c "
echo 'Descargando modelo hand_landmarker.task...'

mkdir -p ~/turtlebot3_ws/src/roberto_gesture_detection

cd ~/turtlebot3_ws/src/roberto_gesture_detection
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

echo 'Verificando descarga...'
ls -lh hand_landmarker.task

echo 'Modelo descargado'
exec bash
"
}

# =========================
# COMPILACIÓN CON COLCON
# =========================
compile_packages() {
    gnome-terminal -- bash -c "
echo 'Compilando paquete con colcon...'

cd ~/turtlebot3_ws

colcon build --packages-select roberto_gesture_detection --symlink-install

echo 'Esperando finalización de compilación...'
sleep 30

echo 'Verificando instalación...'
ls install/roberto_gesture_detection/lib/roberto_gesture_detection/

echo 'Compilación completada'
exec bash
"
}

# =========================
# DETECTOR DE GESTOS
# =========================
run_gesture_detector() {
    gnome-terminal -- bash -c "
echo 'Iniciando Gesture Detector...'

cd ~/turtlebot3_ws
source install/setup.bash
source ~/virtualenvs/rosenv/bin/activate
export PYTHONPATH=\"\$HOME/virtualenvs/rosenv/lib/python3.12/site-packages:\$PYTHONPATH\"

sleep 5

ros2 run roberto_gesture_detection gesture_detector

exec bash
"
}

# =========================
# SIMULACIÓN
# =========================
run_simulation() {
    gnome-terminal -- bash -c "
echo 'Iniciando mundo...'

cd ~/turtlebot3_ws
source install/setup.bash
export TURTLEBOT3_MODEL=burger_cam

sleep 5

ros2 launch roberto_mundo roberto.launch.py

exec bash
"
}

# =========================
# EJECUCIÓN PRINCIPAL
# =========================

case $build_opt in

y|Y)
    echo "Iniciando instalación y compilación completa..."
    sleep 3
    
    echo "Paso 1: Instalando dependencias..."
    install_dependencies
    sleep 60
    
    echo "Esperando finalización de instalación de dependencias..."
    sleep 30
    
    echo "Paso 2: Descargando modelo hand_landmarker.task..."
    download_model
    sleep 40
    
    echo "Esperando descarga del modelo..."
    sleep 20
    
    echo "Paso 3: Compilando con colcon..."
    compile_packages
    sleep 90
    
    echo "Esperando estabilización del sistema tras compilación..."
    sleep 30
    
    echo "Paso 4: Sourcing de setup.bash tras colcon..."
    sleep 10
    
    echo "Lanzando Gesture Detector..."
    run_gesture_detector
    sleep 30
    
    echo "Esperando a que el detector se inicialice..."
    sleep 20
    
    echo "Lanzando mundo de simulación..."
    run_simulation
    sleep 40
    
    echo "Esperando a que Gazebo se estabilice..."
    sleep 20
    ;;

n|N)
    echo "Usando binarios precompilados..."
    sleep 5
    
    echo "Lanzando Gesture Detector..."
    run_gesture_detector
    sleep 30
    
    echo "Esperando a que el detector se inicialice..."
    sleep 20
    
    echo "Lanzando mundo de simulación..."
    run_simulation
    sleep 40
    
    echo "Esperando a que Gazebo se estabilice..."
    sleep 20
    ;;

*)
    echo "Opción inválida. Usa 'y' o 'n'"
    exit 1
    ;;
esac

echo "Sistema de gestos completamente lanzado"
