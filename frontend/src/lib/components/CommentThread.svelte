<script lang="ts">
  import {
    MessageCircle,
    ThumbsUp,
    ThumbsDown,
    Send,
    User,
    Flag,
    AlertTriangle,
    CheckCircle,
    Eye,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { credential } from "$lib/stores";

  export let manifestoId;

  let comments = [];
  let flaggedComments = [];
  let newComment = "";
  let isLoading = true;
  let isSubmitting = false;
  let error = null;
  // credential is now imported from stores
  let sessionId = null;
  let showFlagged = false;

  onMount(async () => {
    // Credential is now handled by authStore (reactive)

    // Get or create session ID (for commenting)
    sessionId = localStorage.getItem("comment_session_id");
    if (!sessionId) {
      sessionId = crypto.randomUUID().replace(/-/g, "");
      localStorage.setItem("comment_session_id", sessionId);
    }

    await loadComments();
    await loadFlaggedComments();
  });

  async function loadComments() {
    try {
      const response = await fetch(
        `http://localhost:8000/api/manifestos/${manifestoId}/comments`,
      );
      if (response.ok) {
        const data = await response.json();
        comments = data.comments || [];
      }
    } catch (err) {
      console.error("Failed to load comments:", err);
    } finally {
      isLoading = false;
    }
  }

  async function loadFlaggedComments() {
    try {
      const response = await fetch(
        `http://localhost:8000/api/manifestos/${manifestoId}/comments/flagged`,
      );
      if (response.ok) {
        const data = await response.json();
        flaggedComments = data.flagged_comments || [];
      }
    } catch (err) {
      console.error("Failed to load flagged comments:", err);
    }
  }

  async function submitComment() {
    if (!newComment.trim() || isSubmitting) return;

    isSubmitting = true;
    error = null;

    try {
      const response = await fetch("http://localhost:8000/api/comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          session_id: sessionId,
          content: newComment.trim(),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to post comment");
      }

      const result = await response.json();

      // Show feedback based on moderation state
      if (result.state === "active") {
        comments = [result, ...comments];
      } else if (result.state === "auto_flagged") {
        flaggedComments = [result, ...flaggedComments];
        error = `Your comment was flagged for review (${result.auto_flag_reason}). It will appear in the Flagged section.`;
      } else if (result.state === "quarantined") {
        error =
          "Your comment was detected as potential spam and has been quarantined.";
      }

      newComment = "";
    } catch (err) {
      error = err.message;
    } finally {
      isSubmitting = false;
    }
  }

  async function voteComment(
    commentId: number,
    voteType: "up" | "down" | "flag",
  ) {
    if (!$credential) {
      error = "You need to authenticate to vote on comments";
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/comments/${commentId}/vote`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nullifier: $credential.nullifier,
            vote_type: voteType,
          }),
        },
      );

      if (response.ok) {
        const result = await response.json();
        // Update comment in list
        comments = comments.map((c) =>
          c.id === commentId
            ? {
                ...c,
                upvotes: result.upvotes,
                downvotes: result.downvotes,
                flag_count: result.flag_count,
                state: result.state,
              }
            : c,
        );
        flaggedComments = flaggedComments.map((c) =>
          c.id === commentId
            ? {
                ...c,
                upvotes: result.upvotes,
                downvotes: result.downvotes,
                flag_count: result.flag_count,
                state: result.state,
              }
            : c,
        );

        // If comment was promoted back to active, move it
        if (result.state === "active") {
          const promoted = flaggedComments.find((c) => c.id === commentId);
          if (promoted) {
            flaggedComments = flaggedComments.filter((c) => c.id !== commentId);
            comments = [{ ...promoted, state: "active" }, ...comments];
          }
        }

        // Reload to get updated lists
        await loadComments();
        await loadFlaggedComments();
      }
    } catch (err) {
      console.error("Vote failed:", err);
    }
  }

  function formatDate(dateStr: string): string {
    if (!dateStr) return "";
    if (!dateStr) return "";
    const date: Date = new Date(dateStr);
    const now: Date = new Date();
    const diffMs: number = now.getTime() - date.getTime();
    const diffMins: number = Math.floor(diffMs / 60000);
    const diffHours: number = Math.floor(diffMs / 3600000);
    const diffDays: number = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }

  function getFlagReasonLabel(reason: string): string {
    switch (reason) {
      case "off_topic":
        return "Off-topic";
      case "spam_like":
        return "Potential spam";
      case "low_relevance":
        return "Low relevance";
      default:
        return "Flagged";
    }
  }
</script>

<div class="card p-6">
  <div
    class="flex items-center justify-between mb-6 pb-4 border-b border-gray-100"
  >
    <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
      <MessageCircle class="w-5 h-5 text-primary-600" />
      <span>Discussion ({comments.length})</span>
    </h3>

    {#if flaggedComments.length > 0}
      <button
        on:click={() => (showFlagged = !showFlagged)}
        class="flex items-center gap-2 text-sm text-warning-600 hover:text-warning-700 transition-colors font-medium border border-warning-200 bg-warning-50 px-3 py-1.5 rounded-full"
      >
        <Eye class="w-4 h-4" />
        {showFlagged ? "Hide" : "Show"} Flagged ({flaggedComments.length})
      </button>
    {/if}
  </div>

  <!-- Comment Form - No authentication required -->
  <div class="mb-8">
    <div class="flex gap-4">
      <div
        class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0"
      >
        <User class="w-5 h-5 text-primary-600" />
      </div>
      <div class="flex-1">
        <textarea
          bind:value={newComment}
          placeholder="Share your thoughts on this promise..."
          rows="3"
          class="w-full bg-white border border-gray-300 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none transition-all"
        ></textarea>
        <div class="flex justify-between items-center mt-3">
          <span class="text-xs text-gray-500 font-medium">
            Posting as: Citizen-{sessionId?.slice(0, 6) || "..."}
          </span>
          <button
            on:click={submitComment}
            disabled={!newComment.trim() || isSubmitting}
            class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg transition-all text-sm font-semibold shadow-sm"
          >
            <Send class="w-4 h-4" />
            {isSubmitting ? "Posting..." : "Post Comment"}
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-2">
          💡 Comments are moderated for relevance. {$credential
            ? "You can vote on comments."
            : "Authenticate to vote on comments."}
        </p>
      </div>
    </div>
    {#if error}
      <div class="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg">
        <p class="text-sm text-red-600 flex items-center gap-2">
          <AlertTriangle class="w-4 h-4" />
          {error}
        </p>
      </div>
    {/if}
  </div>

  <!-- Flagged Comments Section -->
  {#if showFlagged && flaggedComments.length > 0}
    <div class="mb-6 p-4 bg-warning-50 border border-warning-200 rounded-xl">
      <h4
        class="text-sm font-bold text-warning-700 mb-3 flex items-center gap-2"
      >
        <AlertTriangle class="w-4 h-4" />
        Flagged for Review ({flaggedComments.length})
      </h4>
      <p class="text-xs text-warning-600 mb-4">
        These comments need community review. Vote to keep relevant comments or
        remove off-topic ones.
      </p>
      <div class="space-y-3">
        {#each flaggedComments as comment}
          <div class="flex gap-3 opacity-90">
            <div
              class="w-8 h-8 rounded-full bg-warning-100 flex items-center justify-center flex-shrink-0"
            >
              <User class="w-4 h-4 text-warning-600" />
            </div>
            <div
              class="flex-1 bg-white border border-warning-100 rounded-lg p-3 shadow-sm"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-gray-700">
                    {comment.author ||
                      `Citizen-${comment.session_id?.slice(0, 6) || "?"}`}
                  </span>
                  <span
                    class="text-[10px] uppercase tracking-wider px-2 py-0.5 bg-warning-100 text-warning-700 rounded-full font-bold"
                  >
                    {getFlagReasonLabel(comment.auto_flag_reason)}
                  </span>
                </div>
                <span class="text-xs text-gray-500"
                  >{formatDate(comment.created_at)}</span
                >
              </div>
              <p class="text-gray-600 text-sm mb-2">{comment.content}</p>
              {#if comment.similarity_score !== null}
                <p class="text-xs text-gray-400 mb-2">
                  Relevance: {comment.similarity_score}%
                </p>
              {/if}
              <div
                class="flex items-center gap-3 mt-2 border-t border-gray-100 pt-2"
              >
                <button
                  on:click={() => voteComment(comment.id, "up")}
                  class="flex items-center gap-1.5 text-gray-500 hover:text-success-600 text-xs transition-colors font-medium"
                  title="Keep - Relevant"
                >
                  <ThumbsUp class="w-3.5 h-3.5" />
                  <span>Keep ({comment.upvotes || 0})</span>
                </button>
                <button
                  on:click={() => voteComment(comment.id, "down")}
                  class="flex items-center gap-1.5 text-gray-500 hover:text-error-600 text-xs transition-colors font-medium"
                  title="Remove - Off-topic"
                >
                  <ThumbsDown class="w-3.5 h-3.5" />
                  <span>Remove ({comment.downvotes || 0})</span>
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Active Comments List -->
  {#if isLoading}
    <div class="text-center py-12">
      <div
        class="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-3"
      ></div>
      <p class="text-gray-500 text-sm">Loading comments...</p>
    </div>
  {:else if comments.length === 0}
    <div
      class="text-center py-12 bg-gray-50 rounded-xl border border-gray-100 border-dashed"
    >
      <MessageCircle class="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-500 font-medium">No comments yet.</p>
      <p class="text-gray-400 text-sm">Be the first to share your thoughts!</p>
    </div>
  {:else}
    <div class="space-y-6">
      {#each comments as comment}
        <div class="flex gap-4 group">
          <div
            class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 border border-gray-200"
          >
            <User class="w-5 h-5 text-gray-500" />
          </div>
          <div class="flex-1">
            <div
              class="bg-gray-50 rounded-xl p-4 border border-gray-100 group-hover:border-gray-200 transition-colors"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-gray-900">
                    {comment.author ||
                      `Citizen-${comment.session_id?.slice(0, 6) || "?"}`}
                  </span>
                  {#if comment.auto_flag_reason === "low_relevance"}
                    <span
                      class="text-[10px] bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full font-medium"
                    >
                      Low Relevance
                    </span>
                  {/if}
                </div>
                <span class="text-xs text-gray-500"
                  >{formatDate(comment.created_at)}</span
                >
              </div>
              <p class="text-gray-700 text-sm leading-relaxed">
                {comment.content}
              </p>
            </div>

            <div class="flex items-center gap-4 mt-2 pl-2">
              <button
                on:click={() => voteComment(comment.id, "up")}
                class="flex items-center gap-1.5 text-gray-500 hover:text-primary-600 text-xs transition-colors font-medium"
                disabled={!$credential}
                title={$credential ? "Upvote" : "Authenticate to vote"}
              >
                <ThumbsUp class="w-3.5 h-3.5" />
                <span>{comment.upvotes || 0}</span>
              </button>
              <button
                on:click={() => voteComment(comment.id, "down")}
                class="flex items-center gap-1.5 text-gray-500 hover:text-red-600 text-xs transition-colors font-medium"
                disabled={!$credential}
                title={$credential ? "Downvote" : "Authenticate to vote"}
              >
                <ThumbsDown class="w-3.5 h-3.5" />
                <span>{comment.downvotes || 0}</span>
              </button>
              <div class="h-3 w-px bg-gray-300"></div>
              <button
                on:click={() => voteComment(comment.id, "flag")}
                class="flex items-center gap-1.5 text-gray-400 hover:text-warning-600 text-xs transition-colors font-medium"
                disabled={!$credential}
                title={$credential
                  ? "Flag as inappropriate"
                  : "Authenticate to flag"}
              >
                <Flag class="w-3.5 h-3.5" />
                <span>Report</span>
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
