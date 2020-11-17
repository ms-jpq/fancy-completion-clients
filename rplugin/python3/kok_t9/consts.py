from os.path import dirname, join, realpath

__base__ = dirname(dirname(dirname(dirname(realpath(__file__)))))
__artifacts__ = join(__base__, "artifacts")
__temp__ = join(__base__, "temp")
