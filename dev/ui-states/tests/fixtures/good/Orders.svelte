<!-- expect: -->
<script>
  let { orders, reload } = $props();
</script>

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
