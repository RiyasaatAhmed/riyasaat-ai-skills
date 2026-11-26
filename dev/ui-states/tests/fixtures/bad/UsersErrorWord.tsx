// expect: no-error-state
export function Users() {
  const [users, setUsers] = useState(null);
  useEffect(() => { fetch('/api/users').then((r) => r.ok && r.json()).then(setUsers); }, []);
  if (!users) return <div className="error-free-skeleton"><Skeleton /></div>;
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
