from pynvim import Nvim, command, plugin


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    @command("FCt9")
    def initialize(self) -> None:
        pass
