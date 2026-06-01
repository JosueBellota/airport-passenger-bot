"""
Lanzador de Localizacion para el Robot Roberto (Sprint 1).

Este script de lanzamiento (launch file) integra los componentes necesarios para
que el robot pueda posicionarse dentro del mapa del aeropuerto. Utiliza la pila
de navegacion Nav2 (Map Server y AMCL) y gestiona sus estados mediante el 
Lifecycle Manager.

Autor: Mery
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    """
    Genera la descripcion del lanzamiento para la pila de localizacion.
    
    Returns:
        LaunchDescription: Objeto que contiene los argumentos, parametros y nodos.
    """
    
    # 1. Declaracion de argumentos para flexibilidad en el lanzamiento
    # Permite ejecutar el sistema con o sin RViz2
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Establecer a "true" para lanzar RViz junto con la localizacion'
    )

    # 2. Configuracion de rutas de archivos de recursos y paquetes
    # Se obtienen las rutas compartidas de 'roberto_mundo' y 'roberto_nav_punto'
    pkg_mundo = get_package_share_directory('roberto_mundo')
    pkg_nav = get_package_share_directory('roberto_nav_punto')
    
    map_file = os.path.join(pkg_mundo, 'maps', 'mapadelmundo.yaml')
    amcl_config = os.path.join(pkg_nav, 'config', 'amcl_params.yaml')
    rviz_config = os.path.join(pkg_nav, 'rviz', 'localization.rviz')

    return LaunchDescription([
        use_rviz_arg,

        # Map Server 
        # Responsable de leer el archivo YAML/PGM y publicarlo en el topico /map
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'yaml_filename': map_file, 'use_sim_time': True}]
        ),

        # AMCL
        # Filtro de Particulas de Monte Carlo para localizacion global
        # Utiliza los parametros configurados en config/amcl_params.yaml
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[amcl_config, {'use_sim_time': True}]
        ),

        # Lifecycle Manager 
        # Gestor de estados de Nav2: Se asegura de que map_server y amcl 
        # pasen a estado 'Active' automaticamente al arrancar.
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server', 'amcl']
            }]
        ),
        
        # --- NODO NUEVO: Seguidor de Metas de la Web ---
        # Este nodo traduce el /goal_pose enviado desde la web a comandos /cmd_vel
        Node(
            package='roberto_nav_punto',
            executable='simple_follower.py',
            name='simple_follower',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),

        # --- NODO NUEVO: Servidor de Visión (Cámara para Dashboard) ---
        # Este nodo levanta Flask en el puerto 5000 enviando el video web
        Node(
            package='roberto_nav_punto',
            executable='vision_server', 
            name='vision_server_node',
            output='screen'
        ),

        # RViz (Visualizacion opcional)
        # Solo se lanza si el argumento use_rviz es True. 
        # Carga la configuracion personalizada desde el directorio rviz/
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            parameters=[{'use_sim_time': True}]
        )
    ])