// expect: no-error-state
export function Gallery() {
  const { data } = useQuery({ queryKey: ['photos'], queryFn: getPhotos });
  if (!data) return <Skeleton />;
  return <PhotoGrid photos={data} onError={logToSentry} />;
}
