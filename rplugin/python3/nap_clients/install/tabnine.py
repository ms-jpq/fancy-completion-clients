from asyncio import gather
from os import chmod, stat
from os.path import exists, join
from shutil import move, rmtree
from stat import S_IEXEC
from tempfile import TemporaryDirectory

from ..pkgs.consts import __artifacts__
from ..pkgs.da import download, fetch

ADDR = """\
https://update.tabnine.com\
"""
ARCH = (
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
    "x86_64-pc-windows-gnu",
)


async def inst_arch(version: str, arch: str, root: str) -> None:
    path = join(version, arch)
    exe_name = "TabNine.exe" if "windows" in arch else "TabNine"
    uri = join(ADDR, path, exe_name)
    parent = join(root, path)
    fullname = join(parent, exe_name)
    await download(uri, dest=parent, name=exe_name)
    st = stat(fullname)
    chmod(fullname, st.st_mode | S_IEXEC)


async def install() -> None:
    with TemporaryDirectory() as temp:
        temp = "./temp"
        bin_home = "binaries"
        root = join(temp, bin_home)
        ver = await fetch(join(ADDR, "version"))
        version = ver.strip()
        await gather(*(inst_arch(version, arch=arch, root=root) for arch in ARCH))
        dst = join(__artifacts__, bin_home)
        if exists(dst):
            rmtree(dst)
        move(src=root, dst=dst)
