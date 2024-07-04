#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

###############################################################################
# Start TensorBoard #
#####################
# Start the tensorboard for the last training.
###############################################################################

# imports
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

training_id="$(jq -r ".training_id" ./responses/training.json)"
info "Starting TensorBoard for training '${training_id}'"

S3_ENDPOINT=http://localhost:9000 \
  AWS_ACCESS_KEY_ID=admin \
  AWS_SECRET_ACCESS_KEY=password \
  tensorboard --logdir="s3://trainings/${training_id}"
