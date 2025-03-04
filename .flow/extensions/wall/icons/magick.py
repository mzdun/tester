# Copyright (c) 2025 Marcin Zdun
# This code is licensed under MIT license (see LICENSE for details)

import os
import sys
from typing import List

from proj_flow.api.env import Runtime
from proj_flow.api.makefile import Rule, Statement

tool = "magick" if sys.platform == "win32" else "convert"


class MkDirs(Rule):
    def command(self, _: Statement):
        return []

    def run(self, st: Statement, rt: Runtime):
        for output in st.outputs:
            result = rt.mkdirs(output)
            if result:
                return result
        return 0


class Copy(Rule):
    def command(self, _: Statement):
        return []

    def run(self, st: Statement, rt: Runtime):
        return rt.cp(st.inputs[0], st.outputs[0])


class Magick:
    class SvgToPng(Rule):
        def command(self, st: Statement):
            return [
                tool,
                "-background",
                "none",
                *st.inputs,
                "-alpha",
                "Off",
                "-compose",
                "CopyOpacity",
                "-composite",
                st.outputs[0],
            ]

    class Resize(Rule):
        size: str

        def __init__(self, size: str):
            self.size = size

        def command(self, st: Statement):
            return [
                tool,
                "-background",
                "none",
                st.inputs[0],
                "-resize",
                f"{self.size}x{self.size}",
                "-depth",
                "32",
                st.outputs[0],
            ]

    class Merge(Rule):
        def command(self, st: Statement):
            return [
                tool,
                *st.inputs,
                st.outputs[0],
            ]


def mkdirs(dirname: str):
    return MkDirs.statement([dirname], [])


def copy(src: str, dst: str):
    return Copy.statement([dst], [src])


def svg_to_png(output: str, image: str, mask: str):
    return Magick.SvgToPng.statement([output], [image, mask], [os.path.dirname(output)])


def resize(output: str, stencil: str, size: str):
    return Statement(
        Magick.Resize(size), [output], [stencil], [os.path.dirname(output)]
    )


def merge(output: str, layers: List[str]):
    return Magick.Merge.statement([output], layers, [os.path.dirname(output)])
