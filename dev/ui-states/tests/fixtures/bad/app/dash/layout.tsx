// expect: no-error-state, fetch-no-ok
export default async function Layout({ children }) {
  const res = await fetch('https://api.example.com/me');
  const me = await res.json();
  return <div><Header user={me} />{children}</div>;
}
