<script>
  import {
    ThumbsUp,
    ThumbsDown,
    Lock,
    Clock,
    CheckCircle,
    AlertCircle,
    Shield,
    TrendingUp,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { authStore } from "$lib/stores";

  export let manifestoId;
  export let isLocked = false;
  export let gracePeriodEnd = new Date().toISOString();
  export let voteKept = 0;
  export let voteBroken = 0;

  let hasVoted = false;
  let userVote = null;
  let isVoting = false;
  let error = null;

  $: totalVotes = voteKept + voteBroken;
  $: keptPercent =
    totalVotes > 0 ? Math.round((voteKept / totalVotes) * 100) : 0;
  $: brokenPercent =
    totalVotes > 0 ? Math.round((voteBroken / totalVotes) * 100) : 0;
  $: daysRemaining = Math.max(
    0,
    Math.ceil(
      (new Date(gracePeriodEnd).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    ),
  );

  // Reactive credential from auth store
  $: credential = $authStore.credential;

  // Check if user has voted on this manifesto whenever credential changes
  $: if (credential) {
    checkVoteStatus();
  }

  function checkVoteStatus() {
    // Check from auth store's usedVotes
    if (
      credential?.usedVotes?.includes(manifestoId) ||
      credential?.usedVotes?.includes(String(manifestoId))
    ) {
      hasVoted = true;
      const votes = JSON.parse(localStorage.getItem("user_votes") || "{}");
      userVote = votes[manifestoId] || "kept";
    } else {
      // Fallback: Check local votes storage
      const votes = JSON.parse(localStorage.getItem("user_votes") || "{}");
      if (votes[manifestoId]) {
        hasVoted = true;
        userVote = votes[manifestoId];
      }
    }
  }

  onMount(() => {
    checkVoteStatus();
  });

  async function submitVote(voteType) {
    if (isLocked || hasVoted || isVoting || !credential) return;

    isVoting = true;
    error = null;

    try {
      const response = await fetch("http://localhost:8000/api/votes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          nullifier: credential.nullifier,
          vote_type: voteType,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to submit vote");
      }

      // Store vote locally
      const votes = JSON.parse(localStorage.getItem("user_votes") || "{}");
      votes[manifestoId] = voteType;
      localStorage.setItem("user_votes", JSON.stringify(votes));

      // Update auth store with voted manifesto
      authStore.markVoted(manifestoId);

      hasVoted = true;
      userVote = voteType;

      // Update local counts
      if (voteType === "kept") {
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

<div class="card p-5">
  <div class="mb-4 pb-4 border-b border-gray-100">
    <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
      <TrendingUp class="w-5 h-5 text-primary-600" />
      Community Verdict
    </h3>
  </div>

  {#if isLocked}
    <div class="bg-gray-50 rounded-lg p-4 mb-4 text-center">
      <Lock class="w-6 h-6 text-gray-400 mx-auto mb-2" />
      <p class="font-medium text-gray-900">Voting is Locked</p>
      <p class="text-xs text-gray-500 mt-1">
        Opens in {daysRemaining} days
      </p>
    </div>
  {:else if !credential}
    <div class="bg-primary-50 rounded-lg p-4 mb-4 text-center">
      <Shield class="w-6 h-6 text-primary-600 mx-auto mb-2" />
      <p class="font-medium text-primary-900 text-sm">Verify to Vote</p>
      <a href="/auth" class="btn btn-primary btn-sm w-full mt-3"
        >Verify Identity</a
      >
    </div>
  {/if}

  <!-- Results Bar -->
  <div class="mb-6">
    <div class="flex justify-between text-sm mb-2">
      <span class="font-medium text-success-700">{keptPercent}% Kept</span>
      <span class="font-medium text-error-700">{brokenPercent}% Broken</span>
    </div>
    <div class="h-3 bg-gray-100 rounded-full overflow-hidden flex">
      <div
        class="h-full bg-success-500 transition-all duration-500"
        style="width: {keptPercent}%"
      ></div>
      <div
        class="h-full bg-error-500 transition-all duration-500"
        style="width: {brokenPercent}%"
      ></div>
    </div>
    <p class="text-xs text-gray-400 mt-2 text-center">
      {totalVotes} citizens voted
    </p>
  </div>

  {#if !isLocked && credential}
    {#if hasVoted}
      <div class="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
        <CheckCircle class="w-8 h-8 text-success-500 mx-auto mb-2" />
        <p class="font-medium text-gray-900">
          You voted: <span class="capitalize text-success-600"
            >{userVote === "kept" ? "Kept" : "Broken"}</span
          >
        </p>
        <p class="text-xs text-gray-500 mt-1">Thank you for participating.</p>
      </div>
    {:else}
      <div class="grid grid-cols-2 gap-3">
        <button
          on:click={() => submitVote("kept")}
          disabled={isVoting}
          class="flex flex-col items-center justify-center p-3 rounded-xl border border-gray-200 hover:border-success-500 hover:bg-success-50 transition-all group"
        >
          <ThumbsUp
            class="w-6 h-6 text-gray-400 group-hover:text-success-600 mb-1"
          />
          <span
            class="text-sm font-semibold text-gray-700 group-hover:text-success-700"
            >Kept</span
          >
        </button>

        <button
          on:click={() => submitVote("broken")}
          disabled={isVoting}
          class="flex flex-col items-center justify-center p-3 rounded-xl border border-gray-200 hover:border-error-500 hover:bg-error-50 transition-all group"
        >
          <ThumbsDown
            class="w-6 h-6 text-gray-400 group-hover:text-error-600 mb-1"
          />
          <span
            class="text-sm font-semibold text-gray-700 group-hover:text-error-700"
            >Broken</span
          >
        </button>
      </div>
    {/if}
  {/if}

  {#if error}
    <div
      class="mt-4 text-xs text-error-600 flex items-center gap-1 justify-center"
    >
      <AlertCircle class="w-3 h-3" />
      {error}
    </div>
  {/if}
</div>
