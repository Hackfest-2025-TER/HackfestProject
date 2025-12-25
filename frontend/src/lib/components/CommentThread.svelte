<script lang="ts">
  import { MessageCircle, ThumbsUp, ThumbsDown, Send, User, Flag, AlertTriangle, CheckCircle, Eye } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  export let manifestoId;
  
  let comments = [];
  let flaggedComments = [];
  let newComment = '';
  let isLoading = true;
  let isSubmitting = false;
  let error = null;
  let credential = null;
  let sessionId = null;
  let showFlagged = false;
  
  onMount(async () => {
    // Check for ZK credential (for voting)
    const stored = localStorage.getItem('zk_credential');
    if (stored) {
      credential = JSON.parse(stored);
    }
    
    // Get or create session ID (for commenting)
    sessionId = localStorage.getItem('comment_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID().replace(/-/g, '');
      localStorage.setItem('comment_session_id', sessionId);
    }
    
    await loadComments();
    await loadFlaggedComments();
  });
  
  async function loadComments() {
    try {
      const response = await fetch(`http://localhost:8000/api/manifestos/${manifestoId}/comments`);
      if (response.ok) {
        const data = await response.json();
        comments = data.comments || [];
      }
    } catch (err) {
      console.error('Failed to load comments:', err);
    } finally {
      isLoading = false;
    }
  }
  
  async function loadFlaggedComments() {
    try {
      const response = await fetch(`http://localhost:8000/api/manifestos/${manifestoId}/comments/flagged`);
      if (response.ok) {
        const data = await response.json();
        flaggedComments = data.flagged_comments || [];
      }
    } catch (err) {
      console.error('Failed to load flagged comments:', err);
    }
  }
  
  async function submitComment() {
    if (!newComment.trim() || isSubmitting) return;
    
    isSubmitting = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          session_id: sessionId,
          content: newComment.trim()
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to post comment');
      }
      
      const result = await response.json();
      
      // Show feedback based on moderation state
      if (result.state === 'active') {
        comments = [result, ...comments];
      } else if (result.state === 'auto_flagged') {
        flaggedComments = [result, ...flaggedComments];
        error = `Your comment was flagged for review (${result.auto_flag_reason}). It will appear in the Flagged section.`;
      } else if (result.state === 'quarantined') {
        error = 'Your comment was detected as potential spam and has been quarantined.';
      }
      
      newComment = '';
    } catch (err) {
      error = err.message;
    } finally {
      isSubmitting = false;
    }
  }
  
  async function voteComment(commentId: number, voteType: 'up' | 'down' | 'flag') {
    if (!credential) {
      error = 'You need to authenticate to vote on comments';
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/comments/${commentId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nullifier: credential.nullifier,
          vote_type: voteType
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        // Update comment in list
        comments = comments.map(c => 
          c.id === commentId 
            ? { ...c, upvotes: result.upvotes, downvotes: result.downvotes, flag_count: result.flag_count, state: result.state }
            : c
        );
        flaggedComments = flaggedComments.map(c =>
          c.id === commentId
            ? { ...c, upvotes: result.upvotes, downvotes: result.downvotes, flag_count: result.flag_count, state: result.state }
            : c
        );
        
        // If comment was promoted back to active, move it
        if (result.state === 'active') {
          const promoted = flaggedComments.find(c => c.id === commentId);
          if (promoted) {
            flaggedComments = flaggedComments.filter(c => c.id !== commentId);
            comments = [{ ...promoted, state: 'active' }, ...comments];
          }
        }
        
        // Reload to get updated lists
        await loadComments();
        await loadFlaggedComments();
      }
    } catch (err) {
      console.error('Vote failed:', err);
    }
  }
  
  function formatDate(dateStr: string): string {
    if (!dateStr) return '';
    if (!dateStr) return '';
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
  
  function getFlagReasonLabel(reason: string): string {
    switch (reason) {
      case 'off_topic': return 'Off-topic';
      case 'spam_like': return 'Potential spam';
      case 'low_relevance': return 'Low relevance';
      default: return 'Flagged';
    }
  }
</script>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold text-white flex items-center gap-2">
      <MessageCircle class="w-5 h-5 text-emerald-400" />
      <span>Discussion ({comments.length})</span>
    </h3>
    
    {#if flaggedComments.length > 0}
      <button
        on:click={() => showFlagged = !showFlagged}
        class="flex items-center gap-2 text-sm text-amber-400 hover:text-amber-300 transition-colors"
      >
        <Eye class="w-4 h-4" />
        {showFlagged ? 'Hide' : 'Show'} Flagged ({flaggedComments.length})
      </button>
    {/if}
  </div>
  
  <!-- Comment Form - No authentication required -->
  <div class="mb-6">
    <div class="flex gap-3">
      <div class="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
        <User class="w-5 h-5 text-emerald-400" />
      </div>
      <div class="flex-1">
        <textarea
          bind:value={newComment}
          placeholder="Share your thoughts on this promise..."
          rows="3"
          class="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 resize-none"
        ></textarea>
        <div class="flex justify-between items-center mt-2">
          <span class="text-xs text-slate-500">
            Posting as: Citizen-{sessionId?.slice(0, 6) || '...'}
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
        <p class="text-xs text-slate-500 mt-1">
          💡 Comments are moderated for relevance. {credential ? 'You can vote on comments.' : 'Authenticate to vote on comments.'}
        </p>
      </div>
    </div>
    {#if error}
      <div class="mt-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
        <p class="text-sm text-amber-400 flex items-center gap-2">
          <AlertTriangle class="w-4 h-4" />
          {error}
        </p>
      </div>
    {/if}
  </div>
  
  <!-- Flagged Comments Section -->
  {#if showFlagged && flaggedComments.length > 0}
    <div class="mb-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
      <h4 class="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
        <AlertTriangle class="w-4 h-4" />
        Flagged for Review ({flaggedComments.length})
      </h4>
      <p class="text-xs text-slate-400 mb-4">
        These comments need community review. Vote to keep relevant comments or remove off-topic ones.
      </p>
      <div class="space-y-3">
        {#each flaggedComments as comment}
          <div class="flex gap-3 opacity-80">
            <div class="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
              <User class="w-4 h-4 text-amber-400" />
            </div>
            <div class="flex-1 bg-slate-700/30 rounded-lg p-3">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-slate-300">
                    {comment.author || `Citizen-${comment.session_id?.slice(0, 6) || '?'}`}
                  </span>
                  <span class="text-xs px-2 py-0.5 bg-amber-500/20 text-amber-400 rounded">
                    {getFlagReasonLabel(comment.auto_flag_reason)}
                  </span>
                </div>
                <span class="text-xs text-slate-500">{formatDate(comment.created_at)}</span>
              </div>
              <p class="text-slate-300 text-sm">{comment.content}</p>
              {#if comment.similarity_score !== null}
                <p class="text-xs text-slate-500 mt-1">
                  Relevance: {comment.similarity_score}%
                </p>
              {/if}
              <div class="flex items-center gap-3 mt-2">
                <button 
                  on:click={() => voteComment(comment.id, 'up')}
                  class="flex items-center gap-1 text-emerald-500 hover:text-emerald-400 text-xs transition-colors"
                  title="Keep - Relevant"
                >
                  <ThumbsUp class="w-3 h-3" />
                  <span>{comment.upvotes || 0}</span>
                </button>
                <button 
                  on:click={() => voteComment(comment.id, 'down')}
                  class="flex items-center gap-1 text-red-500 hover:text-red-400 text-xs transition-colors"
                  title="Remove - Off-topic"
                >
                  <ThumbsDown class="w-3 h-3" />
                  <span>{comment.downvotes || 0}</span>
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
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-slate-300">
                  {comment.author || `Citizen-${comment.session_id?.slice(0, 6) || '?'}`}
                </span>
                {#if comment.auto_flag_reason === 'low_relevance'}
                  <span class="text-xs px-2 py-0.5 bg-slate-600 text-slate-400 rounded">
                    Low relevance
                  </span>
                {/if}
              </div>
              <span class="text-xs text-slate-500">{formatDate(comment.created_at)}</span>
            </div>
            <p class="text-slate-200 text-sm">{comment.content}</p>
            <div class="flex items-center gap-4 mt-3">
              <button 
                on:click={() => voteComment(comment.id, 'up')}
                class="flex items-center gap-1 text-slate-500 hover:text-emerald-400 text-xs transition-colors"
                disabled={!credential}
                title={credential ? 'Upvote' : 'Authenticate to vote'}
              >
                <ThumbsUp class="w-3 h-3" />
                <span>{comment.upvotes || 0}</span>
              </button>
              <button 
                on:click={() => voteComment(comment.id, 'down')}
                class="flex items-center gap-1 text-slate-500 hover:text-red-400 text-xs transition-colors"
                disabled={!credential}
                title={credential ? 'Downvote' : 'Authenticate to vote'}
              >
                <ThumbsDown class="w-3 h-3" />
                <span>{comment.downvotes || 0}</span>
              </button>
              <button 
                on:click={() => voteComment(comment.id, 'flag')}
                class="flex items-center gap-1 text-slate-500 hover:text-amber-400 text-xs transition-colors"
                disabled={!credential}
                title={credential ? 'Flag as inappropriate' : 'Authenticate to flag'}
              >
                <Flag class="w-3 h-3" />
                <span>{comment.flag_count || 0}</span>
              </button>
            </div>
          </div>
        </div>
        <svelte:self comment={reply} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .comment-thread {
    position: relative;
  }
  
  .comment-main {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: white;
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-3);
    transition: background 0.2s;
  }
  
  .comment-main:hover {
    background: var(--gray-50);
  }
  
  .comment-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--success-100), var(--success-200));
    color: var(--success-600);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 2px solid var(--success-300);
  }
  
  .comment-body {
    flex: 1;
    min-width: 0;
  }
  
  .comment-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2);
    gap: var(--space-2);
    flex-wrap: wrap;
  }
  
  .comment-meta {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .comment-author {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-900);
    font-family: var(--font-mono);
  }
  
  .comment-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px var(--space-2);
    background: var(--success-100);
    color: var(--success-700);
    border-radius: var(--radius-sm);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }
  
  .comment-time {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .comment-text {
    font-size: 0.9375rem;
    color: var(--gray-700);
    line-height: 1.6;
    margin-bottom: var(--space-3);
    word-wrap: break-word;
  }
  
  .comment-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .action-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-md);
    border: 1px solid var(--gray-200);
    background: white;
    color: var(--gray-600);
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .action-btn:hover {
    background: var(--gray-50);
    border-color: var(--gray-300);
  }
  
  .action-btn.upvote:hover {
    border-color: var(--success-500);
    color: var(--success-600);
    background: var(--success-50);
  }
  
  .action-btn.upvote.active {
    border-color: var(--success-600);
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .action-btn.downvote:hover {
    border-color: var(--error-500);
    color: var(--error-600);
    background: var(--error-50);
  }
  
  .action-btn.downvote.active {
    border-color: var(--error-600);
    background: var(--error-100);
    color: var(--error-700);
  }
  
  .reply-count {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    color: var(--gray-500);
    font-size: 0.8125rem;
    margin-left: var(--space-2);
  }
  
  .reply-count :global(svg) {
    color: var(--gray-400);
  }
  
  .comment-replies {
    position: relative;
    margin-left: var(--space-8);
    padding-left: var(--space-6);
    border-left: 2px solid var(--gray-200);
  }
  
  .reply-indicator {
    position: absolute;
    left: -2px;
    top: var(--space-4);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border: 2px solid var(--gray-200);
    border-radius: 50%;
    color: var(--gray-400);
  }
  
  @media (max-width: 640px) {
    .comment-replies {
      margin-left: var(--space-4);
      padding-left: var(--space-4);
    }
    
    .comment-header {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
