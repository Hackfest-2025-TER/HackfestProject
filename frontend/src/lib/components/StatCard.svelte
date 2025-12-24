<script lang="ts">
  import type { ComponentType } from 'svelte';
  
  export let title = 'Stat';
  export let value = '0';
  export let subtitle = '';
  export let icon: ComponentType | null = null;
  export let trend: 'up' | 'down' | null = null;
  export let trendValue = '';
  export let color = 'emerald'; // emerald, blue, purple, amber, red
  
  const colors = {
    emerald: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400',
      icon: 'text-emerald-500'
    },
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      icon: 'text-blue-500'
    },
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      text: 'text-purple-400',
      icon: 'text-purple-500'
    },
    amber: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      icon: 'text-amber-500'
    },
    red: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      text: 'text-red-400',
      icon: 'text-red-500'
    }
  };
  
  $: colorClasses = colors[color] || colors.emerald;
</script>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-colors">
  <div class="flex items-start justify-between">
    <div>
      <p class="text-sm text-slate-400 mb-1">{title}</p>
      <p class="text-3xl font-bold text-white">{value}</p>
      {#if subtitle}
        <p class="text-sm text-slate-500 mt-1">{subtitle}</p>
      {/if}
      {#if trend && trendValue}
        <div class="flex items-center gap-1 mt-2">
          {#if trend === 'up'}
            <span class="text-emerald-400 text-sm">↑ {trendValue}</span>
          {:else}
            <span class="text-red-400 text-sm">↓ {trendValue}</span>
          {/if}
        </div>
      {/if}
    </div>
    {#if icon}
      <div class="{colorClasses.bg} {colorClasses.border} border rounded-lg p-3">
        <svelte:component this={icon} class="w-6 h-6 {colorClasses.icon}" />
      </div>
    {/if}
  </div>
</div>
