// expect: no-error-state
export function Users() {
  const [users, setUsers] = useState<User[] | undefined>();
  useEffect(() => {
    fetch('/api/users')
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setUsers);
  }, []);
  if (!users) return <Skeleton />;
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
