<script>
  import { Copy, Check, Hash } from 'lucide-svelte';
  
  export let hash = '';
  export let label = 'Hash';
  export let truncate = true;
  export let copyable = true;
  
  let copied = false;
  
  $: displayHash = truncate && hash.length > 20 
    ? `${hash.slice(0, 10)}...${hash.slice(-8)}`
    : hash;
  
  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(hash);
      copied = true;
      setTimeout(() => copied = false, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }
</script>

<div class="inline-flex items-center gap-2 bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2">
  <Hash class="w-4 h-4 text-emerald-500 flex-shrink-0" />
  <div class="flex flex-col">
    {#if label}
      <span class="text-xs text-slate-500">{label}</span>
    {/if}
    <code class="text-sm text-slate-300 font-mono">{displayHash}</code>
  </div>
  {#if copyable}
    <button
      on:click={copyToClipboard}
      class="ml-2 p-1 rounded hover:bg-slate-700 transition-colors"
      title="Copy to clipboard"
    >
      {#if copied}
        <Check class="w-4 h-4 text-emerald-400" />
      {:else}
        <Copy class="w-4 h-4 text-slate-400" />
      {/if}
    </button>
  {/if}
</div>
