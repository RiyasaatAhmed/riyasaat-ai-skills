// expect:
import { AxiosError } from 'axios';

export function NetworkErrorState({ error }: { error: AxiosError }) {
  return <p>Couldn't reach the server ({error.code}).</p>;
}
