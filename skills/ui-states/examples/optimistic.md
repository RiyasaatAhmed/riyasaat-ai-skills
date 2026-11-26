# Examples: Optimistic updates

TanStack Query and React 19 `useOptimistic`. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Optimistic update → roll back the item, loudly

**Before:** if the save fails, nothing tells the user. The checkbox stays checked until the next refetch silently flips it back.

```tsx
const toggle = useMutation({
  mutationFn: (todo: Todo) => saveTodo({ ...todo, done: !todo.done }),
  onMutate: (todo) => {
    queryClient.setQueryData<Todo[]>(['todos'], (old) =>
      old?.map((t) => (t.id === todo.id ? { ...t, done: !t.done } : t)),
    );
  },
});
```

**After:** each row owns its mutation, so the error shows by that item. A failure rolls back only that item, so an overlapping toggle on another row survives. The list refetches only when the last running toggle settles, so overlapping toggles don't flicker.

```tsx
function TodoRow({ todo }: { todo: Todo }) {
  const queryClient = useQueryClient();
  const toggle = useMutation({
    mutationKey: ['toggle-todo'],
    mutationFn: (done: boolean) => saveTodo({ ...todo, done }),
    onMutate: async (done) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      setDone(queryClient, todo.id, done);
    },
    onError: (_error, done) => setDone(queryClient, todo.id, !done),
    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: ['toggle-todo'] }) === 1) {
        queryClient.invalidateQueries({ queryKey: ['todos'] });
      }
    },
  });

  return (
    <li>
      <label>
        <input type="checkbox" checked={todo.done} onChange={() => toggle.mutate(!todo.done)} />
        {todo.title}
      </label>
      <span role="alert">
        {toggle.isError && (
          <>Couldn't save. <button onClick={() => toggle.mutate(toggle.variables!)}>Retry</button></>
        )}
      </span>
    </li>
  );
}

function setDone(queryClient: QueryClient, id: string, done: boolean) {
  queryClient.setQueryData<Todo[]>(['todos'], (old) => old?.map((t) => (t.id === id ? { ...t, done } : t)));
}
```

With React 19 `useOptimistic`:

- **Setter:** call it inside `startTransition`.
- **Show failures yourself:** the revert on failure is silent, so catch the error.
- **Update the real value on success:** when the transition ends, the optimistic value goes back to the prop. The checkbox snaps back unless the parent's data changed.

```tsx
function TodoCheckbox({ todo, onSaved }: { todo: Todo; onSaved: (saved: Todo) => void }) {
  const [done, setOptimisticDone] = useOptimistic(todo.done);
  const [failed, setFailed] = useState(false);

  function toggle() {
    startTransition(async () => {
      setFailed(false);
      setOptimisticDone(!done);
      try {
        const saved = await saveTodo({ ...todo, done: !done });
        startTransition(() => onSaved(saved)); // or a Server Action that revalidates, or router.refresh()
      } catch {
        setFailed(true);
      }
    });
  }

  return (
    <>
      <input type="checkbox" checked={done} onChange={toggle} />
      <span role="alert">{failed ? "Couldn't save. Try again." : ''}</span>
    </>
  );
}
```
