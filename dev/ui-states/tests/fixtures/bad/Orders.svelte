<!-- expect: await-no-catch, each-no-else -->
<script>
  let { orders } = $props();
</script>

{#await orders then list}
  {#each list as order}
    <OrderRow {order} />
  {/each}
{/await}
