#!/bin/sh
# Triggering eval: does ui-states load by itself? Needs the claude CLI, signed in.
# Usage: sh dev/ui-states/harness/trigger.sh   (from the repo root)
set -e
work=$(mktemp -d)
mkdir -p "$work/.claude/skills" && cp -R skills/ui-states "$work/.claude/skills/"
cd "$work" && git init -q
echo '{"name":"shop","dependencies":{"react":"^19.2.0","next":"^16.3.0"}}' > package.json
mkdir -p src/orders
printf 'export default function OrdersPage() {\n  return <div>Orders</div>;\n}\n' > src/orders/page.tsx
printf 'export function Button({ kind, children }) {\n  return <button className={kind}>{children}</button>;\n}\n' > src/Button.tsx
while IFS='|' read -r expect prompt; do
  loaded=no
  claude -p "$prompt" --output-format stream-json --verbose --permission-mode plan --max-turns 4 < /dev/null 2>/dev/null \
    | grep -q '"name":"Skill","input":{"skill":"ui-states"' && loaded=yes
  ok=BAD; { [ "$expect" = load ] && [ $loaded = yes ]; } || { [ "$expect" = skip ] && [ $loaded = no ]; } && ok=OK
  echo "$ok expect=$expect loaded=$loaded  $prompt"
done <<'PROMPTS'
load|Show a list of users from /api/users.
load|Add a search box for orders.
load|Build a settings form that saves to /api/settings.
load|Review src/orders/page.tsx for missing states.
skip|Render the nav links from this array: const links = [{ href: '/', label: 'Home' }, { href: '/about', label: 'About' }].
skip|Fix the typo in the empty state text: 'No ordres yet'.
skip|Rename the Button component's kind prop to variant.
skip|Write a utility that formats a price in cents as dollars.
PROMPTS
