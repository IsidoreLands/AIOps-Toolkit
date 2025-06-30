--[[
-
- OODA WIKI: WEZTERM CONFIGURATION v1.5 (DIAGNOSTIC MODE)
-
--]]

-- ============== 1. INITIAL SETUP AND LIBRARIES ==============
local wezterm = require 'wezterm'
local mux = wezterm.mux
local act = wezterm.action
local config = {}
if wezterm.config_builder then
  config = wezterm.config_builder()
end

-- ============== OODA FIVE: ENABLE EVENT DEBUGGING ==============
config.debug_key_events = true

-- NOTE: The functions below are preserved for when we have the correct button names.
local paste_is_armed = false
local last_copy_timestamp = 0
local paste_timeout_seconds = 5
local function copy_last_lines_and_arm_paste(window, pane, line_count)
  local text = pane:get_lines_as_text(line_count)
  wezterm.set_clipboard(text)
  paste_is_armed = true
  last_copy_timestamp = wezterm.time.now()
  window:set_right_status(wezterm.format {
    { Text = string.format("Copied %d lines. Paste is ARMED for %d seconds.", line_count, paste_timeout_seconds) },
  })
end
local function paste_if_armed(window, pane)
  local current_time = wezterm.time.now()
  if paste_is_armed and (current_time - last_copy_timestamp) < paste_timeout_seconds then
    window:perform_action(wezterm.action.PasteFrom 'Clipboard', pane)
    window:set_right_status("Pasted from clipboard.")
    paste_is_armed = false
  else
    window:set_right_status("Paste is not armed.")
    paste_is_armed = false
  end
  wezterm.sleep_ms(1500)
  window:set_right_status("")
end
local copy_key_table = {
  { key = '1', mods = 'NONE', action = wezterm.action_callback(function(window, pane) copy_last_lines_and_arm_paste(window, pane, 50) end) },
  { key = '2', mods = 'NONE', action = wezterm.action_callback(function(window, pane) copy_last_lines_and_arm_paste(window, pane, 100) end) },
  { key = '3', mods = 'NONE', action = wezterm.action_callback(function(window, pane) copy_last_lines_and_arm_paste(window, pane, 150) end) },
}
config.key_tables = { copy_mode = copy_key_table }

-- ============== 3. THEME AND APPEARANCE ==============
config.font = wezterm.font 'JetBrains Mono'
config.color_schemes = {
  ['F-16 HUD (Green)'] = {
    background = '#050A05', foreground = '#00FF41', cursor_bg = '#00FF41',
    cursor_fg = '#050A05', cursor_border = '#00FF41', selection_bg = '#00802B',
    selection_fg = '#FFFFFF',
    ansi = { '#101510', '#00A12A', '#00B32E', '#00C433', '#00D637', '#00E73C', '#00F940', '#00FF41' },
    brights = { '#66FF8C', '#00FF41', '#1FFF5A', '#32FF6A', '#52FF83', '#73FFA1', '#94FFBE', '#B5FFD3' },
  },
}
config.color_scheme = 'F-16 HUD (Green)'
config.window_background_image = 'C:\\Users\\cwpat\\Downloads\\pexels-antonio-moura-47482110-10392692.jpg'
config.window_background_opacity = 0.9
config.text_background_opacity = 0.7

-- ============== 4. STARTUP AND WORKSPACE (REVISED) ==============
wezterm.on('gui-startup', function(cmd)
  local gem_command = { 'ssh', '-i', 'C:\\Users\\cwpat\\.ssh\\id_ed25519', '-tt', 'isidore-admin@159.65.246.113', 'cd ~/aiops_toolkit && /home/isidore-admin/.nvm/versions/node/v22.17.0/bin/node /home/isidore-admin/.nvm/versions/node/v22.17.0/bin/gemini' }
  -- CORRECTED: Changed -t to -tt
  local aio_command = { 'ssh', '-i', 'C:\\Users\\cwpat\\.ssh\\id_ed25519', '-tt', 'isidore-admin@159.65.246.113', 'cd ~/aiops_toolkit && /bin/bash' }
  -- CORRECTED: Changed -t to -tt
  local mwk_command = { 'ssh', '-i', 'C:\\Users\\cwpat\\.ssh\\id_ed25519', '-tt', 'root@104.248.8.20', '/bin/bash' }

  local tab, pane_ul, window = mux.spawn_window { workspace = 'MediaWiki-Stabilization', args = gem_command }
  
  local pane_ur = pane_ul:split{ direction="Right", size=0.5, args = aio_command }
  local pane_bl = pane_ul:split{ direction="Bottom", size=0.5, args = mwk_command }
  local pane_br = pane_ur:split{ direction="Bottom", size=0.5, args = mwk_command }
  local pane_bl_right = pane_bl:split{ direction="Right", size=0.5, args = mwk_command }
  
  window:gui_window():maximize()
  mux.set_active_workspace('MediaWiki-Stabilization')
end)

