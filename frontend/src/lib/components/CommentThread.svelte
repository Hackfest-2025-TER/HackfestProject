<script lang="ts">
  import { MessageCircle, ThumbsUp, ThumbsDown, User, Shield, CornerDownRight } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  export let comment: any;
  
  let upvoted = false;
  let downvoted = false;
  let localUpvotes = comment.upvotes || 0;
  let localDownvotes = comment.downvotes || 0;
  
  function formatDate(dateStr: string): string {
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
  
  function formatNullifier(nullifier: string): string {
    if (!nullifier) return 'Anonymous';
    return nullifier.substring(0, 12) + '...';
  }
  
  function handleUpvote() {
    if (upvoted) {
      upvoted = false;
      localUpvotes--;
    } else {
      upvoted = true;
      localUpvotes++;
      if (downvoted) {
        downvoted = false;
        localDownvotes--;
      }
    }
  }
  
  function handleDownvote() {
    if (downvoted) {
      downvoted = false;
      localDownvotes--;
    } else {
      downvoted = true;
      localDownvotes++;
      if (upvoted) {
        upvoted = false;
        localUpvotes--;
      }
    }
  }
  
  onMount(() => {
    // Check if user has voted on this comment from localStorage
    const votes = JSON.parse(localStorage.getItem('comment_votes') || '{}');
    if (votes[comment.id]) {
      if (votes[comment.id] === 'up') upvoted = true;
      if (votes[comment.id] === 'down') downvoted = true;
    }
  });
</script>

<div class="comment-thread">
  <div class="comment-main">
    <div class="comment-avatar">
      <Shield size={18} />
    </div>
    <div class="comment-body">
      <div class="comment-header">
        <div class="comment-meta">
          <span class="comment-author">{formatNullifier(comment.nullifier)}</span>
          <span class="comment-badge">Verified</span>
        </div>
        <span class="comment-time">{formatDate(comment.created_at)}</span>
      </div>
      <p class="comment-text">{comment.content}</p>
      <div class="comment-actions">
        <button 
          class="action-btn upvote" 
          class:active={upvoted}
          on:click={handleUpvote}
        >
          <ThumbsUp size={14} />
          <span>{localUpvotes}</span>
        </button>
        <button 
          class="action-btn downvote" 
          class:active={downvoted}
          on:click={handleDownvote}
        >
          <ThumbsDown size={14} />
          <span>{localDownvotes}</span>
        </button>
        {#if comment.replies && comment.replies.length > 0}
          <div class="reply-count">
            <MessageCircle size={14} />
            <span>{comment.replies.length} {comment.replies.length === 1 ? 'reply' : 'replies'}</span>
          </div>
        {/if}
      </div>
    </div>
  </div>
  
  {#if comment.replies && comment.replies.length > 0}
    <div class="comment-replies">
      {#each comment.replies as reply}
        <div class="reply-indicator">
          <CornerDownRight size={14} />
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
