import base64
import contextlib
import os
import tempfile
import unittest

from pathlib import Path
from random import choices

import yaml

import packpath


# 1x1 transparent PNG from https://png-pixel.com
TEST_IMG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


class TestPackPath(unittest.TestCase):
    pack_title = "Test Sticker Pack 😎"
    pack_author = "Test Author Name ✍️"
    pack_emojis = [
        "🤡",
        "🥑",
        "🙈",
        "🚢",
        "🐶",
    ]
    pack_n_stickers = 10

    @contextlib.contextmanager
    def pack_config(self, filename: os.PathLike):
        """Make `filename` the temporary config.yaml file for a path."""
        os.rename(filename, self.pack_dir / "config.yaml")
        yield
        os.rename(self.pack_dir / "config.yaml", filename)

    def setUp(self):
        self.pack_dir = Path(tempfile.mkdtemp())
        self.pack_stickers = []

        _, self.yaml_right = tempfile.mkstemp(dir=self.pack_dir)
        _, self.yaml_wrong_cover = tempfile.mkstemp(dir=self.pack_dir)
        _, self.yaml_wrong_sticker = tempfile.mkstemp(dir=self.pack_dir)

        self.test_img = base64.b64decode(TEST_IMG)

        self.yaml_right_content = {
            "pack": {
                "title": self.pack_title,
                "author": self.pack_author,
                "cover": "",
            },
            "stickers": {},
        }

        for i in range(0, self.pack_n_stickers):
            fd, filename = tempfile.mkstemp(dir=self.pack_dir, prefix=f"{i:03}_")
            basename = Path(filename).name
            emoji = choices(self.pack_emojis)[0]

            self.yaml_right_content["stickers"][basename] = emoji
            # Register the order of the emojis
            self.pack_stickers.append(emoji)

            with os.fdopen(fd, "wb") as image:
                image.write(self.test_img)

        # A fully valid YAML
        self.yaml_right_content["pack"]["cover"] = choices([*self.yaml_right_content["stickers"].keys()])[0]
        with open(self.yaml_right, "wt") as yaml_right:
            yaml.dump(self.yaml_right_content, yaml_right, allow_unicode=True)

        # A valid YAML with wrong pack.cover
        yaml_wrong_cover = {**self.yaml_right_content}
        yaml_wrong_cover["pack"]["cover"] = "non-existant-file"
        with open(self.yaml_wrong_cover, "wt") as yaml_wrong:
            yaml.dump(yaml_wrong_cover, yaml_wrong, allow_unicode=True)

        # A valid YAML with bad filenames
        yaml_wrong_sticker = {**self.yaml_right_content}
        yaml_wrong_sticker["stickers"]["non-existant-file"] = "❌"
        with open(self.yaml_wrong_sticker, "wt") as yaml_wrong:
            yaml.dump(yaml_wrong_sticker, yaml_wrong, allow_unicode=True)

    def test_load_yaml(self):
        """Test that a valid YAML can be loaded into a pack."""
        pp = packpath.PackPath()

        with self.pack_config(self.yaml_right):
            pp.load_path(self.pack_dir)

        self.assertEqual(self.pack_title, pp.title)
        self.assertEqual(self.pack_author, pp.author)

        self.assertEqual(self.pack_n_stickers, len(pp.stickers))

        for i, s in enumerate(pp.stickers):
            self.assertEqual(self.pack_stickers[i], s.emoji)
            self.assertEqual(self.test_img, s.image_data)

        self.assertEqual(self.test_img, pp.cover.image_data)
        self.assertEqual(self.pack_n_stickers, pp.nb_stickers)

    def test_bad_yaml_cover(self):
        """A valid YAML with a cover that does not exist."""
        pp = packpath.PackPath()

        with self.pack_config(self.yaml_wrong_cover):
            with self.assertRaises(FileNotFoundError):
                pp.load_path(self.pack_dir)

    def test_bad_stickers(self):
        """A valid YAML with stickers that do not exist."""
        pp = packpath.PackPath()

        with self.pack_config(self.yaml_wrong_sticker):
            with self.assertRaises(FileNotFoundError):
                pp.load_path(self.pack_dir)
