<script>
  export let percentage = 0;
  export let size = 120;
  export let strokeWidth = 10;
  export let color = 'var(--success-500)'; // Accessible green
  export let bgColor = 'var(--gray-200)'; // Light gray track
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
    <span class="text-2xl font-bold text-gray-900">{percentage}%</span>
    {#if label}
      <span class="text-xs text-gray-500">{label}</span>
    {/if}
  </div>
</div>
