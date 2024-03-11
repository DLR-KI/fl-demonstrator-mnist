#!/bin/bash
###############################################################################
# Create Training #
###################
# This script creates a training via http(s) post request on the Ferderated
# Learning Demonstrator plattform.
###############################################################################
set -o pipefail

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# parse arguments
parse_arguments "$@"

# check (and archive) previous creations
mkdir -p ./responses
if jq empty ./responses/training.json 2> /dev/null; then
  id="$(jq -r ".training_id" ./responses/training.json)"
  info "A training was already created last time (ID: $id)"
  if [ "$FORCE_ACTION" = "false" ]; then
    read -pr "Do you want to create a training again? (y/N) " confirm
    case $confirm in
      [Yy]* ) ;;
      *     ) exit 0 ;;
    esac
  fi
  mkdir -p ./responses/archive
  mv ./responses/training.json "./responses/archive/training-$(date "+%Y%m%d-%H%M%S").json"
fi

# search for all clients
clients="$(jq -r '.[] | with_entries(select(.key|match("client";"i")))[]' ./responses/participants.json 2> /dev/null)"
clients="$(echo "$clients" | jq -Rn '[inputs]')"
if [ "$clients" == "" ]; then
  fatal "no local created participants found (no client ids available)"
fi
info "clients: $clients"

# create
info "create training ..."
model_id="$(jq -r ".model_id" ./responses/model.json)"
if [ "$model_id" == "" ]; then
  fatal "no local created model found (no model id available)"
fi
info "  model found (id='${model_id}')"
http_code=$(curl -sS -X POST "${DEMONSTRATOR_BASE_URL}/api/trainings/" \
  -u "mnist-client-01:mnist-secret" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -o "./responses/training.json" \
  -w "%{http_code}" \
  --data-binary @- << EOF
{
  "model_id": "$model_id",
  "target_num_updates": 3,
  "metric_names": ["accuracy", "f1_score"],
  "aggregation_method": "FedAvg",
  "clients": $clients
}
EOF
)
if [ "$http_code" = "201" ]; then
  id="$(jq -r ".training_id" ./responses/training.json)"
  info -e "... \e[0;32m${id}\e[0m"
else
  info -e "... \e[0;31mfailed\e[0m"
  error "http response code: $http_code"
fi
