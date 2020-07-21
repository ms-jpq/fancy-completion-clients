local api = vim.api


local init = function (location)

  vim.g.fancy_completion_settings_private = location

end



return {
  init = init,
}
