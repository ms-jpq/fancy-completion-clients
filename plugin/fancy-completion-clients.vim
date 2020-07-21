let s:path = expand('<sfile>')

lua _fcc = require "fancy_completion_clients"

call v:lua._fcc.init(s:path)
