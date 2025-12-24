<script>
  import { onMount } from 'svelte';
  import { Link, Hash, Clock, CheckCircle } from 'lucide-svelte';
  
  export let blocks = [];
  
  let animatedBlocks = [];
  
  onMount(async () => {
    // If no blocks provided, fetch from API
    if (blocks.length === 0) {
      try {
        const response = await fetch('http://localhost:8000/api/audit/logs');
        if (response.ok) {
          const logs = await response.json();
          // Convert audit logs to block format
          blocks = logs.slice(0, 10).map((log, index) => ({
            index: index,
            hash: log.block_hash || generateHash(),
            prevHash: log.previous_hash || (index > 0 ? 'prev' : '0000000000'),
            timestamp: log.timestamp || new Date().toISOString(),
            type: log.event_type || 'unknown',
            data: log.manifesto_id || log.data
          }));
        }
      } catch (err) {
        // Use sample data if API fails
        blocks = generateSampleBlocks();
      }
    }
    
    // Animate blocks appearing
    for (let i = 0; i < blocks.length; i++) {
      await new Promise(r => setTimeout(r, 100));
      animatedBlocks = [...animatedBlocks, blocks[i]];
    }
  });
  
  function generateHash() {
    return '0x' + Array.from({length: 16}, () => 
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }
  
  function generateSampleBlocks() {
    return [
      { index: 0, hash: '0x8a3f2c...e91b', prevHash: '0x000000...0000', timestamp: new Date(Date.now() - 86400000 * 5).toISOString(), type: 'genesis', data: 'Genesis Block' },
      { index: 1, hash: '0x2d7b4e...c3a2', prevHash: '0x8a3f2c...e91b', timestamp: new Date(Date.now() - 86400000 * 4).toISOString(), type: 'promise', data: 'Promise #1' },
      { index: 2, hash: '0x9f1c8d...b4e7', prevHash: '0x2d7b4e...c3a2', timestamp: new Date(Date.now() - 86400000 * 3).toISOString(), type: 'vote_batch', data: '250 votes' },
      { index: 3, hash: '0x5e2a9b...d8c1', prevHash: '0x9f1c8d...b4e7', timestamp: new Date(Date.now() - 86400000 * 2).toISOString(), type: 'status_change', data: 'Promise #1 → Kept' },
      { index: 4, hash: '0x7c4f3a...a2b9', prevHash: '0x5e2a9b...d8c1', timestamp: new Date(Date.now() - 86400000).toISOString(), type: 'merkle_root', data: 'Merkle Root Update' },
    ];
  }
  
  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  const typeColors = {
    genesis: 'border-purple-500 bg-purple-500/10',
    promise: 'border-emerald-500 bg-emerald-500/10',
    vote_batch: 'border-blue-500 bg-blue-500/10',
    status_change: 'border-amber-500 bg-amber-500/10',
    merkle_root: 'border-cyan-500 bg-cyan-500/10',
    unknown: 'border-slate-500 bg-slate-500/10'
  };
  
  const typeIcons = {
    genesis: Hash,
    promise: CheckCircle,
    vote_batch: Hash,
    status_change: CheckCircle,
    merkle_root: Link,
    unknown: Hash
  };
</script>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
  <h3 class="text-lg font-semibold text-white mb-6 flex items-center gap-2">
    <Link class="w-5 h-5 text-emerald-400" />
    <span>Blockchain Visualizer</span>
  </h3>
  
  <div class="relative">
    <!-- Connection Line -->
    <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-emerald-500 via-blue-500 to-purple-500 opacity-30"></div>
    
    <!-- Blocks -->
    <div class="space-y-4">
      {#each animatedBlocks as block, i (block.index)}
        <div 
          class="relative flex items-start gap-4 animate-fadeIn"
          style="animation-delay: {i * 100}ms"
        >
          <!-- Block Indicator -->
          <div class="relative z-10 w-12 h-12 rounded-lg border-2 flex items-center justify-center flex-shrink-0 {typeColors[block.type] || typeColors.unknown}">
            <svelte:component this={typeIcons[block.type] || typeIcons.unknown} class="w-5 h-5 text-white" />
          </div>
          
          <!-- Block Content -->
          <div class="flex-1 bg-slate-700/30 rounded-lg p-4 border border-slate-700 hover:border-slate-600 transition-colors">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-white">Block #{block.index}</span>
              <span class="text-xs text-slate-500 flex items-center gap-1">
                <Clock class="w-3 h-3" />
                {formatDate(block.timestamp)}
              </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span class="text-slate-500">Hash:</span>
                <code class="ml-1 text-emerald-400 font-mono">
                  {block.hash.length > 16 ? block.hash.slice(0, 16) + '...' : block.hash}
                </code>
              </div>
              <div>
                <span class="text-slate-500">Prev:</span>
                <code class="ml-1 text-blue-400 font-mono">
                  {block.prevHash.length > 16 ? block.prevHash.slice(0, 16) + '...' : block.prevHash}
                </code>
              </div>
            </div>
            
            <div class="mt-2 pt-2 border-t border-slate-700">
              <span class="text-xs text-slate-400">{block.type}: </span>
              <span class="text-xs text-slate-300">{block.data}</span>
            </div>
          </div>
          
          <!-- Connection Arrow -->
          {#if i < animatedBlocks.length - 1}
            <div class="absolute left-6 top-12 w-0.5 h-4 bg-slate-600"></div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
  
  {#if animatedBlocks.length === 0}
    <div class="text-center py-8">
      <div class="animate-spin w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full mx-auto mb-2"></div>
      <p class="text-slate-400 text-sm">Loading blockchain data...</p>
    </div>
  {/if}
</div>

<style>
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out forwards;
    opacity: 0;
  }
</style>
