# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2021 - Diego Escalante Urrelo <diegoe@gnome.org>
"""Entry point for packpath as a script or -m module calls."""

import argparse

import anyio
from signalstickers_client import StickersClient

import packpath


def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="packpath",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=packpath.__doc__,
        epilog="""
---
Configuration is automatically read from `config.yaml` in the provided path.
`config.yaml` has two sections with the following format:

pack:
  title: My Sticker Pack
  author: Mister Sticker
  cover: filename.ext

stickers:
  filename.ext: emoji
  filename-2.ext: emoji
  ...

Note that it's up to you to match Signal's expected image file format.
See: https://github.com/signalstickers/signalstickers-client/blob/master/STICKERS_INTERNALS.md
        """)

    parser.add_argument(
        "--user",
        help="your Signal user token (window.reduxStore.getState().items.uuid_id)",
        default=None, required=True,
        action="store", type=str)
    parser.add_argument(
        "--password",
        help="your Signal password token (window.reduxStore.getState().items.password)",
        default=None, required=True,
        action="store", type=str)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + packpath.__version__)
    parser.add_argument(
        "path",
        help="the path to a directory containing stickers and a config.yaml file",
        default=None, action="store", type=str)

    return parser


async def async_main():
    args = argparser().parse_args()

    if args.path is None:
        raise packpath.PackPathNoPathError

    pp = packpath.PackPath()
    pp.load_path(args.path)

    async with StickersClient(args.user, args.password) as client:
        pack_id, pack_key = await client.upload_pack(pp)

    print(f"""
Pack uploaded. You can install it by visiting:
https://signal.art/addstickers/#pack_id={pack_id}&pack_key={pack_key}

You can also preview your pack at signalstickers.com:
https://signalstickers.com/pack/{pack_id}?key={pack_key}

Note that visiting the above URL will (technically) make the pack ID and key visible to signalstickers.com server logs.
This will NOT add your pack to signalstickers.com, see https://signalstickers.com/contribute for that.
""")


def main():
    anyio.run(async_main)


if __name__ == "__main__":
    main()
