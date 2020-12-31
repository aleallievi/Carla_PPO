#!/bin/bash
# change these.
CARLA_DIR=/home/boschaustin/projects/CL_AD/Carla_PPO/CARLA_9_10_1
AGENTS_DIR=/home/boschaustin/projects/CL_AD/Carla_PPO/examples/running_carla
SCRIPTS_DIR=/home/boschaustin/projects/CL_AD/Carla_PPO/scripts

export WORLD_PORT=9000
export TM_PORT=$((${WORLD_PORT}+50))

export CARLA_EGG=$(ls ${CARLA_DIR}/PythonAPI/carla/dist/*py3*)

export PYTHONPATH=$PYTHONPATH:$CARLA_EGG
export PYTHONPATH=$PYTHONPATH:$CARLA_DIR/PythonAPI/carla

#Launch CARLA server
python3 ${SCRIPTS_DIR}/launch_carla.py --world-port $WORLD_PORT --gpu 3

#Launch CARLA client
python3 ${AGENTS_DIR}/run_ppo_navigation_sync.py --world-port $WORLD_PORT --tm-port $TM_PORT
