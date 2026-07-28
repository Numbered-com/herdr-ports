# herdr-ports

Surface active dev servers in [herdr](https://herdr.dev): a generic `$ports`
badge on every Space running at least one TCP listener, and a popup to inspect
and kill them. Working on several projects at once, it answers "which space
has a live server?" at a glance.

Ports are attributed to a Space by **process ancestry** first: a listener whose
parent chain reaches a pane's shell (`herdr pane process-info` → `shell_pid`)
belongs to that pane's Space, full stop. This is what lets you run the same app
in several Spaces at once - three copies of one server started from the same
worktree directory land in three different Spaces, because their shells differ
even though their cwds are identical.

Listeners with no pane ancestor - system daemons, docker, anything started
outside herdr - fall back to matching the process cwd against the cwds of the
workspace's panes, which is what that heuristic is genuinely good at. System
daemons (cwd `/`, `~/Library`, ...) never match, so the default view stays
clean. On the fallback path exactly one Space still wins: candidates are ranked
exact cwd match, then listener under a pane cwd, then the reverse, ties broken
by the deepest pane cwd, so a Space parked at `$HOME` only claims a server when
nothing more specific matched.

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

### A row per port

The watcher also posts one `$portN` token per listening port (`:3000 next-server`),
so the Space can list its servers instead of just flagging them:

```toml
[ui.sidebar.spaces]
rows = [
  ["state_icon", "workspace"],
  ["branch", "git_status"],
  ["$port1"], ["$port2"], ["$port3"], ["$port4"], ["$port5"],
]
```

herdr drops any row whose tokens all resolve to nothing and sizes the Space
card from the surviving rows, so the card grows and shrinks with the live port
count - a Space with one server shows one row, a Space with none shows none.

The **maximum** is not dynamic: herdr resolves a fixed list of row templates,
so a Space can never render more rows than you declare here. `HERDR_PORTS_ROWS`
(default 5) tells the watcher how many slots to fill and must match the number
of `$portN` rows above; a Space with more listeners than that shows the
lowest-numbered ports and drops the rest. Keep it at 15 or below - a metadata
report may carry at most 16 tokens and `$ports` uses one.

## Popup

```
      SPACE        PORTS          PID     PATH                           COMMAND
> [ ] webapp       :3000          48213   ~/dev/webapp                   next-server (v16)
  [x] api          :8080          48377   ~/dev/api                      bun run src/index.ts

  ↑↓ move · space check · a all · r refresh
                ↵ kill    esc close
```

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
