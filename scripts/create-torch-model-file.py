#!/usr/bin/env python
import pickle
import torch


if __name__ == "__main__":
    model = torch.nn.Sequential(
        torch.nn.Conv2d(1, 32, 3),
        torch.nn.ReLU(),
        torch.nn.Conv2d(32, 64, 3),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Dropout(0.25),
        torch.nn.Flatten(),
        torch.nn.Linear(9216, 128),
        torch.nn.ReLU(),
        torch.nn.Dropout(),
        torch.nn.Linear(128, 10),
    )
    with open("./data/torch-model.pt", "wb") as f:
        pickle.dump(model, f)
    print("[\x1b[0;32mINFO\x1b[0m]  PyTorch model saved.")
