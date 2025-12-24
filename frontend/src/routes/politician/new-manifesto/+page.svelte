<script lang="ts">
  import { Shield, Upload, Plus, Trash2, FileText, Info, Trees, Lightbulb } from 'lucide-svelte';
  
  let manifestoTitle = '';
  let executiveSummary = '';
  let promises: { id: number; title: string; category: string; description: string }[] = [
    { id: 1, title: 'Reforestation Initiative', category: 'environment', description: 'Plant 1 million trees in urban areas by 2026 to combat heat islands.' },
    { id: 2, title: 'Digital Literacy Program', category: 'education', description: 'Provide free coding workshops for 50,000 students across the state.' }
  ];
  
  let newPromiseTitle = '';
  let newPromiseCategory = 'economy';
  let newPromiseDescription = '';
  
  const categories = [
    { value: 'economy', label: 'Economy' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'education', label: 'Education' },
    { value: 'environment', label: 'Environment' },
    { value: 'infrastructure', label: 'Infrastructure' },
    { value: 'technology', label: 'Technology & Governance' }
  ];
  
  function addPromise() {
    if (newPromiseTitle && newPromiseDescription) {
      promises = [...promises, {
        id: Date.now(),
        title: newPromiseTitle,
        category: newPromiseCategory,
        description: newPromiseDescription
      }];
      newPromiseTitle = '';
      newPromiseDescription = '';
    }
  }
  
  function removePromise(id: number) {
    promises = promises.filter(p => p.id !== id);
  }
  
</script>

<svelte:head>
  <title>Draft New Manifesto - Politician Portal</title>
</svelte:head>

