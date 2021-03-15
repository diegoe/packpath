# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2021 - Diego Escalante Urrelo <diegoe@gnome.org>
"""Automatically upload Signal stickers from a given path and YAML configuration."""

__author__ = "Diego Escalante Urrelo"
__license__ = "AGPL-3.0-only"
__version__ = "0.9.4"

import os
import yaml

from pathlib import Path

from signalstickers_client.models import LocalStickerPack, Sticker


class PackPathNoConfigError(Exception):
    """Pack config not found."""
    pass


class PackPath(LocalStickerPack):
    def load_path(self, pack_path: os.PathLike):
        """Load the LocalStickerPack object based on a config.yaml file."""

        self.pp_path = Path(pack_path)
        self.pp_config_path = self.pp_path / "config.yaml"

        if not self.pp_config_path.is_file():
            raise PackPathNoConfigError(f"config.yaml not found in path {self.pp_path}")

        with self.pp_config_path.open() as y:
            self.pp_config = yaml.safe_load(y)

        self.title = self.pp_config["pack"]["title"]
        self.author = self.pp_config["pack"]["author"]

        print(f"[packpath] Configuring sticker pack {self.title} by {self.author}")

        for path, emoji in self.pp_config["stickers"].items():
            sticker_path = self.pp_path / path

            print(f"[packpath] Adding: {emoji} for {sticker_path}")

            with sticker_path.open("rb") as image_data:
                stick = Sticker()
                stick.id = self.nb_stickers
                stick.emoji = emoji

                stick.image_data = image_data.read()
                self._addsticker(stick)

        # Note that technically Signal does not require a cover, however
        # we opinionatedly require that one is defined in config.yaml.
        cover_path = self.pp_path / self.pp_config["pack"]["cover"]
        with cover_path.open("rb") as image_data:
            cover = Sticker()
            cover.id = self.nb_stickers

            cover.image_data = image_data.read()
            self.cover = cover
