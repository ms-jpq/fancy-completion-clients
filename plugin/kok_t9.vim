let s:path = expand('<sfile>')

lua _kok_clients = require "kok_t9/clients"

call v:lua._kok_clients.init(s:path)
