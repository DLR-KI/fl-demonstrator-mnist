# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

FROM ghcr.io/dlr-ki/fl-demonstrator-client:main
#FROM local/fl-demonstrator-client:latest

# install system dependencies
USER root
RUN apt-get update && \
    # git dependencies
    apt-get install -y git && \
    # cleaning up unused files
    rm -rf /var/lib/apt/lists/*
USER client

# install app dependencies (only)
COPY --chown=client:client pyproject.toml README.md /home/client/app/
RUN mkdir -p src && \
    pip install --no-warn-script-location . && \
    rm -rf src

# install app (training code)
COPY --chown=client:client ./src /home/client/app/src
RUN pip install --no-warn-script-location . && \
    rm -rf pyproject.toml README.md

# settings
ENV FL_DEMONSTRATOR_BASE_URL=http://web:8000
ENV FL_CLIENT_SETTINGS_MODULE=settings.Settings
ENV FL_CLIENT_ADDITIONAL_SYS_PATH=/home/client/app:/home/client/app/src
