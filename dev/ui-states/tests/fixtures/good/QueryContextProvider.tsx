// expect:
import { useQuery, UseQueryResult } from 'react-query';

const OrdersContext = createContext<UseQueryResult<Order[]> | undefined>(undefined);

export function OrdersProvider({ children }) {
  const query = useQuery<Order[]>('orders', () => axios.get('/api/orders').then((r) => r.data));
  return <OrdersContext.Provider value={{ ...query }}>{children}</OrdersContext.Provider>;
}
