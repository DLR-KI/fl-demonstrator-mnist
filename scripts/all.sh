#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

###############################################################################
# Run all scripts #
###################
# This is just a shortcut for testing purpose.
###############################################################################

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Docker cleanup"
docker volume prune -f

info "Create example torch model file"
python ./scripts/create-torch-model-file.py

info "Download MNIST dataset and split it into 10 small and unique client subsets"
python ./scripts/download-and-split.py

info "Create a virtual demonstration network for all docker container"
docker network create mnist-demo
trap_add "docker network remove mnist-demo" EXIT SIGINT SIGQUIT SIGABRT SIGTERM

info "Start Federated Learning Platform"
docker compose -f docker-compose.server.yml up -d
trap_add "docker compose -f docker-compose.server.yml down" EXIT SIGINT SIGQUIT SIGABRT SIGTERM

info "Open Logs"
if [ "$WSL_DISTRO_NAME" = "" ]; then
  info "Start the following two command each in a seperated terminal session"
  info "  $ docker logs -f web"
  info "  $ docker logs -f celery"
else
  if command -v wt.exe > /dev/null 2>&1; then
    wt.exe --window 0 split-pane -p Ubuntu bash -c "docker logs -f web" \; split-pane -p Ubuntu bash -c "docker logs -f celery"
  else
    cmd.exe /c start wsl.exe -- docker logs -f web
    cmd.exe /c start wsl.exe -- docker logs -f celery
  fi
fi
read -rsp $'Press enter to continue...\n'

info "Create FL Demonstrator actor, clients and training"
./scripts/create-participants.sh -f
./scripts/create-model.sh -f
./scripts/create-training.sh -f

info "Build as well as start clients and be ready to train"
docker compose --env-file ./responses/participants.env up -d --build
trap_add "docker compose down" EXIT SIGINT SIGQUIT SIGABRT SIGTERM
# wait for the clients (end point web servers) to be ready
sleep 5

info "Start training via FL Demonstrator"
./scripts/start-training.sh

info "See client logs (client-01)"
docker logs -f client-01
