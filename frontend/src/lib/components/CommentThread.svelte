<script lang="ts">
  import { MessageCircle, ThumbsUp, Send, User } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  export let manifestoId;
  
  let comments = [];
  let newComment = '';
  let isLoading = true;
  let isSubmitting = false;
  let error = null;
  let credential = null;
  
  onMount(async () => {
    const stored = localStorage.getItem('zk_credential');
    if (stored) {
      credential = JSON.parse(stored);
    }
    await loadComments();
  });
  
  async function loadComments() {
    try {
      const response = await fetch(`http://localhost:8000/api/manifestos/${manifestoId}/comments`);
      if (response.ok) {
        comments = await response.json();
      }
    } catch (err) {
      console.error('Failed to load comments:', err);
    } finally {
      isLoading = false;
    }
  }
  
  async function submitComment() {
    if (!newComment.trim() || !credential || isSubmitting) return;
    
    isSubmitting = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          nullifier: credential.nullifier,
          content: newComment.trim()
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to post comment');
      }
      
      const comment = await response.json();
      comments = [comment, ...comments];
      newComment = '';
    } catch (err) {
      error = err.message;
    } finally {
      isSubmitting = false;
    }
  }
  
  function formatDate(dateStr: string): string {
    const date: Date = new Date(dateStr);
    const now: Date = new Date();
    const diffMs: number = now.getTime() - date.getTime();
    const diffMins: number = Math.floor(diffMs / 60000);
    const diffHours: number = Math.floor(diffMs / 3600000);
    const diffDays: number = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }
</script>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
  <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
    <MessageCircle class="w-5 h-5 text-emerald-400" />
    <span>Discussion ({comments.length})</span>
  </h3>
  
  <!-- Comment Form -->
  {#if credential}
    <div class="mb-6">
      <div class="flex gap-3">
        <div class="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
          <User class="w-5 h-5 text-emerald-400" />
        </div>
        <div class="flex-1">
          <textarea
            bind:value={newComment}
            placeholder="Share your thoughts anonymously..."
            rows="3"
            class="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 resize-none"
          ></textarea>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs text-slate-500">
              Posting as: {credential.nullifier.slice(0, 12)}...
            </span>
            <button
              on:click={submitComment}
              disabled={!newComment.trim() || isSubmitting}
              class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors text-sm"
            >
              <Send class="w-4 h-4" />
              {isSubmitting ? 'Posting...' : 'Post'}
            </button>
          </div>
        </div>
      </div>
      {#if error}
        <p class="text-sm text-red-400 mt-2">{error}</p>
      {/if}
    </div>
  {:else}
    <div class="bg-slate-700/50 border border-slate-600 rounded-lg p-4 mb-6">
      <p class="text-sm text-slate-400 mb-2">
        You need a ZK credential to participate in discussions.
      </p>
      <a href="/auth" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium">
        Generate Credential →
      </a>
    </div>
  {/if}
  
  <!-- Comments List -->
  {#if isLoading}
    <div class="text-center py-8">
      <div class="animate-spin w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full mx-auto mb-2"></div>
      <p class="text-slate-400 text-sm">Loading comments...</p>
    </div>
  {:else if comments.length === 0}
    <div class="text-center py-8">
      <MessageCircle class="w-12 h-12 text-slate-600 mx-auto mb-2" />
      <p class="text-slate-400">No comments yet. Be the first to share your thoughts!</p>
    </div>
  {:else}
    <div class="space-y-4">
      {#each comments as comment}
        <div class="flex gap-3">
          <div class="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0">
            <User class="w-5 h-5 text-slate-400" />
          </div>
          <div class="flex-1 bg-slate-700/30 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-slate-300">
                {comment.nullifier?.slice(0, 12) || 'Anonymous'}...
              </span>
              <span class="text-xs text-slate-500">{formatDate(comment.created_at)}</span>
            </div>
            <p class="text-slate-200 text-sm">{comment.content}</p>
            <div class="flex items-center gap-4 mt-3">
              <button class="flex items-center gap-1 text-slate-500 hover:text-emerald-400 text-xs transition-colors">
                <ThumbsUp class="w-3 h-3" />
                <span>{comment.upvotes || 0}</span>
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
