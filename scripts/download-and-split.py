#!/usr/bin/env python

import pickle
import torch
from torch.utils.data import Subset
from torchvision import transforms
from torchvision.datasets import MNIST


DATA_PATH = "./data"


def get_datasets():
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    trainset = MNIST(DATA_PATH, train=True, download=True, transform=transform)
    testset = MNIST(DATA_PATH, train=False, transform=transform)
    return trainset, testset


def save_to_file(obj, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(obj, f)
    print(f"[\x1b[0;32mINFO\x1b[0m]  Saved: {filepath}")


if __name__ == "__main__":
    client_data_sizes = [50, 100, 75, 250, 15, 300, 80, 120, 180, 140]
    test_data_size = 200

    trainset, testset = get_datasets()
    indices = torch.arange(len(trainset))
    indices = indices[torch.randperm(indices.shape[0])]

    data_idx = 0
    for client_idx, client_size in enumerate(client_data_sizes):
        client_subset = Subset(trainset, indices[data_idx:data_idx+client_size].numpy().tolist())
        save_to_file(client_subset, DATA_PATH + f"/client-{client_idx+1:02}.pt")
        data_idx = data_idx + client_size + 1

    indices = torch.arange(len(testset))
    indices = indices[torch.randperm(indices.shape[0])]
    testset_subset = Subset(testset, indices[:test_data_size].numpy().tolist())
    save_to_file(testset_subset, DATA_PATH + "/client-test.pt")
