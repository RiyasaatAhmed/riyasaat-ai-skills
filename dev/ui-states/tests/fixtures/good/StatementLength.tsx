// expect:
export function useTrack(items) {
  useEffect(() => { items.length && track(items); }, [items]);
  return <span>{items.length > 0 ? 'Tracked' : 'Nothing to track'}</span>;
}
