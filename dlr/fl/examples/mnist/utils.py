from collections import Counter
import torch
from torch.utils.data import DataLoader

from config import Config  # type:ignore [import]


def log_data_distribution(config: Config, train_loader: DataLoader, test_loader: DataLoader) -> None:
    """
    Calculate and log the data distribution.

    Args:
        config (Config): training configuration and logging handle
        train_loader (DataLoader): training data loader
        test_loader (DataLoader): testing data loader
    """
    if config.args.round != 0:
        return

    def add_label_distribution(tag, loader: DataLoader):
        if hasattr(loader.dataset, "targets"):
            targets = loader.dataset.targets.tolist()
        else:
            targets = torch.cat([target for _, target in loader], dim=0).tolist()
        counter = Counter(targets)
        for label_idx in sorted(counter.keys()):
            config.summary_writer.add_scalar(tag, counter.get(label_idx), label_idx)

    config.summary_writer.add_scalar("Data/Training Sample Size", len(train_loader.dataset))  # type: ignore[arg-type]
    config.summary_writer.add_scalar("Data/Testing Sample Size", len(test_loader.dataset))  # type: ignore[arg-type]
    add_label_distribution("Data/Training Label Distribution", train_loader)
    add_label_distribution("Data/Testing Label Distribution", test_loader)
