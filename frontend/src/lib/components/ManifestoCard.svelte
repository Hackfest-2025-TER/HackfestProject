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
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    kept: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    broken: 'bg-red-500/20 text-red-400 border-red-500/30'
  };
  
  const categoryColors = {
    Infrastructure: 'bg-blue-500/20 text-blue-400',
    Healthcare: 'bg-pink-500/20 text-pink-400',
    Education: 'bg-purple-500/20 text-purple-400',
    Economy: 'bg-amber-500/20 text-amber-400',
    Environment: 'bg-green-500/20 text-green-400',
    General: 'bg-slate-500/20 text-slate-400'
  };
</script>

<a 
  href="/manifestos/{manifesto.id}" 
  class="block bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-emerald-500/50 transition-all hover:shadow-lg hover:shadow-emerald-500/10"
>
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <div class="flex items-center gap-2 mb-2">
        <span class="px-2 py-1 text-xs rounded-full {categoryColors[manifesto.category] || categoryColors.General}">
          {manifesto.category}
        </span>
        <span class="px-2 py-1 text-xs rounded-full border {statusColors[manifesto.status]}">
          {manifesto.status.charAt(0).toUpperCase() + manifesto.status.slice(1)}
        </span>
        {#if isLocked}
          <span class="px-2 py-1 text-xs rounded-full bg-slate-600/50 text-slate-300 flex items-center gap-1">
            <Clock class="w-3 h-3" />
            Locked
          </span>
        {/if}
      </div>
      <h3 class="text-lg font-semibold text-white mb-1">{manifesto.title}</h3>
      <p class="text-sm text-slate-400">by {manifesto.politician_name}</p>
    </div>
  </div>
  
  <p class="text-slate-300 text-sm mb-4 line-clamp-2">{manifesto.description}</p>
  
  <!-- Vote Progress -->
  <div class="mb-4">
    <div class="flex justify-between text-xs mb-1">
      <span class="text-emerald-400 flex items-center gap-1">
        <ThumbsUp class="w-3 h-3" />
        Kept ({manifesto.vote_kept})
      </span>
      <span class="text-red-400 flex items-center gap-1">
        Broken ({manifesto.vote_broken})
        <ThumbsDown class="w-3 h-3" />
      </span>
    </div>
    <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
      <div 
        class="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all"
        style="width: {keptPercent}%"
      ></div>
    </div>
  </div>
  
  <!-- Footer Stats -->
  <div class="flex items-center justify-between text-xs text-slate-500">
    <div class="flex items-center gap-1">
      <Users class="w-3 h-3" />
      <span>{totalVotes} votes</span>
    </div>
    {#if isLocked}
      <div class="flex items-center gap-1 text-yellow-400">
        <Clock class="w-3 h-3" />
        <span>Opens in {daysRemaining} days</span>
      </div>
    {:else}
      <div class="flex items-center gap-1">
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
