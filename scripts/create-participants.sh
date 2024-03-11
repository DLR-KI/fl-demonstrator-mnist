#!/bin/bash
###############################################################################
# Create Participants #
#######################
# This script creates multiple participants via http(s) post request on the
# Ferderated Learning Demonstrator plattform.
# There will be a single actor who is also is client and multiple other client
# user.
###############################################################################
set -o pipefail

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# parse arguments
parse_arguments "$@"

# check (and archive) previous creations
mkdir -p ./responses/participants
if jq empty ./responses/participants.json 2> /dev/null; then
  client_num="$(find ./responses/participants/client-*.json | wc -l)"
  info "There were already $client_num participants created last time"
  if [ "$FORCE_ACTION" = "false" ]; then
    read -pr "Do you want to create the participants again? (y/N) " confirm
    case $confirm in
      [Yy]* ) ;;
      *     ) exit 0 ;;
    esac
  fi
  mkdir -p ./responses/archive/participants
  d="$(date "+%Y%m%d-%H%M%S")"
  mv ./responses/participants.json "./responses/archive/participants-$d.json"
  mv ./responses/participants.env "./responses/archive/participants-$d.env"
  for c in ./responses/participants/client-*.json; do
    f="$(basename "$c")"
    mv "$c" "./responses/archive/participants/${f%.*}-$d.${f##*.}"
  done
fi

echo "[" > ./responses/participants.json
echo -n "" > ./responses/participants.env
for num in $(seq "$CLIENT_NUM"); do
  n="$(printf %02d "$num")"
  if [ "$num" = "1" ]; then
    actor=true
    info -n "create actor (client $n) ... "
  else
    actor=false
    info -n "create client $n ... "
  fi

  http_code=$(curl -sS -X POST "${DEMONSTRATOR_BASE_URL}/api/users/" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -o "./responses/participants/client-$n.json" \
    -w "%{http_code}" \
    --data-binary @- << EOF
{
  "message_endpoint": "http://client-$n:8101/",
  "actor": $actor,
  "client": true,
  "username": "mnist-client-$n",
  "first_name": "MNIST",
  "last_name": "Client $n",
  "email": "mnist.client-$n@example.com",
  "password": "mnist-secret"
}
EOF
)

  if [ "$http_code" = "201" ]; then
    id="$(jq -r ".id" "./responses/participants/client-$n.json")"
    info2 -e "\e[0;32m${id}\e[0m"
    echo -n "  { \"client-$n\": \"$id\" }" >> ./responses/participants.json
    echo "CLIENT_$n=$id" >> ./responses/participants.env
  else
    echo -n "  { \"client-$n\": null }" >> ./responses/participants.json
    echo "CLIENT_$n=" >> ./responses/participants.env
    info2 -e "\e[0;31mfailed\e[0m"
    error "http response code: $http_code"
  fi
  if [ "$num" = "$CLIENT_NUM" ]; then
    echo "" >> ./responses/participants.json
  else
    echo "," >> ./responses/participants.json
  fi
done
echo "]" >> ./responses/participants.json
