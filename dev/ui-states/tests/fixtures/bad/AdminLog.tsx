// expect: no-error-state
export function AdminLog() {
  const { data } = useQuery({ queryKey: ['log'], queryFn: getLog });
  if (!data) return <Skeleton />;
  return <section><h2>Error log</h2><LogTable rows={data} /></section>;
}
