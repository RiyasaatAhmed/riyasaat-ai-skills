// expect:
// Patterns that look like happy-path code but are fine. Found while running the checker on real apps.
import { useQuery } from '@apollo/client';

export function useCustomers(QUERY) {
  const result = useQuery(QUERY); // passed on whole, so the error travels with it
  return result;
}

export function CustomFields({ fields, customer, onRefresh }) {
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem('filters') ?? '{}');
  } catch {}

  async function submit(response: Response) {
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.message ?? `HTTP ${response.status}`);
    }
  }

  function refresh() {
    try {
      onRefresh();
    } catch {
      // The parent shows its own error state, so nothing is lost here.
    }
  }

  const fetch = () => onRefresh();
  fetch();

  return <div>{fields?.length && customer?.fields?.length ? <FieldList fields={fields} /> : null}</div>;
}
