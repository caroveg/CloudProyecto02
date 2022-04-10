#!/bin/bash
export PROJECT_BASE_DIR=/home/ubuntu/CloudProyecto02
source $PROJECT_BASE_DIR/proyecto03v/bin/activate
cd $PROJECT_BASE_DIR/
nohup python entrypoint.py 2>&1
