#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser, Namespace
from logging import getLogger, Logger
from os import environ
import torch.nn
from typing import Any, Dict, Tuple
from uuid import UUID
import warnings

from dlr.fl.client import Communication
from dlr.ki.logging import load_default

from config import Config  # type:ignore [import]
import training  # type:ignore [import]
from utils import log_data_distribution  # type:ignore [import]


def train(model: torch.nn.Module, config: Config) -> Tuple[torch.nn.Module, Dict[str, Any], int]:
    """
    Train a model.

    Args:
        model (torch.nn.Module): model to train
        config (Config): training configuration and logging handle

    Returns:
        Tuple[torch.nn.Module, Dict[str, Any], int]: trained model, calculated metrics, and sample size
    """
    model = model.to(config.device)
    train_loader, test_loader = training.get_data_loader(config.batch_size)
    log_data_distribution(config, train_loader, test_loader)
    optimizer = config.optimizer(model.parameters())
    scheduler = config.scheduler(optimizer)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Ignore warning that `scheduler.step()` is called before `optimizer.step()` and therefore the
        # first learning rates are skipped. This is exactly what we want!
        # We want to continue and not restart.
        scheduler.step(config.get_global_training_epoch(0))
    for epoch in range(1, config.epochs + 1):
        config.logger.debug(f"EPOCH: {epoch}")
        config.logger.debug("start training")
        training.train_epoch(config, model, train_loader, optimizer, epoch)
        config.logger.debug("start testing")
        metrics = training.test(config, model, test_loader, epoch)
        config.logger.debug("test metrics: " + str(metrics))
        scheduler.step()
    sample_size = len(train_loader.dataset)  # type: ignore[arg-type]
    return model, metrics, sample_size


def test(model: torch.nn.Module, config: Config) -> Dict[str, Any]:
    """
    Test a model.

    Args:
        model (torch.nn.Module): model to test
        config (Config): training configuration and logging handle

    Returns:
        Dict[str, Any]: calculated metrics
    """
    model = model.to(config.device)
    _, test_loader = training.get_data_loader(config.batch_size)
    config.logger.debug("start testing")
    metrics = training.test(config, model, test_loader, epoch=-1)
    config.logger.debug("test metrics: " + str(metrics))
    return metrics


def main(logger: Logger) -> None:
    """
    Main entry point of the Machine Learning training script.

    Args:
        logger (Logger): logger instance

    Raises:
        ValueError: Unknown action in command line arguments
    """
    logger.info(
        "Hint: FL_DEMONSTRATOR_USERNAME and CLIENT_ID must be set as environment variables"
        "and the later one must also be a valid UUID."
    )
    USERNAME = environ["FL_DEMONSTRATOR_USERNAME"]  # raise KeyError if not set
    PASSWORD = "mnist-secret"
    args = parse_args()
    logger.debug("args: " + str(args))
    com = Communication.from_user_password(
        args.client_id,
        args.training_id,
        args.round,
        args.model_id,
        USERNAME,
        PASSWORD
    )
    model: torch.nn.Module = com.download_model()
    with Config(args) as config:
        match args.action:
            case "train":
                trained_model, metrics, sample_size = train(model, config)
                com.upload_model(trained_model, metrics, sample_size)
            case "test":
                metrics = test(model, config)
                com.upload_metrics(metrics)
            case _:
                raise ValueError(f"Unknown action: {args.action}")
    logger.info("trainings script end")


def parse_args() -> Namespace:
    """
    Parse command line arguments.

    This function creates an argument parser for the main.py script,
    defines the necessary arguments, and parses the command line input.

    Returns:
        Namespace: The parsed command line arguments
    """
    parser = ArgumentParser(prog="main.py", description="MNIST example main.py")
    parser.add_argument("action", choices=["train", "test"], type=str, help="Action to perform")
    parser.add_argument("--client-id", default=UUID(environ["CLIENT_ID"]), type=UUID, help="Client UUID")
    parser.add_argument("--training-id", required=True, type=UUID, help="Training UUID")
    parser.add_argument("--round", required=True, type=int, help="Training round")
    parser.add_argument("--model-id", required=True, type=UUID, help="Global model UUID")
    return parser.parse_args()


def full_stack() -> str:
    """
    Get the full stack trace as string.

    Returns:
        str: stack trace

    Reference:

    - https://stackoverflow.com/a/16589622 (source)
    """
    import sys
    import traceback

    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:
        # if an exception is present
        # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
        del stack[-1]
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        stackstr += "  " + traceback.format_exc().lstrip(trc)
    return stackstr


if __name__ == "__main__":
    # set up logging module
    load_default("logs/train.log")
    logger = getLogger("fl.client")
    logger.info("Start training")

    try:
        # call main function
        main(logger)
    except Exception as ex:
        # catch and log any unexpected exception including its call stack
        if hasattr(ex, "message"):
            message = ex.message
        else:
            message = ex
        logger.error(message)
        logger.debug(full_stack())
