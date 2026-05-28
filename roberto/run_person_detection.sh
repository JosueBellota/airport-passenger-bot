
#!/bin/bash

echo "====================================="
echo "   DETECTOR DE PERSONAS - ROBERTO"
echo "====================================="
echo ""

read -p "¿Compilar con colcon? [y/n]: " build_opt

# =========================
# COMPILACIÓN (Opcional)
# =========================
compile_packages() {
    gnome-terminal -- bash -c "
echo 'Compilando paquetes...'

cd ~/turtlebot3_ws
colcon build --packages-select roberto_mundo roberto_person_detection
source install/setup.bash

echo 'Compilación completada'
exec bash
"
}

# =========================
# LANZAR MUNDO/SIMULACIÓN
# =========================
run_world() {
    gnome-terminal -- bash -c "
echo 'Iniciando mundo Gazebo...'

cd ~/turtlebot3_ws
source install/setup.bash
export TURTLEBOT3_MODEL=burger_cam

ros2 launch roberto_mundo roberto.launch.py

exec bash
"
}

# =========================
# CREAR HUMANO EN GAZEBO
# =========================
run_human() {
    gnome-terminal -- bash -c "
echo 'Creando humano en Gazebo...'

cd ~/turtlebot3_ws
source install/setup.bash

ros2 run ros_gz_sim create \
-world mini_terminal_final \
-file https://fuel.gazebosim.org/1.0/openrobotics/models/Standing%20person \
-name my_human \
-x 2.0 -y 0.0 -z 0.0

exec bash
"
}

# =========================
# DETECTOR DE PERSONAS
# =========================
run_person_detector() {
    gnome-terminal -- bash -c "
echo 'Iniciando Detector de Personas...'

cd ~/turtlebot3_ws
source install/setup.bash

ros2 run roberto_person_detection person_detector

exec bash
"
}

# =========================
# ECHO DEL TOPIC
# =========================
run_echo() {
    gnome-terminal -- bash -c "
echo 'Mostrando detecciones...'

cd ~/turtlebot3_ws
source install/setup.bash

ros2 topic echo /person_detected

exec bash
"
}

# =========================
# EJECUCIÓN PRINCIPAL
# =========================

case $build_opt in

y|Y)
    echo "Compilando con colcon..."
    compile_packages
    sleep 60
    
    echo "Esperando estabilización del sistema..."
    sleep 30
    
    echo "Lanzando mundo..."
    run_world
    sleep 40
    
    echo "Esperando a que Gazebo se estabilice..."
    sleep 20
    
    echo "Creando humano..."
    run_human
    sleep 15
    
    echo "Esperando a que el humano se cargue..."
    sleep 15
    
    echo "Iniciando detector..."
    run_person_detector
    sleep 15
    
    echo "Mostrando resultados..."
    sleep 5
    
    run_echo
    ;;

n|N)
    echo "Usando binarios precompilados..."
    sleep 5
    
    echo "Lanzando mundo..."
    run_world
    sleep 40
    
    echo "Esperando a que Gazebo se estabilice..."
    sleep 20
    
    echo "Creando humano..."
    run_human
    sleep 15
    
    echo "Esperando a que el humano se cargue..."
    sleep 15
    
    echo "Iniciando detector..."
    run_person_detector
    sleep 15
    
    echo "Mostrando resultados..."
    sleep 5
    
    run_echo
    ;;

*)
    echo "Opción inválida. Usa 'y' o 'n'"
    exit 1
    ;;
esac

echo "Sistema de detección lanzado"
