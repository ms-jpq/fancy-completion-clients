from os import chmod, stat
from os.path import join
from shutil import move
from stat import S_IEXEC
from tempfile import TemporaryDirectory

from ..shared.consts import __artifacts__
from ..shared.da import download, fetch

ADDR = """\
https://update.tabnine.com/\
"""
ARCH = (
    "i686-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
    "x86_64-pc-windows-gnu",
    "i686-unknown-linux-gnu",
    "i686-pc-windows-gnu",
)


async def install() -> None:
    with TemporaryDirectory() as temp:
        bin_home = "binaries"
        root = join(temp, bin_home)
        version = await fetch(ADDR + "version")
        for arch in ARCH:
            path = join(version, arch)
            exe_name = "TabNine.exe" if "windows" in arch else "TabNine"
            uri = ADDR + path
            await download(uri, dest=root, name=exe_name)
            fullname = join(root, exe_name)
            st = stat(fullname)
            chmod(fullname, st.st_mode | S_IEXEC)
        move(src=root, dst=join(__artifacts__, bin_home))
