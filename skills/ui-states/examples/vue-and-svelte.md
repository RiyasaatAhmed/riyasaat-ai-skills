# Examples: Vue and Svelte

The same states outside React. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Vue → the same states in a template

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';

const orders = ref<Order[] | undefined>(undefined);
const failed = ref(false);

async function load() {
  failed.value = false;
  try {
    const res = await fetch('/api/orders', { signal: AbortSignal.timeout(10_000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    orders.value = await res.json();
  } catch {
    failed.value = true;
  }
}

onMounted(load);
</script>

<template>
  <template v-if="orders !== undefined">
    <Notice v-if="failed">Couldn't refresh. <button @click="load">Retry</button></Notice>
    <OrdersEmpty v-if="orders.length === 0" />
    <OrderList v-else :orders="orders" />
  </template>
  <InlineError v-else-if="failed" message="Couldn't load orders." @retry="load" />
  <OrdersSkeleton v-else />
</template>
```

## Svelte → every block has its other branch

**Before:**

```svelte
{#await orders then list}
  {#each list as order}
    <OrderRow {order} />
  {/each}
{/await}
```

**After:**

```svelte
{#await orders}
  <OrdersSkeleton />
{:then list}
  {#each list as order (order.id)}
    <OrderRow {order} />
  {:else}
    <OrdersEmpty />
  {/each}
{:catch}
  <InlineError message="Couldn't load orders." onretry={reload} />
{/await}
```
