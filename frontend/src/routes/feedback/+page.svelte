<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Bug, Lightbulb, MessageSquare, Upload, Shield, Info, ArrowLeft } from 'lucide-svelte';
  
  let feedbackType: 'bug' | 'suggestion' | 'general' = 'bug';
  let feedbackContent = '';
  let isSubmitting = false;
  
  const feedbackTypes = [
    { value: 'bug', label: 'Bug Report', icon: Bug },
    { value: 'suggestion', label: 'Suggestion', icon: Lightbulb },
    { value: 'general', label: 'General', icon: MessageSquare }
  ];
  
  async function submitFeedback() {
    if (!feedbackContent.trim()) return;
    isSubmitting = true;
    await new Promise(resolve => setTimeout(resolve, 1500));
    isSubmitting = false;
    // Reset form
    feedbackContent = '';
  }
</script>

<svelte:head>
  <title>Submit Feedback - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

<main class="feedback-page">
  <div class="container">
    <div class="feedback-card card">
      <div class="card-header">
        <h1>Report an Issue or Share Ideas</h1>
        <p>Help us build a more transparent election platform. Your feedback helps ensure integrity and usability.</p>
      </div>
      
      <!-- Feedback Type -->
      <div class="form-section">
        <label class="form-label">What kind of feedback is this?</label>
        <div class="type-options">
          {#each feedbackTypes as type}
            <button 
              class="type-btn" 
              class:selected={feedbackType === type.value}
              on:click={() => feedbackType = type.value}
            >
              <svelte:component this={type.icon} size={20} />
              <span>{type.label}</span>
            </button>
          {/each}
        </div>
      </div>
      
      <!-- Content -->
      <div class="form-section">
        <label class="form-label">Tell us more</label>
        <textarea 
          class="form-textarea"
          placeholder="Describe what happened or share your idea..."
          rows="6"
          bind:value={feedbackContent}
        ></textarea>
        <div class="char-count">{feedbackContent.length}/500 characters</div>
      </div>
      
      <!-- Screenshot Upload -->
      <div class="form-section">
        <label class="form-label">Add screenshot (optional)</label>
        <div class="upload-zone">
          <Upload size={24} />
          <p><span class="upload-link">Click to upload</span> or drag and drop</p>
          <span class="upload-hint">SVG, PNG, JPG or GIF (max. 800x400px)</span>
        </div>
      </div>
      
      <!-- Privacy Notice -->
      <div class="privacy-notice">
        <Shield size={18} />
        <div>
          <strong>Privacy & Transparency</strong>
          <p>
            Your privacy matters. This feedback is submitted anonymously and is not 
            stored on the public immutable ledger, but helps us improve the platform for everyone.
          </p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="form-actions">
        <a href="/" class="cancel-link">Cancel and go back</a>
        <button 
          class="submit-btn" 
          on:click={submitFeedback}
          disabled={!feedbackContent.trim() || isSubmitting}
        >
          {#if isSubmitting}
            <span class="spinner"></span>
            Submitting...
          {:else}
            Submit Feedback
          {/if}
        </button>
      </div>
    </div>
    
    <!-- Footer Links -->
    <div class="footer-links">
      <a href="/terms">Terms of Service</a>
      <a href="/privacy">Privacy Policy</a>
      <a href="/help">Help Center</a>
    </div>
  </div>
</main>

<Footer />

<style>
  .feedback-page {
    min-height: 100vh;
    background: var(--gray-50);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-8) var(--space-4);
  }
  
  .container {
    width: 100%;
    max-width: 560px;
  }
  
  .feedback-card {
    padding: var(--space-8);
  }
  
  .card-header {
    text-align: center;
    margin-bottom: var(--space-8);
  }
  
  .card-header h1 {
    font-size: 1.5rem;
    margin-bottom: var(--space-2);
  }
  
  .card-header p {
    color: var(--gray-500);
    font-size: 0.9rem;
  }
  
  .form-section {
    margin-bottom: var(--space-6);
  }
  
  .form-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-700);
    margin-bottom: var(--space-3);
  }
  
  .type-options {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-3);
  }
  
  .type-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-4);
    border: 2px solid var(--gray-200);
    background: white;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all 0.2s;
    color: var(--gray-500);
  }
  
  .type-btn:hover {
    border-color: var(--primary-300);
    color: var(--primary-600);
  }
  
  .type-btn.selected {
    border-color: var(--primary-500);
    background: var(--primary-50);
    color: var(--primary-600);
  }
  
  .type-btn span {
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .form-textarea {
    width: 100%;
    padding: var(--space-4);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    font-family: inherit;
    resize: vertical;
    line-height: 1.6;
  }
  
  .form-textarea:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .form-textarea::placeholder {
    color: var(--gray-400);
  }
  
  .char-count {
    text-align: right;
    font-size: 0.75rem;
    color: var(--gray-400);
    margin-top: var(--space-2);
  }
  
  .upload-zone {
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    text-align: center;
    background: var(--gray-50);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .upload-zone:hover {
    border-color: var(--primary-400);
    background: var(--primary-50);
  }
  
  .upload-zone :global(svg) {
    color: var(--gray-400);
    margin-bottom: var(--space-2);
  }
  
  .upload-zone p {
    color: var(--gray-600);
    font-size: 0.875rem;
    margin-bottom: var(--space-1);
  }
  
  .upload-link {
    color: var(--primary-600);
    font-weight: 500;
  }
  
  .upload-hint {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .privacy-notice {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--primary-50);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .privacy-notice :global(svg) {
    color: var(--primary-600);
    flex-shrink: 0;
    margin-top: 2px;
  }
  
  .privacy-notice strong {
    display: block;
    color: var(--gray-900);
    font-size: 0.875rem;
    margin-bottom: var(--space-1);
  }
  
  .privacy-notice p {
    font-size: 0.8rem;
    color: var(--gray-600);
    line-height: 1.5;
    margin: 0;
  }
  
  .form-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .cancel-link {
    font-size: 0.875rem;
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .cancel-link:hover {
    color: var(--gray-700);
  }
  
  .submit-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--primary-700);
  }
  
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .footer-links {
    display: flex;
    justify-content: center;
    gap: var(--space-4);
    margin-top: var(--space-6);
  }
  
  .footer-links a {
    font-size: 0.8rem;
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .footer-links a:hover {
    color: var(--primary-600);
  }
</style>
