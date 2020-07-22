let s:path = expand('<sfile>')

lua _fcc = require "fancy-completion/clients"

call v:lua._fcc.init(s:path)
