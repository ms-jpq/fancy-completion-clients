let s:path = expand('<sfile>')

lua _narc_clients = require "narc_t9/clients"

call v:lua._narc_clients.init(s:path)
