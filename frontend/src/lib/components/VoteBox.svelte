<script>
  import { ThumbsUp, ThumbsDown, Lock, Clock, CheckCircle, AlertCircle } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  export let manifestoId;
  export let isLocked = false;
  export let gracePeriodEnd = new Date().toISOString();
  export let voteKept = 0;
  export let voteBroken = 0;
  
  let hasVoted = false;
  let userVote = null;
  let isVoting = false;
  let error = null;
  let credential = null;
  
  $: totalVotes = voteKept + voteBroken;
  $: keptPercent = totalVotes > 0 ? Math.round((voteKept / totalVotes) * 100) : 0;
  $: brokenPercent = totalVotes > 0 ? Math.round((voteBroken / totalVotes) * 100) : 0;
  $: daysRemaining = Math.max(0, Math.ceil((new Date(gracePeriodEnd).getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
  
  onMount(() => {
    // Check if user has a credential stored
    const stored = localStorage.getItem('zk_credential');
    if (stored) {
      credential = JSON.parse(stored);
    }
    
    // Check if user already voted on this manifesto
    const votes = JSON.parse(localStorage.getItem('user_votes') || '{}');
    if (votes[manifestoId]) {
      hasVoted = true;
      userVote = votes[manifestoId];
    }
  });
  
  async function submitVote(voteType) {
    if (isLocked || hasVoted || isVoting || !credential) return;
    
    isVoting = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/api/votes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          nullifier: credential.nullifier,
          vote_type: voteType
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to submit vote');
      }
      
      // Store vote locally
      const votes = JSON.parse(localStorage.getItem('user_votes') || '{}');
      votes[manifestoId] = voteType;
      localStorage.setItem('user_votes', JSON.stringify(votes));
      
      hasVoted = true;
      userVote = voteType;
      
      // Update local counts
      if (voteType === 'kept') {
        voteKept += 1;
      } else {
        voteBroken += 1;
      }
    } catch (err) {
      error = err.message;
    } finally {
      isVoting = false;
    }
  }
</script>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
  <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
    {#if isLocked}
      <Lock class="w-5 h-5 text-yellow-400" />
      <span>Voting Locked</span>
    {:else}
      <CheckCircle class="w-5 h-5 text-emerald-400" />
      <span>Cast Your Vote</span>
    {/if}
  </h3>
  
  {#if isLocked}
    <div class="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-4">
      <div class="flex items-center gap-2 text-yellow-400 mb-2">
        <Clock class="w-4 h-4" />
        <span class="font-medium">Grace Period Active</span>
      </div>
      <p class="text-sm text-slate-400">
        Voting opens in <span class="text-yellow-400 font-semibold">{daysRemaining} days</span>. 
        This grace period allows time for the promise to be evaluated fairly.
      </p>
    </div>
  {:else if !credential}
    <div class="bg-slate-700/50 border border-slate-600 rounded-lg p-4 mb-4">
      <div class="flex items-center gap-2 text-slate-300 mb-2">
        <AlertCircle class="w-4 h-4" />
        <span class="font-medium">ZK Credential Required</span>
      </div>
      <p class="text-sm text-slate-400 mb-3">
        You need a zero-knowledge credential to vote anonymously.
      </p>
      <a href="/auth" class="inline-block bg-emerald-600 hover:bg-emerald-700 text-white text-sm px-4 py-2 rounded-lg transition-colors">
        Generate Credential
      </a>
    </div>
  {:else if hasVoted}
    <div class="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 mb-4">
      <div class="flex items-center gap-2 text-emerald-400 mb-2">
        <CheckCircle class="w-4 h-4" />
        <span class="font-medium">Vote Recorded</span>
      </div>
      <p class="text-sm text-slate-400">
        You voted: <span class="font-semibold {userVote === 'kept' ? 'text-emerald-400' : 'text-red-400'}">
          {userVote === 'kept' ? 'Promise Kept' : 'Promise Broken'}
        </span>
      </p>
    </div>
  {/if}
  
  {#if error}
    <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
      <p class="text-sm text-red-400">{error}</p>
    </div>
  {/if}
  
  <!-- Vote Buttons -->
  <div class="grid grid-cols-2 gap-4 mb-6">
    <button
      on:click={() => submitVote('kept')}
      disabled={isLocked || hasVoted || isVoting || !credential}
      class="flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
        {hasVoted && userVote === 'kept' 
          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' 
          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-emerald-500/50 hover:bg-emerald-500/10'}
        disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <ThumbsUp class="w-8 h-8 mb-2" />
      <span class="font-semibold">Kept</span>
      <span class="text-2xl font-bold">{voteKept}</span>
    </button>
    
    <button
      on:click={() => submitVote('broken')}
      disabled={isLocked || hasVoted || isVoting || !credential}
      class="flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
        {hasVoted && userVote === 'broken' 
          ? 'bg-red-500/20 border-red-500 text-red-400' 
          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-red-500/50 hover:bg-red-500/10'}
        disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <ThumbsDown class="w-8 h-8 mb-2" />
      <span class="font-semibold">Broken</span>
      <span class="text-2xl font-bold">{voteBroken}</span>
    </button>
  </div>
  
  <!-- Progress Bar -->
  <div class="mb-2">
    <div class="flex justify-between text-xs mb-1">
      <span class="text-emerald-400">{keptPercent}% Kept</span>
      <span class="text-red-400">{brokenPercent}% Broken</span>
    </div>
    <div class="h-3 bg-slate-700 rounded-full overflow-hidden flex">
      <div 
        class="h-full bg-emerald-500 transition-all"
        style="width: {keptPercent}%"
      ></div>
      <div 
        class="h-full bg-red-500 transition-all"
        style="width: {brokenPercent}%"
      ></div>
    </div>
  </div>
  
  <p class="text-xs text-slate-500 text-center">
    {totalVotes} total votes • Results stored on blockchain
  </p>
</div>
