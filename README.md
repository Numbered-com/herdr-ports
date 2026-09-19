# herdr-ports

Surface active dev servers in [herdr](https://herdr.dev): a generic `$ports`
badge on every Space running at least one TCP listener, and a popup to inspect
and kill them. Working on several projects at once, it answers "which space
has a live server?" at a glance.

Ports are attributed to a Space by matching the listener's process cwd against
the cwds of the workspace's panes - servers started outside herdr still show
up as long as they run inside a workspace directory. System daemons (cwd `/`,
`~/Library`, ...) never match, so the default view stays clean.

## Install

```sh
herdr plugin install Numbered-com/herdr-ports
```

Requirements: `jq`, plus the fastest available socket lister - `netstat`
(macOS, built-in), `ss` (Linux, iproute2) or `lsof` (universal fallback; also
used on macOS to resolve process cwds). Bash 3.2+ (stock macOS works).

## Configure

Plugins cannot inject sidebar rows or keybindings (herdr plugin v1), so add to
your `config.toml`:

```toml
# Show the badge next to the Space title
[ui.sidebar.spaces]
rows = [["state_icon", "workspace", "$ports"], ["branch", "git_status"]]

# Open the popup with prefix+a
[[keys.command]]
key = "prefix+a"
type = "plugin_action"
command = "numbered.ports.open"
```

Then `herdr server reload-config`.

## Popup

```
      Space  Program              Ports Path             Pid    Mem  Cpu%
▌ [ ] webapp next-server (v16)    :3000 ~/dev/webapp   48213   305M   1.2
  [x] api    bun run src/index.ts :8080 ~/dev/api      48377    64M   0.0

  ↑↓ move · space check · a all · r refresh
                ↵ kill    esc close
```

The table spans the pane, btop-style: Space and Ports hug their content,
Program and Path share the rest, Pid, Mem and Cpu% sit flush right. A row is any
process holding a TCP `LISTEN` socket whose cwd sits in a workspace pane's cwd
(no process-name filter); `a` lists every listener on the machine. As the pane
narrows, columns drop in order (Program, Mem and Cpu%, Path, Pid), then Ports
and Space crop; long lists scroll with the
cursor. The table refreshes itself every `HERDR_PORTS_REFRESH` seconds (default
3, `0` disables): one socket dump detects new or dead servers, one `ps` updates
Mem and Cpu%, and only the screen lines that changed are repainted. Colors stay subtle: accent ports, green spaces, dim pid and command.

The footer mimics herdr's native settings modal: a dim hint line (replaced by
the outcome of the last kill), then CTA chips - accent `↵ kill`, gray
`esc close`. Set `HERDR_PORTS_ACCENT` (256-color index, default 223) to match
your theme's accent. Hints and chips are all clickable. Mouse: click a row to
check it, use the wheel to move. Keyboard:

- arrows / `j` `k`: move - `space`: check - `enter`: kill checked rows (or the
  highlighted one when none checked); TERM, then the list redraws the instant
  the targets exit (stragglers get KILL in the background), and the Space's
  `$ports` badge clears right away instead of waiting out the metadata TTL
- `a`: include listeners outside herdr workspaces - `r`: refresh - `esc` / `q`: quit

## How the badge works

`herdr-ports watch` polls every 5s (`HERDR_PORTS_INTERVAL`) and posts a
`ports=↯` token (`HERDR_PORTS_BADGE`) as workspace metadata with a TTL,
so the badge clears itself shortly after the last server dies. Nerd Font
glyphs cannot be used here: herdr strips Private Use Area characters from
metadata tokens. The watcher is a singleton started automatically by a
`pane.created` event hook - no daemon setup needed.

## CLI

```sh
herdr plugin action invoke open --plugin numbered.ports   # open the popup
./herdr-ports list                                        # one-shot table
./herdr-ports watch                                       # run the poller in foreground
```
