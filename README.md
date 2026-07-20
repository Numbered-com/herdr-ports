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

Requirements: `jq`, and `lsof` (macOS/Linux) or `ss` (Linux). Bash 3.2+ (stock
macOS works).

## Configure

Plugins cannot inject sidebar rows or keybindings (herdr plugin v1), so add to
your `config.toml`:

```toml
# Show the badge on Space rows
[ui.sidebar.spaces]
rows = [["state_icon", "workspace"], ["branch", "git_status", "$ports"]]

# Open the popup with prefix+a
[[keys.command]]
key = "prefix+a"
type = "plugin_action"
command = "numbered.ports.open"
```

Then `herdr server reload-config`.

## Popup

```
      SPACE        PORTS          PID     PATH                           COMMAND
> [ ] micadoni     :4461          43520   ~/.../micadoni/apps/web        next-server (v16.2.10)
  [x] micadoni     :4839          43492   ~/.../micadoni/apps/sanity     node .../node_modules/.bin
```

Mouse: click a row to check it, use the wheel to move, and click the
`[ Kill ] [ Refresh ] [ All listeners ] [ Quit ]` buttons. Keyboard:

- arrows / `j` `k`: move - `space`: check - `enter`: kill checked rows (or the
  highlighted one when none checked); TERM first, KILL after 2s
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
