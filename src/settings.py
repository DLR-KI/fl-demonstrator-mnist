# SPDX-FileCopyrightText: 2024 Benedikt Franke <benedikt.franke@dlr.de>
# SPDX-FileCopyrightText: 2024 Florian Heinrich <florian.heinrich@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from logging import getLogger

from dlr.fl.client.settings import Settings as SettingsBase
from dlr.ki.logging import load_default


def main() -> None:
    from dlr.fl.client.__main__ import default_main

    load_default("logs/train.log")
    getLogger("fl.client").info("logging initialized")
    default_main()


class Settings(SettingsBase):
    MAIN_MODULE: str = "settings.main"
