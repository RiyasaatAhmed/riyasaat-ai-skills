// expect: async-handler-no-try
export function Toolbar({ save }) {
  return <button onClick={async () => { await save(); }}>Save</button>;
}
