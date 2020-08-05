from os import remove
from os.path import exists, join
from shutil import move
from tempfile import TemporaryDirectory

from ..shared.consts import __artifacts__
from ..shared.da import call, download, unzip

ADDR = """\
https://www.sqlite.org/src/zip/sqlite.zip?r=release\
"""


async def install() -> None:
    with TemporaryDirectory() as temp:
        name = "sqlite.zip"
        await download(ADDR, dest=temp, name=name)
        zip_name = join(temp, "sqlite.zip")
        unzip(zip_name)
        spellfix = join("sqlite", "ext", "misc", "spellfix.c")
        target = "spellfix.so"
        await call(
            "gcc", "-shared", "-fPIC", "-Wall", spellfix, "-o", target, cwd=temp,
        )
        compiled = join(temp, target)
        dst = join(__artifacts__, target)
        if exists(dst):
            remove(dst)
        move(src=compiled, dst=dst)
