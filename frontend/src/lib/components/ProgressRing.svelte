<script>
  export let percentage = 0;
  export let size = 120;
  export let strokeWidth = 10;
  export let color = '#10b981'; // emerald-500
  export let bgColor = '#334155'; // slate-700
  export let label = '';
  
  $: radius = (size - strokeWidth) / 2;
  $: circumference = 2 * Math.PI * radius;
  $: offset = circumference - (percentage / 100) * circumference;
</script>

<div class="relative inline-flex items-center justify-center" style="width: {size}px; height: {size}px;">
  <svg class="transform -rotate-90" width={size} height={size}>
    <!-- Background circle -->
    <circle
      cx={size / 2}
      cy={size / 2}
      r={radius}
      fill="none"
      stroke={bgColor}
      stroke-width={strokeWidth}
    />
    <!-- Progress circle -->
    <circle
      cx={size / 2}
      cy={size / 2}
      r={radius}
      fill="none"
      stroke={color}
      stroke-width={strokeWidth}
      stroke-linecap="round"
      stroke-dasharray={circumference}
      stroke-dashoffset={offset}
      class="transition-all duration-500 ease-out"
    />
  </svg>
  <div class="absolute inset-0 flex flex-col items-center justify-center">
    <span class="text-2xl font-bold text-white">{percentage}%</span>
    {#if label}
      <span class="text-xs text-slate-400">{label}</span>
    {/if}
  </div>
</div>
