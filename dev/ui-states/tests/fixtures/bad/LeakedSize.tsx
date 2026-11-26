// expect: leaked-zero
export function Tags({ tags }: { tags: Set<string> }) {
  return <div>{tags.size && <TagList tags={[...tags]} />}</div>;
}
