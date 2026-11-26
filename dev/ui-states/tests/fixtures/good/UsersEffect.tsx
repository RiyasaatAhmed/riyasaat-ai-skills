// expect:
import { useEffect, useState } from 'react';

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'success'; users: User[] };

export function Users() {
  const [state, setState] = useState<State>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading' });
    fetch('/api/users', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<User[]>;
      })
      .then((users) => setState({ status: 'success', users }))
      .catch((err) => {
        if (err.name !== 'AbortError') setState({ status: 'error' });
      });
    return () => controller.abort();
  }, [attempt]);

  switch (state.status) {
    case 'loading':
      return <UserListSkeleton rows={6} />;
    case 'error':
      return <InlineError message="Couldn't load users." onRetry={() => setAttempt((n) => n + 1)} />;
    case 'success':
      return state.users.length === 0
        ? <EmptyState title="No teammates yet" action={<InviteButton />} />
        : <UserList users={state.users} />;
  }
}
