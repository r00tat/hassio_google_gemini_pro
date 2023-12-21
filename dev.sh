#!/bin/bash
# setup dev environemnt
set -eo pipefail

if [[ ! -d "bin" || ! -f "bin/activate" ]]; then
  python3 -m venv .
  source bin/activate
  pip3 install -r requirements.txt
fi

if [[ ! -d "config/custom_components" ]]; then
  mkdir -p config/custom_components/
fi

COMPONENT_NAME="gemini"
CONTAINER_NAME="homeassistant-${COMPONENT_NAME}"

rsync -avz "custom_components/${COMPONENT_NAME}/" "config/custom_components/${COMPONENT_NAME}/"

if [ ! "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
  docker run -d \
    --name $CONTAINER_NAME \
    --privileged \
    --restart=unless-stopped \
    -e TZ=Europe/Vienna \
    -v $PWD/config:/config \
    -v /run/dbus:/run/dbus:ro \
    -p 8123:8123 \
    ghcr.io/home-assistant/home-assistant:stable

else
  docker restart $CONTAINER_NAME
fi
docker logs -n 10 -f $CONTAINER_NAME
