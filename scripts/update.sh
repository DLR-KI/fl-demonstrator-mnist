#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

###############################################################################
# Update Dependencies #
#######################
# This script updates:
# - the local git repository
###############################################################################

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "update local git repository"
git fetch
git pull

info "update server components"
docker compose -f docker-compose.server.yml pull
docker compose -f docker-compose.server.yml build

info "update client components"
docker pull ghcr.io/dlr-ki/fl-demonstrator-client:main
docker compose pull
docker compose build
