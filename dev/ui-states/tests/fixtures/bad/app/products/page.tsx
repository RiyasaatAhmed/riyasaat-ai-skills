// expect: no-error-state
export default async function ProductsPage() {
  const res = await fetch('https://api.example.com/products', { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const products: Product[] = await res.json();
  return products.length === 0 ? <ProductsEmpty /> : <ProductGrid products={products} />;
}
