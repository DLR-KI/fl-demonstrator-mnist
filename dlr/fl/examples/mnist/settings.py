from logging import getLogger

from dlr.fl.client.settings import Settings as SettingsBase
from dlr.ki.logging import load_default


def main() -> None:
    from dlr.fl.client.__main__ import default_main

    load_default("logs/train.log")
    getLogger("fl.client").info("logging initialized")
    default_main()


class Settings(SettingsBase):
    MAIN_MODULE: str = "dlr.fl.examples.mnist.settings.main"
