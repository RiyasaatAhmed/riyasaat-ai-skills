# Examples: Long text and images

Wrapping, missing fields, dates, and image fallbacks. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Long text → wraps instead of breaking

**Before:** a long translated label is cut off, and a pasted URL overflows the row.

```css
.tag  { width: 80px; white-space: nowrap; overflow: hidden; }
.name { white-space: nowrap; margin-left: 8px; }
```

**After:** text wraps, and the logical property flips for right-to-left languages.

```css
.tag  { max-width: 100%; overflow-wrap: anywhere; }
.row > .name { min-width: 0; overflow-wrap: anywhere; margin-inline-start: 8px; } /* lets a flex child shrink */
.description {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
} /* plus a "Show more" button */
```

Missing fields get a placeholder, never the raw value:

```tsx
<dd>{user.email ?? 'Not provided'}</dd>
```

Dates rendered on the server and the client must come out the same. The server often doesn't know the user's time zone, so pick one honest option:

```tsx
// (a) A time zone stored on the user's profile:
new Intl.DateTimeFormat(user.locale, { dateStyle: 'medium', timeZone: user.timeZone }).format(order.createdAt)

// (b) Format on the client only, after mount:
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);
<time dateTime={order.createdAt.toISOString()}>{mounted ? formatLocal(order.createdAt) : ''}</time>

// (c) Render UTC, and say so:
new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC' }).format(order.createdAt) + ' UTC'
```

## Images → a fallback and a fixed size

```tsx
function Avatar({ src, name }: { src?: string; name: string }) {
  const [failed, setFailed] = useState(false);
  const img = useRef<HTMLImageElement>(null);

  useEffect(() => setFailed(false), [src]); // a reused row with a new src gets a fresh try
  useEffect(() => {
    // With server rendering, the image can fail before hydration, so onError never fires.
    if (img.current?.complete && img.current.naturalWidth === 0) setFailed(true);
  }, [src]);

  return src && !failed
    ? <img ref={img} src={src} alt="" width={40} height={40} onError={() => setFailed(true)} />
    : <span className="avatar-fallback" aria-hidden="true">{initials(name)}</span>;
}
```

`alt=""` and `aria-hidden` because the name is shown next to it. `.avatar-fallback` has the same 40 × 40 size, so nothing shifts.
