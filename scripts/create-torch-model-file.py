#!/usr/bin/env python

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import os
import torch


if __name__ == "__main__":
    model = torch.nn.Sequential(
        torch.nn.Conv2d(1, 32, 3),
        torch.nn.ReLU(),
        torch.nn.Conv2d(32, 64, 3),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Flatten(),
        torch.nn.Dropout(0.25),
        torch.nn.Linear(9216, 128),
        torch.nn.ReLU(),
        torch.nn.Dropout(),
        torch.nn.Linear(128, 10),
    )
    # Federated Learning Demonstrator supports normal PyTorch models (torch.nn.Module) and TorchScript models
    os.makedirs("./data", exist_ok=True)
    torch.jit.save(torch.jit.script(model), "./data/torch-model.pt")
    print("[\x1b[0;32mINFO\x1b[0m]  PyTorch model saved.")
