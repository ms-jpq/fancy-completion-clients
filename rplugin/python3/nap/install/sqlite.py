from os.path import join
from tempfile import TemporaryDirectory

from ..shared.consts import __temp__
from ..shared.da import download, unzip

ADDR = """
https://www.sqlite.org/src/zip/sqlite.zip?r=release
"""


async def install() -> None:
    with TemporaryDirectory() as temp:
        base = __temp__
        zip_name = join(base, "sqlite.zip")
        await download(ADDR, dest=base, name=zip_name)
        unzip(zip_name)

        pass
