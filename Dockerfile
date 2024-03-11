FROM ghcr.io/dlr-ki/fl-demonstrator-client:main

# install system dependencies
USER root
RUN apt-get update && \
    # git dependencies
    apt-get install -y git && \
    # cleaning up unused files
    rm -rf /var/lib/apt/lists/*
USER client

# install app dependencies
COPY --chown=client:client pyproject.toml README.md /home/client/app/
RUN mkdir -p dlr/fl/examples/mnist && \
    pip install --no-warn-script-location --extra-index-url https://download.pytorch.org/whl/cpu . && \
    rm -rf dlr pyproject.toml README.md

# fix pip bug
RUN pip uninstall -y fl-demonstrator-client && \
    pip install --no-warn-script-location -U git+https://mnist-example:EEKvxrARr8gDGxx9r4oW@gitlab.dlr.de/ki-cx-federatedlearning/fl-demonstrator-client.git@main

# copy training code
COPY --chown=client:client ./dlr /home/client/app/dlr

# settings
ENV FL_DEMONSTRATOR_BASE_URL=http://web:8000
ENV FL_DEMONSTRATOR_TRAINING_SCRIPT_PATH=dlr/fl/examples/mnist/main.py
ENV FL_CLIENT_SETTINGS_MODULE=dlr.fl.examples.mnist.settings.Settings
ENV FL_CLIENT_ADDITIONAL_SYS_PATH=/home/client/app:/home/client/app/dlr/fl/examples/mnist
