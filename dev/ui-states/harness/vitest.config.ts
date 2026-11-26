import { defineConfig } from 'vitest/config';
export default defineConfig({
  
  test: { environment: 'jsdom', testTimeout: 45_000, include: ['users.test.tsx', 'orders.test.tsx'], reporters: ['default'] },
});
