#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

###############################################################################
# Create Model #
################
# This script creates a model via http(s) post request on the Ferderated
# Learning Demonstrator plattform.
###############################################################################
set -o pipefail

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# parse arguments
parse_arguments "$@"

# check (and archive) previous creations
if jq empty ./responses/model.json 2> /dev/null; then
  id="$(jq -r ".model_id" ./responses/model.json)"
  info "A model was already created last time (ID: $id)"
  if [ "$FORCE_ACTION" = "false" ]; then
    read -pr "Do you want to create the model again? (y/N) " confirm
    case $confirm in
      [Yy]* ) ;;
      *     ) exit 0 ;;
    esac
  fi
  mkdir -p ./responses/archive
  mv ./responses/model.json "./responses/archive/model-$(date "+%Y%m%d-%H%M%S").json"
fi

# create PyTorch model
if [ -f ./data/torch-model.pt ]; then
  info "A PyTorch model already exists ... skip"
else
  python ./scripts/create-torch-model-file.py
fi

# create
info -n "create model ... "
http_code=$(curl -sS -X POST "${DEMONSTRATOR_BASE_URL}/api/models/" \
  -u "mnist-client-01:mnist-secret" \
  -H "Accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -o "./responses/model.json" \
  -w "%{http_code}" \
  -F name="MNIST Model" \
  -F description="A PyTorch model for MNIST classification" \
  -F model_file=@data/torch-model.pt
)
if [ "$http_code" = "201" ]; then
  id="$(jq -r ".model_id" ./responses/model.json)"
  info2 -e "\e[0;32m${id}\e[0m"
else
  info2 -e "\e[0;31mfailed\e[0m"
  error "http response code: $http_code"
fi
