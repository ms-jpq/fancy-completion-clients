let s:path = expand('<sfile>')

lua _nap_clients = require "nap/clients"

call v:lua._nap_clients.init(s:path)
