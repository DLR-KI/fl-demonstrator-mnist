# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import pickle
import torch
from torch.nn import Module
from torch.utils.data import DataLoader, Dataset
from torch.optim import Optimizer
from torcheval.metrics.functional import (
    multiclass_accuracy,
    multiclass_auroc,
    multiclass_recall,
    multiclass_precision,
)
from typing import Dict, Tuple

from config import Config  # type:ignore [import]


def get_datasets() -> Tuple[Dataset, Dataset]:
    """
    Load and return the training and testing datasets.

    Returns:
        Tuple[Dataset, Dataset]: training and testing datasets
    """
    with open("./data/client-train.pt", "rb") as f:
        trainset = pickle.load(f)
    with open("./data/client-test.pt", "rb") as f:
        testset = pickle.load(f)
    return trainset, testset


def get_data_loader(batch_size: int) -> Tuple[DataLoader, DataLoader]:
    """
    Get the training and testing data loaders.

    Args:
        batch_size (int): batch size

    Returns:
        Tuple[DataLoader, DataLoader]: training and testing data loaders
    """
    trainset, testset = get_datasets()
    train_loader = DataLoader(trainset, batch_size=batch_size)
    test_loader = DataLoader(testset, batch_size=batch_size)
    return train_loader, test_loader


def train_epoch(config: Config, model: Module, train_loader: DataLoader, optimizer: Optimizer, epoch: int):
    """
    Train a model for one epoch.

    Args:
        config (Config): training configuration and logging handle
        model (Module): model to train
        train_loader (DataLoader): training data loader
        optimizer (Optimizer): training optimizer
        epoch (int): current epoch
    """
    dataset_length = len(train_loader.dataset)  # type: ignore[arg-type]
    dataloader_length = len(train_loader)

    model.train()
    for batch_idx, (data, target) in enumerate(train_loader, 0):
        data, target = data.to(config.device), target.to(config.device)
        optimizer.zero_grad()
        output = model(data)
        loss = config.loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % config.log_interval == 0 or batch_idx == dataloader_length - 1:
            x = batch_idx * config.batch_size + len(data)
            msg = "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                epoch, x, dataset_length,
                100. * x / dataset_length, loss.item()
            )
            config.logger.info(msg)

    config.summary_writer.add_scalar("Loss/Training", loss.item(), config.get_global_training_epoch(epoch))


def test(config: Config, model: Module, test_loader: DataLoader, epoch: int) -> Dict[str, float]:
    """
    Test a model.

    Args:
        config (Config): training configuration and logging handle
        model (Module): model to test
        test_loader (DataLoader): testing data loader
        epoch (int): current epoch

    Returns:
        Dict[str, float]: calculated metrics
    """
    model.eval()
    test_loss = 0.
    outputs, targets = torch.tensor([]), torch.tensor([])
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(config.device), target.to(config.device)
            output = model(data)
            test_loss += config.loss(output, target).detach().cpu().item()
            outputs = torch.cat((outputs, output.detach().cpu()), dim=0)
            targets = torch.cat((targets, target.detach().cpu()), dim=0)

    metrics: Dict[str, float] = dict(
        loss=test_loss/float(len(targets)),
        accuracy=multiclass_accuracy(outputs, targets, num_classes=10).item(),
        auroc=multiclass_auroc(outputs, targets, num_classes=10).item(),
        recall=multiclass_recall(outputs, targets, num_classes=10).item(),
        precision=multiclass_precision(outputs, targets, num_classes=10).item(),
    )

    msg = "Test set: Average loss: {:.4f}, Accuracy: {}".format(
        metrics["loss"], metrics["accuracy"]
    )
    config.logger.info(msg)

    global_epoch = config.get_global_training_epoch(epoch)
    config.summary_writer.add_scalar("Loss/Testing", metrics["loss"], global_epoch)
    config.summary_writer.add_scalar("Metrics/Accuracy", metrics["accuracy"], global_epoch)
    config.summary_writer.add_scalar("Metrics/AUROC", metrics["auroc"], global_epoch)
    config.summary_writer.add_scalar("Metrics/Recall", metrics["recall"], global_epoch)
    config.summary_writer.add_scalar("Metrics/Precision", metrics["precision"], global_epoch)

    return metrics
