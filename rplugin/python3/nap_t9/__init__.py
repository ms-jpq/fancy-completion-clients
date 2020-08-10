from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Awaitable

from pynvim import Nvim, command, plugin

from .install import install
from .nvim import print


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim
        self.chan = ThreadPoolExecutor()

    def _submit(self, co: Awaitable[None]) -> None:
        loop: AbstractEventLoop = self.nvim.loop

        def run(nvim: Nvim) -> None:
            fut = run_coroutine_threadsafe(co, loop)
            try:
                fut.result()
            except Exception as e:
                stack = format_exc()
                nvim.async_call(nvim.err_write, f"{stack}{e}")

        self.chan.submit(run, self.nvim)

    @command("NAPInstallTabNine")
    def inst_tabnine(self) -> None:
        async def inst() -> None:
            await print(self.nvim, "⏳...⌛️")
            await install()
            await print(self.nvim, "✅")

        self._submit(inst())
