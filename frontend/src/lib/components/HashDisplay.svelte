<script>
  import { Copy, Check, FileText } from "lucide-svelte";

  export let hash = "";
  export let label = "Reference ID";
  export let truncate = true;
  export let copyable = true;

  let copied = false;

  $: displayHash =
    truncate && hash.length > 16
      ? `${hash.slice(0, 8)}...${hash.slice(-6)}`
      : hash;

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(hash);
      copied = true;
      setTimeout(() => (copied = false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  }
</script>

<div
  class="inline-flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-left"
>
  <div class="flex flex-col">
    {#if label}
      <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
        >{label}</span
      >
    {/if}
    <code
      class="text-xs text-gray-700 font-mono bg-gray-100 px-1 py-0.5 rounded"
      >{displayHash}</code
    >
  </div>
  {#if copyable}
    <button
      on:click={copyToClipboard}
      class="ml-1 p-1.5 rounded-md hover:bg-gray-200 transition-colors focus:ring-2 focus:ring-primary-500 outline-none"
      title="Copy to clipboard"
    >
      {#if copied}
        <Check class="w-4 h-4 text-success-600" />
      {:else}
        <Copy class="w-4 h-4 text-gray-400 hover:text-gray-600" />
      {/if}
    </button>
  {/if}
</div>
