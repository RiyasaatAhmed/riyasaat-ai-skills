# Examples: Forms

Submit buttons and unsaved changes. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Submit button → busy, not disabled

**Before:** `disabled` drops keyboard focus if the button had it. The label never changes, so the user can't tell what is happening.

```tsx
<button type="submit" disabled={saving}>Save</button>
```

**After:** the button stays focusable, says it is busy, and a second click does nothing.

```tsx
function onSubmit(event: React.FormEvent) {
  event.preventDefault();
  if (saving) return;
  save();
}

<button type="submit" aria-disabled={saving}>
  {saving ? 'Saving…' : 'Save'}
</button>
```

Give the busy state a visible style, or the button still looks clickable:

```css
button[aria-disabled='true'] { opacity: 0.6; cursor: progress; }
```

If the API accepts an idempotency key, send one, so a double submit that gets through is still safe on the server.

## Unsaved changes → warn before leaving

```tsx
useEffect(() => {
  if (!dirty) return;
  const warn = (event: BeforeUnloadEvent) => event.preventDefault();
  window.addEventListener('beforeunload', warn);
  return () => window.removeEventListener('beforeunload', warn);
}, [dirty]);
```

This covers closing the tab and reloading. For in-app navigation, use the router's blocker if it has one, like React Router's `useBlocker`. If it has none, say so in your report instead of inventing one.
