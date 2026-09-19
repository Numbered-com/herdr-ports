import pathlib
import subprocess
import unittest


class DetectionTest(unittest.TestCase):
    def test_nested_worktrees_do_not_inherit_parent_listeners(self):
        source = pathlib.Path(__file__).with_name('herdr-ports').read_text()
        functions = source.split('\ncase "${1:-}" in')[0]
        scenario = r'''
set -e
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
workspace_cwds() {
    printf 'root\t/project\nactive\t/project/.worktrees/active\nidle\t/project/.worktrees/idle\n'
}
HERDR=mock_herdr
mock_herdr() {
    printf '%s\n' '{"result":{"workspaces":[
      {"workspace_id":"root","label":"Root","worktree":{"repo_key":"repo","is_linked_worktree":false}},
      {"workspace_id":"active","label":"Active","worktree":{"repo_key":"repo","is_linked_worktree":true}},
      {"workspace_id":"idle","label":"Idle","worktree":{"repo_key":"repo","is_linked_worktree":true}}
    ]}}'
}
pid_ports() { printf '123\t3000\n'; }
pid_cwds() { cat >/dev/null; printf '123\t%s\n' "$resolved"; }
ps_each() { printf '123 1024 0.0 server\n'; }
for resolved in /project /project/apps/web /project/.worktrees/active/apps/web /project-other /; do
    case "$resolved" in
        /project/.worktrees/active/*) expected=active; label=Root; tree=Active ;;
        /project|/project/apps/web) expected=root; label=Root; tree=- ;;
        *) expected=''; label=-; tree=- ;;
    esac
    build_rows "$tmp" > "$tmp/rows"
    [ "$(active_workspaces)" = "$expected" ]
    [ "$(cut -f1 "$tmp/rows")" = "$label" ]
    [ "$(cut -f9 "$tmp/rows")" = "$tree" ]
done
workspace_cwds() { :; }
[ -z "$(active_workspaces)" ]
'''
        result = subprocess.run(['bash', '-c', functions + scenario], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_popup_tracks_watcher_when_listener_cwd_changes(self):
        source = pathlib.Path(__file__).with_name('herdr-ports').read_text()
        functions = source.split('\ncase "${1:-}" in')[0]
        scenario = r'''
set -e
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
workspace_cwds() { printf 'w1\t/project\n'; }
workspace_labels() { printf 'w1\tProject\n'; }
pid_ports() { printf '123\t3000\n'; }
pid_cwds() { cat >/dev/null; [ -z "$resolved" ] || printf '123\t%s\n' "$resolved"; }
ps_each() { printf '123 1024 0.0 server\n'; }
for resolved in '' /project /elsewhere /project/subdir ''; do
    build_rows "$tmp" > "$tmp/rows"
    badge=$(active_workspaces)
    space=$(cut -f1 "$tmp/rows")
    case "$resolved" in
        /project*) [ "$badge" = w1 ] && [ "$space" = Project ] ;;
        *) [ -z "$badge" ] && [ "$space" = - ] ;;
    esac
done
'''
        result = subprocess.run(['bash', '-c', functions + scenario], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
