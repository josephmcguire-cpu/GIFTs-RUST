#!/usr/bin/env bash
# Run a command with npm on PATH. GNU Make uses a minimal environment where Homebrew,
# nvm, Volta, or fnm may not be loaded — load them here before exec.
#
# Optional: export NPM=/full/path/to/npm  (or: make docs-build NPM="$(command -v npm)")
set -eo pipefail
# Note: do not use "set -u" — sourcing nvm/asdf often breaks with nounset.

_prepend_npm_dir() {
	local _p="$1"
	[[ -n "$_p" && -x "$_p" ]] || return 1
	export PATH="$(dirname "$_p"):$PATH"
	return 0
}

if [[ -n "${NPM:-}" && -x "$NPM" ]]; then
	_prepend_npm_dir "$NPM"
fi

# macOS: do this *before* nvm/Homebrew PATH hacks — many setups only define npm in ~/.zprofile / ~/.zshrc
if [[ "$(uname -s)" == "Darwin" ]] && ! command -v npm &>/dev/null; then
	# zsh login+interactive loads the same startup files as Terminal.app for most users
	while IFS= read -r _line; do
		[[ -z "$_line" ]] && continue
		[[ "$_line" == /* ]] || continue
		[[ -x "$_line" ]] || continue
		_prepend_npm_dir "$_line" && break
	# type -P resolves a real path even when npm is an nvm shell function (command -v may not print /…/npm)
	done < <(/bin/zsh -il -c 'type -P npm' 2>/dev/null)
fi

if ! command -v npm &>/dev/null; then
	# nvm (bash-oriented)
	export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
	for _nvm in "$NVM_DIR/nvm.sh" "$HOME/.config/nvm/nvm.sh"; do
		if [[ -s "$_nvm" ]]; then
			# shellcheck source=/dev/null
			source "$_nvm" || true
			break
		fi
	done
fi

# asdf (optional)
if [[ -f "$HOME/.asdf/asdf.sh" ]]; then
	# shellcheck source=/dev/null
	source "$HOME/.asdf/asdf.sh" || true
fi

# mise, Linuxbrew, macOS Homebrew, Volta
export PATH="$HOME/.local/bin:/home/linuxbrew/.linuxbrew/bin:$HOME/.volta/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

if command -v mise &>/dev/null; then
	# shellcheck disable=SC2046
	eval "$(mise env -s bash 2>/dev/null)" || eval "$(mise activate bash 2>/dev/null)" || true
fi

if command -v fnm &>/dev/null; then
	# shellcheck disable=SC2046
	eval "$(fnm env --shell bash 2>/dev/null)" || true
fi

_script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
_repo_root=$(cd "$_script_dir/.." && pwd)
if [[ -f "$_repo_root/docs-site/.nvmrc" ]] && type nvm &>/dev/null; then
	pushd "$_repo_root/docs-site" >/dev/null || exit 1
	nvm install 2>/dev/null || true
	nvm use || true
	popd >/dev/null || true
fi

_resolve_npm_from_login_shells() {
	local _p
	_p=$(/bin/bash -lic 'type -P npm' 2>/dev/null) || true
	if [[ -n "$_p" && -x "$_p" ]]; then
		export PATH="$(dirname "$_p"):$PATH"
		return 0
	fi
	return 1
}

if ! command -v npm &>/dev/null; then
	_resolve_npm_from_login_shells || true
fi

if ! command -v npm &>/dev/null; then
	echo "docs-with-npm.sh: npm not found." >&2
	echo "  Install Node.js 18+: https://nodejs.org/  or:  brew install node" >&2
	echo "  Or from a shell where npm works:  make docs-build NPM=\"\$(command -v npm)\"" >&2
	echo "  Or use Docker (no local Node):      make docs-docker-build" >&2
	exit 127
fi

exec "$@"
