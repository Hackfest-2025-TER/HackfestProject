<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import StatCard from '$lib/components/StatCard.svelte';
  import BlockchainVisualizer from '$lib/components/BlockchainVisualizer.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, Activity, Server, AlertTriangle, CheckCircle, Zap, Globe, Search, RefreshCw } from 'lucide-svelte';
  
  // Network stats
  const networkStats = {
    stability: 'Stable',
    uptime: 99.99,
    lastHeartbeat: 12,
    activeNodes: 142,
    blockHeight: 12402192,
    hashRate: '420 TH/s',
    peers: { current: 842, max: 850 },
    integrityCoefficient: 99.9,
    anomalies: 0
  };
  
  // Audit log entries
  const auditLogs = [
    { timestamp: '10:42:01.242', blockHash: '0x8a7...f92b', actionType: 'New Vote Block', status: 'Verified' },
    { timestamp: '10:42:00.891', blockHash: '0x3c2...e11a', actionType: 'Node Sync', status: 'Confirmed' },
    { timestamp: '10:41:59.430', blockHash: '0x1b9...c00d', actionType: 'Manifesto Update', status: 'Signed' },
    { timestamp: '10:41:58.112', blockHash: '0x7f4...a33e', actionType: 'Vote Batch #22', status: 'ZK-Proof Valid' },
    { timestamp: '10:41:56.004', blockHash: '0x9d2...b11c', actionType: 'System Check', status: 'Pass' },
    { timestamp: '10:41:55.221', blockHash: '0x4e1...e55f', actionType: 'Node Join', status: 'Accepted' }
  ];
  
  // Sample blocks for visualization
  const blocks = [
    { height: 12402190, hash: '0x8a7f...9b2c', previousHash: '0x0000...0000', merkleRoot: '0x4f2a...8d1e', timestamp: '2024-10-14T10:41:55Z', transactions: 42, validator: 'Node_Alpha' },
    { height: 12402191, hash: '0x3c2e...f11a', previousHash: '0x8a7f...9b2c', merkleRoot: '0x7b3c...2f4a', timestamp: '2024-10-14T10:41:58Z', transactions: 38, validator: 'Node_Beta' },
    { height: 12402192, hash: '0x1b9d...c00d', previousHash: '0x3c2e...f11a', merkleRoot: '0x9e5d...1c7b', timestamp: '2024-10-14T10:42:01Z', transactions: 55, validator: 'Node_Gamma' }
  ];
  
  // Node distribution
  const nodeDistribution = [
    { region: 'North America', count: 42 },
    { region: 'Europe', count: 58 },
    { region: 'Asia', count: 31 },
    { region: 'Other', count: 11 }
  ];
  
  let verifyHash = '';
  
  const statusColors = {
    'Verified': 'success',
    'Confirmed': 'success',
    'Signed': 'primary',
    'ZK-Proof Valid': 'success',
    'Pass': 'success',
    'Accepted': 'success'
  };
</script>

<svelte:head>
  <title>Network Integrity Dashboard - PromiseThread</title>
</svelte:head>

<Header variant="default" />