-- ============== 5. KEY AND MOUSE BINDINGS ==============
config.keys = {
  { key = 'Insert', mods = 'CTRL', action = act.CopyTo 'Clipboard' },
  { key = 'Insert', mods = 'SHIFT', action = act.PasteFrom 'Clipboard' },
  { key = '-', mods = 'ALT', action = act.SplitHorizontal { args = { 'wsl.exe', 'ssh', 'isidore-admin@159.65.246.113' } } },
  { key = '\\', mods = 'ALT', action = act.SplitVertical { args = { 'wsl.exe', 'ssh', 'isidore-admin@159.65.246.113' } } },
  { key = 'w', mods = 'ALT', action = act.CloseCurrentPane { confirm = true } },
  { key = 'LeftArrow', mods = 'SUPER', action = act.ActivatePaneDirection 'Left' },
  { key = 'RightArrow', mods = 'SUPER', action = act.ActivatePaneDirection 'Right' },
  { key = 'UpArrow', mods = 'SUPER', action = act.ActivatePaneDirection 'Up' },
  { key = 'DownArrow', mods = 'SUPER', action = act.ActivatePaneDirection 'Down' },
  { key = 'l', mods = 'ALT', action = act.SpawnCommandInNewTab { label = 'Legate', args = { 'cmd.exe', '/c', 'ssh -i C:\\Users\\cwpat\\.ssh\\id_ed25519_legate legate@159.65.246.113' } } },
  { key = 'q', mods = 'CTRL|SHIFT', action = act.SpawnCommandInNewTab { label = 'Quaestor', args = { 'cmd.exe', '/c', 'ssh -i C:\\Users\\cwpat\\.ssh\\id_ed25519_quaestor quaestor@159.65.246.113' } } },
  { key = 'c', mods = 'CTRL|SHIFT', action = act.SpawnCommandInNewTab { label = 'Centurion', args = { 'cmd.exe', '/c', 'ssh -i C:\\Users\\cwpat\\.ssh\\id_ed25519_centurion centurion@159.65.246.113' } } },
  { key = 'd', mods = 'CTRL|SHIFT', action = act.SpawnCommandInNewTab { label = 'Decanus', args = { 'cmd.exe', '/c', 'ssh -i C:\\Users\\cwpat\\.ssh\\id_ed25519_decanus decanus@159.65.246.113' } } },
  { key = 'a', mods = 'CTRL|SHIFT', action = act.SpawnCommandInNewTab { label = 'Auxilia', args = { 'cmd.exe', '/c', 'ssh -i C:\\Users\\cwpat\\.ssh\\id_ed25519_auxilia auxilia@159.65.246.113' } } },
}

config.mouse_bindings = {
  -- OODA FIVE: Side button bindings are temporarily disabled pending observation.
  -- { event = { Down = { streak = 1, button = '???' } }, mods = 'NONE', action = wezterm.action.ActivateKeyTable { name = 'copy_mode', one_shot = false } },
  -- { event = { Up = { streak = 1, button = '???' } }, mods = 'NONE', action = wezterm.action.PopKeyTable },
  -- { event = { Down = { streak = 1, button = '???' } }, mods = 'NONE', action = wezterm.action_callback(paste_if_armed) },

  -- Original User Binding: Right-click for copy/paste
  { event = { Down = { streak = 1, button = 'Right' } }, mods = 'NONE', action = wezterm.action_callback(function(window, pane)
    local has_selection = window:get_selection_text_for_pane(pane) ~= ''
    if has_selection then
      window:perform_action(act.CopyTo('ClipboardAndPrimarySelection'), pane)
      window:perform_action(act.ClearSelection, pane)
    else
      window:perform_action(act.PasteFrom 'Clipboard', pane)
    end
  end) },
}

-- ============== 6. RETURN FINAL CONFIGURATION ==============
return config

--[[
-
- OODA FIVE: ISSUE REPORT (June 30, 2025)
- For: Operation: Orchard
-
- A cosmetic display issue was observed where garbled/duplicated command prompts
- appear in specific panes.
-
- TRIGGERS:
-   1. Moving the WezTerm window to a secondary monitor (with different display scaling).
-   2. Manually resizing pane dimensions by dragging the borders.
-
- ASSESSMENT:
-   This is likely a system-level issue related to graphics drivers or display
-   scaling, not a bug in this configuration file.
-
- DECISION:
-   Per the Resource Economy Principle (Metarule C), this aesthetic issue is
-   de-prioritized to focus on the primary mission (MediaWiki stabilization).
-   To be re-evaluated during Operation: Orchard.
-
--]]
