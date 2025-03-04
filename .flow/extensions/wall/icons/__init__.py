# Copyright (c) 2025 Marcin Zdun
# This code is licensed under MIT license (see LICENSE for details)

import os

from proj_flow.api import env, step
from proj_flow.api.makefile import Makefile

from . import magick

ICONS = os.path.join("data", "icons")
ASSETS = os.path.join("data", "assets")
ICONS_PNG = os.path.join(ICONS, "png")
STENCIL = os.path.join(ICONS_PNG, "appicon.png")
SIZES = ["16", "24", "32", "48", "256"]

makefile = Makefile(
    [
        magick.svg_to_png(
            output=STENCIL,
            image=os.path.join(ICONS, "appicon.svg"),
            mask=os.path.join(ICONS, "appicon-mask.svg"),
        ),
        *(
            magick.resize(
                output=os.path.join(ICONS_PNG, f"appicon-{size}.png"),
                stencil=STENCIL,
                size=size,
            )
            for size in SIZES
        ),
        magick.merge(
            os.path.join(ASSETS, "appicon.ico"),
            [os.path.join(ICONS_PNG, f"appicon-{size}.png") for size in SIZES],
        ),
        magick.mkdirs(ICONS_PNG),
        magick.copy(
            os.path.join(ICONS_PNG, f"appicon-256.png"),
            os.path.join(ASSETS, f"appicon.png"),
        ),
    ]
)


@step.register
class IconsStep:
    name = "Icons"
    runs_before = ["Build"]

    def platform_dependencies(self):
        return [f"{magick.tool}>=6"]

    def run(self, config: env.Config, rt: env.Runtime) -> int:
        return makefile.run(rt)