<main class="audit-page">
  <div class="container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-badge">SYSTEM DIAGNOSTIC: TRUST LAYER 1</div>
      <h1>Network Integrity Dashboard</h1>
      <p>Real-time cryptographic verification, consensus monitoring, and anomaly detection for the 2024 General Election.</p>
      <div class="last-audit">
        <span class="audit-label">LAST AUDIT CYCLE</span>
        <span class="audit-value">Block #8,921,084 • 24s ago</span>
        <button class="refresh-btn">
          <RefreshCw size={14} />
        </button>
      </div>
    </div>
    
    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">SYSTEM STABILITY</span>
          <Activity size={20} />
        </div>
        <div class="stat-value status-indicator">
          <span class="status-dot online"></span>
          {networkStats.stability}
        </div>
        <div class="stat-bar">
          <div class="stat-fill" style="width: {networkStats.uptime}%"></div>
        </div>
        <span class="stat-meta">Uptime: {networkStats.uptime}% (Last 30 days)</span>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">LAST HEARTBEAT</span>
          <Zap size={20} />
        </div>
        <div class="stat-value">{networkStats.lastHeartbeat}ms</div>
        <div class="heartbeat-viz">
          <span class="beat"></span>
          <span class="beat"></span>
          <span class="beat"></span>
          <span class="beat"></span>
        </div>
        <span class="stat-meta">Sync latency optimal</span>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">ACTIVE AUDITORS</span>
          <Server size={20} />
        </div>
        <div class="stat-value">
          {networkStats.activeNodes} Nodes
          <span class="node-change">+39</span>
        </div>
        <div class="node-icons">
          <span class="node-icon active"></span>
          <span class="node-icon active"></span>
          <span class="node-icon"></span>
        </div>
        <span class="stat-meta">Global consensus reached</span>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">THREAT DETECTION</span>
          <AlertTriangle size={20} />
        </div>
        <div class="stat-value">{networkStats.anomalies} Anomalies</div>
        <span class="stat-meta success">
          <Shield size={14} />
          Network secure & encrypted
        </span>
      </div>
    </div>
    
    <!-- Main Grid -->
    <div class="main-grid">
      <!-- Integrity Coefficient -->
      <div class="integrity-card card">
        <div class="integrity-header">
          <div>
            <h3>Integrity Coefficient</h3>
            <p>Weighted score based on block validation, node consensus, and timestamp accuracy.</p>
          </div>
          <span class="layer-badge">Layer 1 Verified</span>
        </div>
        
        <div class="integrity-score">
          <span class="score-value">{networkStats.integrityCoefficient}%</span>
          <span class="score-status">
            <CheckCircle size={18} />
            Optimal State
          </span>
        </div>
        
        <div class="network-stats">
          <div class="network-stat">
            <span class="network-label">BLOCK HEIGHT</span>
            <span class="network-value">{networkStats.blockHeight.toLocaleString()}</span>
          </div>
          <div class="network-stat">
            <span class="network-label">HASH RATE</span>
            <span class="network-value">{networkStats.hashRate}</span>
          </div>
          <div class="network-stat">
            <span class="network-label">PEERS</span>
            <span class="network-value">{networkStats.peers.current}/{networkStats.peers.max}</span>
          </div>
        </div>
      </div>
      
      <!-- Manual Verification -->
      <div class="verify-card card">
        <h3>Manual Verification</h3>
        <p>Enter a transaction hash or ballot ID to independently verify its presence in the immutable ledger.</p>
        
        <div class="verify-input">
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Enter Hash (e.g., 0x4f...692)"
            bind:value={verifyHash}
          />
        </div>
        
        <button class="btn btn-success btn-lg verify-btn">
          Verify Ledger →
        </button>
      </div>
    </div>
    
    <!-- Ledger Feed & Node Distribution -->
    <div class="feed-grid">
      <!-- Cryptographic Ledger Feed -->
      <div class="feed-card card">
        <div class="feed-header">
          <div class="feed-title">
            <Shield size={18} />
            <h3>Cryptographic Ledger Feed</h3>
          </div>
          <span class="live-badge">
            <span class="live-dot"></span>
            Live Updates
          </span>
        </div>
        
        <table class="feed-table">
          <thead>
            <tr>
              <th>TIMESTAMP</th>
              <th>BLOCK HASH</th>
              <th>ACTION TYPE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {#each auditLogs as log}
              <tr>
                <td class="timestamp">{log.timestamp}</td>
                <td><HashDisplay hash={log.blockHash} /></td>
                <td>{log.actionType}</td>
                <td>
                  <span class="status-tag {statusColors[log.status] || 'primary'}">
                    {log.status}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      
      <!-- Node Distribution -->
      <div class="nodes-card card">
        <div class="nodes-header">
          <Globe size={18} />
          <h3>Node Distribution</h3>
        </div>
        
        <div class="globe-placeholder">
          <div class="globe-visual">
            <div class="globe-ring"></div>
            <div class="globe-ring"></div>
            <div class="globe-ring"></div>
          </div>
        </div>
        
        <div class="node-list">
          {#each nodeDistribution as region}
            <div class="node-region">
              <span class="region-name">{region.region}:</span>
              <span class="region-count">{region.count} Nodes</span>
            </div>
          {/each}
        </div>
      </div>
    </div>
    
    <!-- Blockchain Visualizer -->
    <div class="blockchain-section card">
      <h3>Recent Blocks</h3>
      <BlockchainVisualizer {blocks} />
    </div>
  </div>
  
  <!-- Footer Status Bar -->
  <div class="status-bar">
    <div class="status-item">
      <Shield size={14} />
      Audit Trail ID: #8921-X-2024
    </div>
    <div class="status-links">
      <a href="/privacy">Privacy Protocol</a>
      <a href="/docs">Node Documentation</a>
      <a href="/license">Open Source License</a>
    </div>
    <div class="status-item">
      Powered by OpenElection Protocol v2.4.1
    </div>
  </div>
</main>

<Footer />

<style>
  .audit-page {
    min-height: 100vh;
    background: var(--gray-900);
    color: white;
  }
  
  .container {
    max-width: 1280px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  .card {
    background: var(--gray-800);
    border-color: var(--gray-700);
  }
  
  /* Page Header */
  .page-header {
    margin-bottom: var(--space-8);
  }
  
  .header-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    background: var(--success-500);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
    letter-spacing: 0.05em;
    margin-bottom: var(--space-3);
  }
  
  .page-header h1 {
    color: white;
    font-size: 2rem;
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-400);
    max-width: 600px;
  }
  
  .last-audit {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-top: var(--space-4);
    padding: var(--space-3);
    background: var(--gray-800);
    border-radius: var(--radius-lg);
    width: fit-content;
  }
  
  .audit-label {
    font-size: 0.65rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .audit-value {
    font-family: var(--font-mono);
    font-size: 0.875rem;
    color: var(--gray-300);
  }
  
  .refresh-btn {
    width: 28px;
    height: 28px;
    border: none;
    background: var(--gray-700);
    color: var(--gray-400);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .refresh-btn:hover {
    background: var(--gray-600);
    color: white;
  }
  
  /* Stats Grid */
  .stats-grid {
    display: grid;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .stats-grid {
      grid-template-columns: repeat(4, 1fr);
    }
  }
  
  .stat-card {
    padding: var(--space-5);
  }
  
  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
    color: var(--gray-500);
  }
  
  .stat-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gray-400);
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: var(--space-2);
  }
  
  .status-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
    box-shadow: 0 0 8px var(--success-500);
  }
  
  .stat-bar {
    height: 4px;
    background: var(--gray-700);
    border-radius: var(--radius-full);
    margin-bottom: var(--space-2);
  }
  
  .stat-fill {
    height: 100%;
    background: var(--success-500);
    border-radius: var(--radius-full);
  }
  
  .stat-meta {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .stat-meta.success {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    color: var(--success-500);
  }
  
  .node-change {
    font-size: 0.875rem;
    color: var(--success-500);
    font-weight: 500;
    margin-left: var(--space-2);
  }
  
  .heartbeat-viz {
    display: flex;
    gap: 4px;
    margin-bottom: var(--space-2);
  }
  
  .beat {
    width: 8px;
    height: 20px;
    background: var(--success-500);
    border-radius: 2px;
    animation: beat 1s ease infinite;
  }
  
  .beat:nth-child(2) { animation-delay: 0.2s; }
  .beat:nth-child(3) { animation-delay: 0.4s; }
  .beat:nth-child(4) { animation-delay: 0.6s; }
  
  @keyframes beat {
    0%, 100% { transform: scaleY(0.5); }
    50% { transform: scaleY(1); }
  }
  
  .node-icons {
    display: flex;
    gap: 4px;
    margin-bottom: var(--space-2);
  }
  
  .node-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--gray-700);
  }
  
  .node-icon.active {
    background: var(--gray-600);
  }
  
  /* Main Grid */
  .main-grid {
    display: grid;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .main-grid {
      grid-template-columns: 2fr 1fr;
    }
  }
  
  .integrity-card {
    padding: var(--space-6);
  }
  
  .integrity-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-6);
  }
  
  .integrity-header h3 {
    color: white;
    margin-bottom: var(--space-1);
  }
  
  .integrity-header p {
    font-size: 0.875rem;
    color: var(--gray-400);
  }
  
  .layer-badge {
    padding: var(--space-2) var(--space-3);
    background: var(--success-500);
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: var(--radius-full);
  }
  
  .integrity-score {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    margin-bottom: var(--space-6);
  }
  
  .score-value {
    font-size: 4rem;
    font-weight: 700;
    color: var(--success-400);
    line-height: 1;
  }
  
  .score-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--success-400);
    font-weight: 500;
  }
  
  .network-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
  }
  
  .network-stat {
    padding: var(--space-3);
    background: var(--gray-700);
    border-radius: var(--radius-lg);
  }
  
  .network-label {
    display: block;
    font-size: 0.65rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-1);
  }
  
  .network-value {
    font-family: var(--font-mono);
    font-size: 1rem;
    color: white;
  }
  
  /* Verify Card */
  .verify-card {
    padding: var(--space-5);
  }
  
  .verify-card h3 {
    color: white;
    margin-bottom: var(--space-2);
  }
  
  .verify-card p {
    font-size: 0.875rem;
    color: var(--gray-400);
    margin-bottom: var(--space-4);
  }
  
  .verify-input {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--gray-700);
    border: 1px solid var(--gray-600);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
  }
  
  .verify-input :global(svg) {
    color: var(--gray-500);
  }
  
  .verify-input input {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    font-size: 0.875rem;
    outline: none;
  }
  
  .verify-input input::placeholder {
    color: var(--gray-500);
  }
  
  .verify-btn {
    width: 100%;
  }
  
  /* Feed Grid */
  .feed-grid {
    display: grid;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .feed-grid {
      grid-template-columns: 2fr 1fr;
    }
  }
  
  .feed-card {
    overflow: hidden;
  }
  
  .feed-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-bottom: 1px solid var(--gray-700);
  }
  
  .feed-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .feed-title h3 {
    color: white;
    font-size: 1rem;
  }
  
  .live-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .live-dot {
    width: 8px;
    height: 8px;
    background: var(--success-500);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  
  .feed-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .feed-table th {
    text-align: left;
    padding: var(--space-3) var(--space-4);
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: var(--gray-750, rgba(55, 65, 81, 0.5));
  }
  
  .feed-table td {
    padding: var(--space-3) var(--space-4);
    font-size: 0.8rem;
    color: var(--gray-300);
    border-bottom: 1px solid var(--gray-700);
  }
  
  .timestamp {
    font-family: var(--font-mono);
    color: var(--gray-500);
  }
  
  .status-tag {
    padding: var(--space-1) var(--space-2);
    font-size: 0.7rem;
    font-weight: 500;
    border-radius: var(--radius-sm);
  }
  
  .status-tag.success {
    color: var(--success-400);
  }
  
  .status-tag.primary {
    color: var(--primary-400);
  }
  
  /* Nodes Card */
  .nodes-card {
    padding: var(--space-4);
  }
  
  .nodes-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
    color: var(--success-400);
  }
  
  .nodes-header h3 {
    color: white;
    font-size: 1rem;
  }
  
  .globe-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: var(--space-8);
  }
  
  .globe-visual {
    position: relative;
    width: 120px;
    height: 120px;
  }
  
  .globe-ring {
    position: absolute;
    border: 2px solid var(--success-500);
    border-radius: 50%;
    opacity: 0.3;
  }
  
  .globe-ring:nth-child(1) {
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }
  
  .globe-ring:nth-child(2) {
    width: 70%;
    height: 100%;
    top: 0;
    left: 15%;
  }
  
  .globe-ring:nth-child(3) {
    width: 100%;
    height: 70%;
    top: 15%;
    left: 0;
  }
  
  .node-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .node-region {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
  }
  
  .region-name {
    color: var(--gray-400);
  }
  
  .region-count {
    color: var(--gray-300);
  }
  
  /* Blockchain Section */
  .blockchain-section {
    padding: var(--space-4);
  }
  
  .blockchain-section h3 {
    color: white;
    margin-bottom: var(--space-4);
    padding: 0 var(--space-4);
  }
  
  /* Status Bar */
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
    padding: var(--space-4) var(--space-6);
    background: var(--gray-800);
    border-top: 1px solid var(--gray-700);
  }
  
  .status-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .status-links {
    display: flex;
    gap: var(--space-4);
  }
  
  .status-links a {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .status-links a:hover {
    color: white;
  }
</style>
