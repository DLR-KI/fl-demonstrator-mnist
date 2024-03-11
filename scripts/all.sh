#!/bin/bash
###############################################################################
# Run all scripts #
###################
# This is just a shortcut for testing purpose.
###############################################################################

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Docker cleanup"
docker volume prune -f

info "Download MNIST dataset and split it into 10 small and unique client subsets"
python ./scripts/download-and-split.py

info "Create a virtual demonstration network for all docker container"
docker network create mnist-demo
trap_add "docker network remove mnist-demo" EXIT SIGINT SIGQUIT SIGABRT SIGTERM

info "Start Federated Learning Platform"
docker compose -f docker-compose.server.yml up -d --build
trap_add "docker compose -f docker-compose.server.yml down" EXIT SIGINT SIGQUIT SIGABRT SIGTERM

info "Open Logs"
if [ "$WSL_DISTRO_NAME" = "" ]; then
  info "Start the following two command each in a seperated terminal session"
  info "  $ docker logs -f web"
  info "  $ docker logs -f celery"
else
  cmd.exe /c start wsl.exe -- docker logs -f web
  cmd.exe /c start wsl.exe -- docker logs -f celery
fi
read -rsp $'Press enter to continue...\n'

info "Create FL Demonstrator actor, clients and training"
./scripts/create-participants.sh -f
./scripts/create-model.sh -f
./scripts/create-training.sh -f

info "Build as well as start clients and be ready to train"
docker compose --env-file ./responses/participants.env up -d --build
trap_add "docker compose down" EXIT SIGINT SIGQUIT SIGABRT SIGTERM
sleep 1

info "Start training via FL Demonstrator"
./scripts/start-training.sh

info "See client logs (client-01)"
docker logs -f client-01
