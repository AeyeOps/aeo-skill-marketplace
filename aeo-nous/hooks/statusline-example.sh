#!/bin/bash
# Example Visual Statusline for Claude Code
#
# This is an OPTIONAL visual statusline bundled with aeo-nous. It renders a
# compact terminal status bar showing context %, git info, lines changed, and
# model name. You do NOT need this for nous to function -- only the activity
# logger (nous-logger.sh) is required.
#
# To use this as your visual statusline, point your wrapper's ORIGINAL_CMD
# at this script, or set it directly in ~/.claude/settings.json.

input=$(cat)

# --- Extract Fields ---------------------------------------------------------------
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
lines_added=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
lines_removed=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')
pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
[ "$pct" = "null" ] || [ -z "$pct" ] && pct=0

# --- Progress Bar -----------------------------------------------------------------
bar_width=6
filled=$((pct * bar_width / 100))
[ $filled -gt $bar_width ] && filled=$bar_width
bar=""
[ $filled -gt 0 ] && bar+="\033[36m$(printf "%${filled}s" | tr ' ' '=')\033[0m"
empty=$((bar_width - filled))
[ $empty -gt 0 ] && bar+="\033[90m$(printf "%${empty}s" | tr ' ' '-')\033[0m"

if [ $pct -lt 50 ]; then pct_color="\033[32m"
elif [ $pct -lt 75 ]; then pct_color="\033[33m"
elif [ $pct -lt 90 ]; then pct_color="\033[38;5;208m"
else pct_color="\033[31m"; fi

# --- Lines +/- --------------------------------------------------------------------
lines_info=""
if [ "$lines_added" -gt 0 ] || [ "$lines_removed" -gt 0 ]; then
    lines_info=" \033[32m+${lines_added}\033[0m\033[31m-${lines_removed}\033[0m"
fi

# --- PWD --------------------------------------------------------------------------
short_pwd="?"
if [ -n "$cwd" ]; then
    short_pwd=$(basename "$cwd")
    [ ${#short_pwd} -gt 15 ] && short_pwd="${short_pwd:0:12}..."
fi

# --- Git --------------------------------------------------------------------------
git_info=""
if [ -n "$cwd" ] && [ -d "$cwd" ] && git -C "$cwd" rev-parse --git-dir &>/dev/null; then
    branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
    [ ${#branch} -gt 12 ] && branch="${branch:0:10}.."
    git_info="\033[35m$branch\033[0m"
    staged=$(git -C "$cwd" diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
    modified=$(git -C "$cwd" diff --numstat 2>/dev/null | wc -l | tr -d ' ')
    untracked=$(git -C "$cwd" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
    [ "$staged" -gt 0 ] && git_info+=" \033[32m+$staged\033[0m"
    [ "$modified" -gt 0 ] && git_info+="\033[33m~$modified\033[0m"
    [ "$untracked" -gt 0 ] && git_info+="\033[90m?$untracked\033[0m"
fi

# --- Model ------------------------------------------------------------------------
short_model=$(echo "$model_name" | sed 's/Claude //' | cut -c1-6)

# --- Render -----------------------------------------------------------------------
printf "\033[34m%s\033[0m" "$short_pwd"
[ -n "$git_info" ] && printf " │ %b" "$git_info"
printf " │ [%b]%b%d%%\033[0m%b" "$bar" "$pct_color" "$pct" "$lines_info"
printf " │ \033[36m%s\033[0m" "$short_model"
