# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from argparse import Namespace
from contextlib import ContextDecorator
from functools import partial
import logging
import torch
from torch.nn import CrossEntropyLoss
from torch.optim import SGD
from torch.optim.lr_scheduler import StepLR
from torch.utils.tensorboard import SummaryWriter


class Config(ContextDecorator):
    """
    Training configuration class including logging (summary writer) handle.

    Example:

    ```python
    with Config(args) as config:
        trained_model, metrics, sample_size = train(model, config)
        # ...
    ```
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    epochs = 2
    batch_size = 256
    optimizer = partial(SGD, lr=0.05, momentum=0.9, nesterov=True, weight_decay=0.0001)
    scheduler = partial(StepLR, step_size=5, gamma=0.95)
    loss = CrossEntropyLoss(reduction="mean")
    logger = logging.getLogger("fl.client")
    log_interval = 20

    def __init__(self, args: Namespace) -> None:
        self.args = args
        self.summary_writer = SummaryWriter(f"s3://trainings/{self.args.training_id}/{self.args.client_id}")

    def get_global_training_epoch(self, local_epoch: int) -> int:
        """
        Get the global training epoch.

        Calculates and returns the global training epoch based on the local epoch and the training round.

        Note:

        - `self.args.round` (training round) is zero based
        - testing rounds are not considered or included

        Example:

        Consider a scenario where the client returns the model to the server after every three local epochs.
        If we are in the second training round and the first local epoch, the global training epoch would be
        calculated as 1 + 3*2, which equals 7.

        Args:
            local_epoch (int): local training epoch

        Returns:
            int: global training epoch
        """
        # NOTE:
        # - self.args.round is zero based
        # - testing rounds are not considered
        return max(local_epoch, 0) + self.epochs * self.args.round

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.summary_writer.close()
