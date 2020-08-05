from os.path import dirname, join, realpath

__nap__ = dirname(dirname(realpath(__file__)))
__base__ = dirname(dirname(dirname(__nap__)))
__artifacts__ = join(__base__, "artifacts")
