from os.path import dirname, join, realpath

__nap__ = dirname(dirname(realpath(__file__)))
__base__ = dirname(dirname(dirname(__nap__)))
___artifacts__ = join(__base__, "artifacts")
