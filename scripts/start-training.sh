#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

###############################################################################
# Create Training #
###################
# This script creates a training via http(s) post request on the Ferderated
# Learning Demonstrator plattform.
###############################################################################

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# parse arguments
parse_arguments "$@"

# check (and archive) previous creations
mkdir -p ./responses
if [ -f ./responses/training-start.json ]; then
  mkdir -p ./responses/archive
  mv ./responses/training-start.json "./responses/archive/training-start-$(date "+%Y%m%d-%H%M%S").json"
fi

# request training start
info -n "start training ... "
training_id="$(jq -r ".training_id" ./responses/training.json)"
if [ "$training_id" == "" ]; then
  info -e "... \e[0;31mfailed\e[0m"
  fatal "no local created training found (no training id available)"
fi
info2 -n "id='${training_id}' ... "
http_code=$(curl -sS -X POST "${DEMONSTRATOR_BASE_URL}/api/trainings/${training_id}/start/" \
  -u "mnist-client-01:mnist-secret" \
  -H "Accept: application/json" \
  -o "./responses/training-start.json" \
  -w "%{http_code}"
)
if [ "$http_code" = "202" ]; then
  info2 -e "\e[0;32mstarted\e[0m"
else
  info2 -e "\e[0;31mfailed\e[0m"
  error "http response code: $http_code"
fi
