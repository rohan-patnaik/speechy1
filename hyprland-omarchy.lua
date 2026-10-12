-- Omarchy Lua Hyprland. Modifier keycodes are XKB codes, not evdev codes.
-- Tracks four modifier booleans; no ordinary key events are saved.
local down = {}
local recording = false
local command = os.getenv("HOME") .. "/.local/bin/speechy1 "
hl.on("input.keyboard.key", function(code, _, state)
  if code ~= 37 and code ~= 105 and code ~= 133 and code ~= 134 then return end
  down[code] = state == 1 or nil
  local ctrl = down[37] or down[105]
  local super = down[133] or down[134]
  local chord = ctrl and super
  if chord and not recording then
    recording = true
    hl.exec_cmd(command .. "start --keyboard")
  elseif recording and not chord then
    recording = false
    hl.exec_cmd(command .. "stop")
  end
  if not ctrl and not super then hl.exec_cmd(command .. "release") end
end)
