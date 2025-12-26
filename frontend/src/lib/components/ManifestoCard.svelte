<script>
  import {
    Clock,
    ThumbsUp,
    ThumbsDown,
    Users,
    Calendar,
    ArrowRight,
  } from "lucide-svelte";

  export let manifesto = {
    id: 1,
    title: "Promise Title",
    description: "Promise description",
    representative_name: "Representative Name",
    category: "General",
    status: "pending",
    vote_kept: 0,
    vote_broken: 0,
    grace_period_end: new Date().toISOString(),
    created_at: new Date().toISOString(),
  };

  $: totalVotes = manifesto.vote_kept + manifesto.vote_broken;
  $: keptPercent =
    totalVotes > 0 ? Math.round((manifesto.vote_kept / totalVotes) * 100) : 0;
  $: isLocked = new Date(manifesto.grace_period_end) > new Date();

  $: daysRemaining = Math.max(
    0,
    Math.ceil(
      (new Date(manifesto.grace_period_end).getTime() - Date.now()) /
        (1000 * 60 * 60 * 24),
    ),
  );

  const categoryStyles = {
    Infrastructure: "bg-blue-100 text-blue-700",
    Healthcare: "bg-rose-100 text-rose-700",
    Education: "bg-indigo-100 text-indigo-700",
    Economy: "bg-emerald-100 text-emerald-700",
    Environment: "bg-teal-100 text-teal-700",
    General: "bg-gray-100 text-gray-700",
  };
</script>

<a
  href="/manifestos/{manifesto.id}"
  class="group flex flex-col h-full bg-white rounded-xl shadow-card hover:shadow-card-hover hover:scale-[1.01] transition-all duration-200 border border-transparent hover:border-primary-100"
>
  <div class="p-6 md:p-8 flex-1">
    <!-- Header with Status -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex flex-wrap gap-2">
        <span
          class="px-3 py-1 text-xs font-semibold rounded-full {categoryStyles[
            manifesto.category
          ] || categoryStyles.General}"
        >
          {manifesto.category}
        </span>

        {#if isLocked}
          <span
            class="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600 flex items-center gap-1.5"
          >
            <Clock class="w-3.5 h-3.5" />
            Voting opens in {daysRemaining}d
          </span>
        {:else}
          <span
            class="px-3 py-1 text-xs font-medium rounded-full bg-success-50 text-success-700 flex items-center gap-1.5 px-3"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-success-500 animate-pulse"
            ></span>
            Open for voting
          </span>
        {/if}
      </div>
    </div>

    <!-- Title & Representative -->
    <div class="mb-4">
      <h3
        class="text-xl font-bold font-serif text-gray-900 group-hover:text-primary-700 transition-colors mb-2 leading-tight"
      >
        {manifesto.title}
      </h3>
      <p class="text-sm font-medium text-gray-500">
        Promised by <span class="text-gray-900"
          >{manifesto.representative_name}</span
        >
      </p>
    </div>

    <!-- Description -->
    <p class="text-gray-600 text-base leading-relaxed line-clamp-3 mb-6">
      {manifesto.description}
    </p>

    <!-- Vote Visualization -->
    <div class="space-y-2">
      <div
        class="flex justify-between text-xs font-medium uppercase tracking-wider text-gray-500"
      >
        <span>Citizen Consensus</span>
        <span>{totalVotes} Votes</span>
      </div>

      {#if totalVotes > 0}
        <div class="h-3 bg-gray-100 rounded-full overflow-hidden flex">
          <div
            class="h-full bg-success-500"
            style="width: {keptPercent}%"
          ></div>
          <div
            class="h-full bg-error-500"
            style="width: {100 - keptPercent}%"
          ></div>
        </div>

        <div class="flex justify-between text-sm font-medium pt-1">
          <div class="text-success-700 flex items-center gap-1.5">
            <ThumbsUp class="w-4 h-4" />
            {keptPercent}% Kept
          </div>
          <div class="text-error-700 flex items-center gap-1.5">
            {100 - keptPercent}% Broken
            <ThumbsDown class="w-4 h-4" />
          </div>
        </div>
      {:else}
        <div
          class="bg-gray-50 rounded-lg p-3 text-sm text-gray-500 text-center italic"
        >
          No votes cast yet. Be the first!
        </div>
      {/if}
    </div>
  </div>

  <!-- Footer Action -->
  <div
    class="px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-xl flex justify-between items-center group-hover:bg-primary-50/30 transition-colors"
  >
    <span
      class="text-sm font-medium text-primary-700 group-hover:text-primary-800"
    >
      {#if isLocked}
        View details
      {:else}
        Cast your vote
      {/if}
    </span>
    <ArrowRight
      class="w-4 h-4 text-primary-400 group-hover:translate-x-1 transition-transform"
    />
  </div>
</a>

<style>
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
