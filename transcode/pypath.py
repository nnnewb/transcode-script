from pathlib import PurePath

import click


class PyPath(click.Path):
    def convert(self, value, param, ctx):
        return PurePath(super().convert(value, param, ctx))