<script>
  import { Clock, ThumbsUp, ThumbsDown, Users, Calendar } from 'lucide-svelte';
  
  export let manifesto = {
    id: 1,
    title: 'Promise Title',
    description: 'Promise description',
    politician_name: 'Politician Name',
    category: 'General',
    status: 'pending',
    vote_kept: 0,
    vote_broken: 0,
    grace_period_end: new Date().toISOString(),
    created_at: new Date().toISOString()
  };
  
  $: totalVotes = manifesto.vote_kept + manifesto.vote_broken;
  $: keptPercent = totalVotes > 0 ? Math.round((manifesto.vote_kept / totalVotes) * 100) : 0;
  $: isLocked = new Date(manifesto.grace_period_end) > new Date();
  
  $: daysRemaining = Math.max(0, Math.ceil((new Date(manifesto.grace_period_end).getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
  
  const statusColors = {
    pending: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    kept: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
    broken: 'bg-red-500/10 text-red-600 border-red-500/20'
  };
  
  const categoryColors = {
    Infrastructure: 'bg-blue-500/10 text-blue-600',
    Healthcare: 'bg-pink-500/10 text-pink-600',
    Education: 'bg-purple-500/10 text-purple-600',
    Economy: 'bg-amber-500/10 text-amber-600',
    Environment: 'bg-green-500/10 text-green-600',
    General: 'bg-slate-500/10 text-slate-600'
  };
</script>

<a 
  href="/manifestos/{manifesto.id}" 
  class="block bg-white border border-gray-200 rounded-xl p-6 hover:border-emerald-500/50 transition-all hover:shadow-lg hover:shadow-emerald-500/10 card"
>
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <div class="flex items-center gap-2 mb-2 flex-wrap">
        <span class="px-2 py-1 text-xs rounded-full font-medium {categoryColors[manifesto.category] || categoryColors.General}">
          {manifesto.category}
        </span>
        <span class="px-2 py-1 text-xs rounded-full border font-medium {statusColors[manifesto.status]}">
          {manifesto.status.charAt(0).toUpperCase() + manifesto.status.slice(1)}
        </span>
        {#if isLocked}
          <span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-500 flex items-center gap-1">
            <Clock class="w-3 h-3" />
            Locked
          </span>
        {/if}
      </div>
      <h3 class="text-lg font-bold text-gray-900 mb-1">{manifesto.title}</h3>
      <p class="text-sm text-gray-500">by {manifesto.politician_name}</p>
    </div>
  </div>
  
  <p class="text-gray-600 text-sm mb-4 line-clamp-2">{manifesto.description}</p>
  
  <!-- Vote Progress -->
  <div class="mb-4">
    <div class="flex justify-between text-xs mb-1">
      <span class="text-emerald-600 flex items-center gap-1 font-medium">
        <ThumbsUp class="w-3 h-3" />
        Kept ({manifesto.vote_kept})
      </span>
      <span class="text-red-600 flex items-center gap-1 font-medium">
        Broken ({manifesto.vote_broken})
        <ThumbsDown class="w-3 h-3" />
      </span>
    </div>
    <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
      <div 
        class="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all"
        style="width: {keptPercent}%"
      ></div>
    </div>
  </div>
  
  <!-- Footer Stats -->
  <div class="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-gray-100">
    <div class="flex items-center gap-1">
      <Users class="w-3 h-3" />
      <span>{totalVotes} votes</span>
    </div>
    {#if isLocked}
      <div class="flex items-center gap-1 text-amber-600 font-medium">
        <Clock class="w-3 h-3" />
        <span>Opens in {daysRemaining} days</span>
      </div>
    {:else}
      <div class="flex items-center gap-1 text-emerald-600 font-medium">
        <Calendar class="w-3 h-3" />
        <span>Voting open</span>
      </div>
    {/if}
  </div>
</a>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
