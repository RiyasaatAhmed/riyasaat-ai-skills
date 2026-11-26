// expect: empty-default, leaked-zero, no-error-state
export function Vendors() {
  const { data = [] } = useQuery({ queryKey: ['v'], queryFn: getVendors });
  return <ul>{data.length && data.map((v) => <li key={v.id}>{v.name}</li>)}</ul>;
}
