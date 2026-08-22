--[==[
fx.lua -- one small module.

The levelled long comment exists so the body can hold ]] and [[
without closing early, which is why the row lists every level it knows.
]==]

local M = {}

-- Returns the sum of a and b.
local function add(a, b)
  return a + b  -- a trailing comment
end

M.add = add
M.url = "http://example.com/not-a-comment"

return M
