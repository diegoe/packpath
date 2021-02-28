# packpath
Automatically upload Signal stickers from a given path and YAML configuration

## How it works

`packpath` reads a path and loads a `config.yaml` file from it to automatically
fill a `signalstickers-client` client, and submit stickers.

It subclasses `signalstickers_client.models.LocalStickerPack` to add a
`load_path()` method.

The module is meant for command line invocation, but can easily be used
in code:

```sh
  $ python3 -m packpath [path] --user [uuid_id] --password [password]
```

## YAML format

The YAML format is rather simple:

```yaml
pack:
  title: Your sticker pack title
  author: An author name
  cover: filename-for-the-cover.png

stickers:
  filename.png: 👀
  another-filename.png: 👋
  (...)
```

To save yourself some work, you can use `ls` to output an almost ready
list of filenames to use on your `config.yaml`:

```sh
  $ ls -1 >> config.yaml
```

## Signal credentials

From https://github.com/signalstickers/signalstickers-client#uploading-a-pack:

> You will need your Signal credentials To obtain them, open the
> Developer Tools in Signal Desktop, and type
> window.reduxStore.getState().items.uuid_id to get your USER, and
> window.reduxStore.getState().items.password to get your PASSWORD.

The above is also available in `python3 -m packpath --help`.

## Credits

This is a simple wrapper on top of the very handy
[`signalstickers-client`](https://github.com/signalstickers/signalstickers-client).

Go check it out.

## Disclaimer

All boiler plate disclaimers apply. But also please be respectful of
Signal's service. Don't abuse this or any other script. This is meant to
help legitimate users make the most of the service.


## Development

Make sure to run flake8 on any changes you make, and also to run the
tests:
```sh
  $ flake8 packpath
  $ python3 -m unittest discover
```
