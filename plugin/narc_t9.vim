let s:path = expand('<sfile>')

lua _narc_clients = require "narc/clients"

call v:lua._narc_clients.init(s:path)