<main class="draft-page">
  <div class="container">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <a href="/politician/dashboard">Dashboard</a>
      <span>/</span>
      <span class="current">New Manifesto</span>
    </div>
    
    <div class="page-header">
      <div class="header-content">
        <h1>Draft New Manifesto</h1>
        <p>Define your commitments for the 2024 Election Cycle. All promises are publicly tracked.</p>
      </div>
      <div class="secure-badge">
        <span class="status-dot online"></span>
        CONNECTED
      </div>
    </div>
    
    <!-- Main Form -->
    <form class="manifesto-form">
      <!-- Title -->
      <div class="form-section">
        <label class="form-label">Manifesto Title / Campaign Slogan</label>
        <input 
          type="text" 
          class="form-input large" 
          placeholder="e.g., A Vision for a Better Tomorrow"
          bind:value={manifestoTitle}
        />
      </div>
      
      <!-- Executive Summary -->
      <div class="form-section">
        <label class="form-label">Executive Summary / Vision</label>
        <textarea 
          class="form-textarea"
          placeholder="Outline your core vision statement here..."
          rows="6"
          bind:value={executiveSummary}
        ></textarea>
      </div>
      
      <!-- PDF Upload -->
      <div class="form-section">
        <label class="form-label">Full Manifesto Document (PDF)</label>
        <div class="upload-zone">
          <Upload size={24} />
          <p><span class="upload-link">Click to upload</span> or drag and drop</p>
          <span class="upload-hint">PDF (MAX. 10MB)</span>
        </div>
      </div>
      
      <!-- Campaign Promises -->
      <div class="form-section promises-section">
        <h2>Campaign Promises</h2>
        <p class="section-desc">Add specific, trackable commitments that citizens can monitor.</p>
        
        <!-- Add Promise Form -->
        <div class="add-promise-form card">
          <div class="form-row">
            <div class="form-group flex-2">
              <label class="form-label small">PROMISE TITLE</label>
              <input 
                type="text" 
                class="form-input"
                placeholder="e.g., Reduce Carbon Emissions"
                bind:value={newPromiseTitle}
              />
            </div>
            <div class="form-group flex-1">
              <label class="form-label small">CATEGORY</label>
              <select class="form-select" bind:value={newPromiseCategory}>
                {#each categories as cat}
                  <option value={cat.value}>{cat.label}</option>
                {/each}
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label small">DESCRIPTION & SUCCESS METRICS</label>
            <textarea 
              class="form-textarea small"
              placeholder="Describe the goal and how success will be measured..."
              rows="3"
              bind:value={newPromiseDescription}
            ></textarea>
          </div>
          
          <button type="button" class="add-promise-btn" on:click={addPromise}>
            <Plus size={16} />
            Add Promise to List
          </button>
        </div>
        
        <!-- Promise List -->
        <div class="promise-list">
          {#each promises as promise}
            <div class="promise-item">
              <div class="promise-icon" class:environment={promise.category === 'environment'} class:education={promise.category === 'education'}>
                {#if promise.category === 'environment'}
                  <Trees size={18} />
                {:else}
                  <Lightbulb size={18} />
                {/if}
              </div>
              <div class="promise-content">
                <div class="promise-header">
                  <h4>{promise.title}</h4>
                  <span class="category-badge {promise.category}">{promise.category.toUpperCase()}</span>
                </div>
                <p>{promise.description}</p>
              </div>
              <button type="button" class="remove-btn" on:click={() => removePromise(promise.id)}>
                <Trash2 size={18} />
              </button>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Warning Notice -->
      <div class="warning-notice">
        <Info size={20} />
        <div>
          <strong>Permanent Record</strong>
          <p>Once published, this manifesto becomes a permanent record. Future changes require transparent amendments.</p>
        </div>
      </div>
      
      <!-- Footer Actions -->
      <div class="form-footer">
        <div class="hash-preview">
          <span class="preview-label">STATUS</span>
          <span class="preview-value">Draft - Not Published</span>
        </div>

        <div class="action-buttons">
          <button type="button" class="btn btn-secondary btn-lg">Save Draft</button>
          <button type="submit" class="btn btn-success btn-lg">
            <Upload size={18} />
            Publish Manifesto
          </button>
        </div>
      </div>
    </form>
  </div>
</main>

<style>
  .draft-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-8);
  }
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4);
  }
  
  .breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    margin-bottom: var(--space-4);
  }
  
  .breadcrumb a {
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .breadcrumb span {
    color: var(--gray-400);
  }
  
  .breadcrumb .current {
    color: var(--gray-700);
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-8);
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .header-content h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .header-content p {
    color: var(--gray-500);
    max-width: 500px;
  }
  
  .secure-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--success-50);
    color: var(--success-700);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
  }
  
  /* Form */
  .manifesto-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }
  
  .form-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .form-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-700);
  }
  
  .form-label.small {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gray-500);
  }
  
  .form-input {
    padding: var(--space-3);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .form-input.large {
    padding: var(--space-4);
    font-size: 1rem;
  }
  
  .form-input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .form-textarea {
    padding: var(--space-4);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    resize: vertical;
    font-family: inherit;
  }
  
  .form-textarea.small {
    padding: var(--space-3);
    font-size: 0.85rem;
  }
  
  .form-textarea:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .form-select {
    padding: var(--space-3);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    background: white;
    cursor: pointer;
  }
  
  .upload-zone {
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
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
  
  /* Promises Section */
  .promises-section h2 {
    font-size: 1.25rem;
    margin-bottom: var(--space-1);
  }
  
  .section-desc {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin-bottom: var(--space-4);
  }
  
  .add-promise-form {
    padding: var(--space-5);
    margin-bottom: var(--space-4);
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .add-promise-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border: 2px solid var(--primary-500);
    background: transparent;
    color: var(--primary-600);
    border-radius: var(--radius-lg);
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .add-promise-btn:hover {
    background: var(--primary-50);
  }
  
  .promise-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .promise-item {
    display: flex;
    align-items: flex-start;
    gap: var(--space-4);
    padding: var(--space-4);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
  }
  
  .promise-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--gray-100);
    color: var(--gray-500);
    flex-shrink: 0;
  }
  
  .promise-icon.environment {
    background: var(--success-100);
    color: var(--success-600);
  }
  
  .promise-icon.education {
    background: var(--primary-100);
    color: var(--primary-600);
  }
  
  .promise-content {
    flex: 1;
  }
  
  .promise-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-1);
  }
  
  .promise-header h4 {
    font-size: 0.95rem;
  }
  
  .category-badge {
    padding: 2px 6px;
    font-size: 0.6rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
  }
  
  .category-badge.environment {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .category-badge.education {
    background: var(--primary-100);
    color: var(--primary-700);
  }
  
  .promise-content p {
    font-size: 0.85rem;
    color: var(--gray-600);
    line-height: 1.5;
  }
  
  .remove-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    color: var(--gray-400);
    cursor: pointer;
    border-radius: var(--radius-md);
  }
  
  .remove-btn:hover {
    background: var(--error-50);
    color: var(--error-500);
  }
  
  /* Warning */
  .warning-notice {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--warning-50);
    border-radius: var(--radius-lg);
    border-left: 4px solid var(--warning-500);
  }
  
  .warning-notice :global(svg) {
    color: var(--warning-600);
    flex-shrink: 0;
  }
  
  .warning-notice strong {
    display: block;
    color: var(--warning-800);
    margin-bottom: var(--space-1);
  }
  
  .warning-notice p {
    font-size: 0.85rem;
    color: var(--gray-600);
    margin: 0;
  }
  
  /* Footer */
  .form-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6) 0;
    border-top: 1px solid var(--gray-200);
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .hash-preview {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .preview-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .action-buttons {
    display: flex;
    gap: var(--space-3);
  }
</style>
