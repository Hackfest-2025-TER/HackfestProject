<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { 
    Shield, Eye, EyeOff, Lock, Database, Server, 
    CheckCircle, XCircle, AlertTriangle, Fingerprint
  } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Privacy Policy - PromiseThread</title>
  <meta name="description" content="Learn how PromiseThread protects your privacy using zero-knowledge proofs and cryptographic techniques." />
</svelte:head>

<Header />

<main class="min-h-screen bg-white">
  <!-- Hero -->
  <section class="py-16 bg-gradient-to-br from-[#082770] to-[#0a3490]">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div class="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-6">
        <Shield class="w-8 h-8 text-white" />
      </div>
      <h1 class="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
      <p class="text-xl text-white/90">
        Your privacy isn't just a policy—it's built into our architecture.
      </p>
    </div>
  </section>
  
  <!-- TL;DR -->
  <section class="pb-12">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6">
        <h2 class="text-lg font-semibold text-emerald-400 mb-4">TL;DR - The Short Version</h2>
        <ul class="space-y-2 text-slate-300">
          <li class="flex items-start gap-2">
            <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span>We store <strong>zero personal information</strong> about voters</span>
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span>Your identity is protected by <strong>zero-knowledge cryptography</strong></span>
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span>We <strong>cannot see</strong> how you voted, even if we wanted to</span>
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span>No tracking, no cookies for analytics, no third-party data sharing</span>
          </li>
        </ul>
      </div>
    </div>
  </section>
  
  <!-- Main Content -->
  <section class="pb-20">
    <div class="max-w-4xl mx-auto px-4 space-y-12">
      
      <!-- What We Collect -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Database class="w-6 h-6 text-blue-400" />
          <h2 class="text-xl font-bold text-white">What We Store</h2>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-emerald-400 font-medium mb-3 flex items-center gap-2">
              <CheckCircle class="w-4 h-4" /> We Store
            </h3>
            <ul class="space-y-2 text-slate-300 text-sm">
              <li>• Anonymous nullifiers (random identifiers)</li>
              <li>• Credential hashes (not reversible)</li>
              <li>• Vote records linked to nullifiers</li>
              <li>• Public comments (anonymous)</li>
              <li>• Promise text and signatures</li>
            </ul>
          </div>
          <div>
            <h3 class="text-red-400 font-medium mb-3 flex items-center gap-2">
              <XCircle class="w-4 h-4" /> We Don't Store
            </h3>
            <ul class="space-y-2 text-slate-300 text-sm">
              <li>• Your name or real identity</li>
              <li>• Your voter ID or registration number</li>
              <li>• Your location or IP address</li>
              <li>• Any link between you and your votes</li>
              <li>• Browser fingerprints or device info</li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- Zero-Knowledge -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Fingerprint class="w-6 h-6 text-purple-400" />
          <h2 class="text-xl font-bold text-white">Zero-Knowledge Proofs</h2>
        </div>
        
        <p class="text-slate-300 mb-4">
          When you verify as a citizen, we use zero-knowledge proofs. This means:
        </p>
        
        <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600 mb-4">
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-purple-400 text-xs font-bold">1</span>
              </div>
              <p class="text-slate-300 text-sm">
                You prove you're a registered citizen <strong>without revealing which citizen you are</strong>
              </p>
            </div>
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-purple-400 text-xs font-bold">2</span>
              </div>
              <p class="text-slate-300 text-sm">
                We receive a cryptographic proof that verifies eligibility, but contains <strong>no identifying information</strong>
              </p>
            </div>
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-purple-400 text-xs font-bold">3</span>
              </div>
              <p class="text-slate-300 text-sm">
                You get an anonymous credential that <strong>cannot be traced back</strong> to your real identity
              </p>
            </div>
          </div>
        </div>
        
        <p class="text-slate-400 text-sm">
          This is mathematically guaranteed—not a policy we might change, but a fundamental property of the cryptography.
        </p>
      </div>
      
      <!-- Visibility -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Eye class="w-6 h-6 text-amber-400" />
          <h2 class="text-xl font-bold text-white">What's Public vs. Private</h2>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <div class="flex items-center gap-2 mb-3">
              <Eye class="w-5 h-5 text-amber-400" />
              <h3 class="text-white font-medium">Public (Everyone Sees)</h3>
            </div>
            <ul class="space-y-1 text-slate-300 text-sm">
              <li>• Promise text and commitments</li>
              <li>• Politician signatures</li>
              <li>• Vote aggregates (totals)</li>
              <li>• Discussion comments</li>
              <li>• Blockchain records</li>
            </ul>
          </div>
          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <div class="flex items-center gap-2 mb-3">
              <EyeOff class="w-5 h-5 text-purple-400" />
              <h3 class="text-white font-medium">Private (No One Sees)</h3>
            </div>
            <ul class="space-y-1 text-slate-300 text-sm">
              <li>• Your real identity</li>
              <li>• How you voted</li>
              <li>• Your voter registration ID</li>
              <li>• Which nullifier belongs to you</li>
              <li>• Any personal information</li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- Data Security -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Lock class="w-6 h-6 text-emerald-400" />
          <h2 class="text-xl font-bold text-white">Data Security</h2>
        </div>
        
        <div class="space-y-4 text-slate-300">
          <p>
            Our security model assumes the worst case: what if our servers are completely compromised?
          </p>
          <div class="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
            <div class="flex gap-3">
              <AlertTriangle class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 class="text-amber-400 font-medium mb-1">Even if we're hacked:</h4>
                <ul class="text-sm space-y-1">
                  <li>• Attackers cannot determine your real identity from nullifiers</li>
                  <li>• Blockchain records remain tamper-proof (we don't control them)</li>
                  <li>• Signatures cannot be forged (private keys are never stored)</li>
                  <li>• Vote tallies on blockchain cannot be altered</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Third Parties -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Server class="w-6 h-6 text-cyan-400" />
          <h2 class="text-xl font-bold text-white">Third Parties</h2>
        </div>
        
        <div class="space-y-4 text-slate-300">
          <p>We minimize third-party dependencies:</p>
          <ul class="space-y-2">
            <li class="flex items-start gap-2">
              <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span><strong>No Google Analytics</strong> or tracking scripts</span>
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span><strong>No advertising networks</strong></span>
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span><strong>No social media pixels</strong></span>
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span><strong>No data brokers</strong> or selling of information</span>
            </li>
          </ul>
          <p class="text-slate-400 text-sm mt-4">
            We use a public blockchain for immutability, which means vote aggregates are publicly visible—but 
            they contain no personal information.
          </p>
        </div>
      </div>
      
      <!-- Your Rights -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-6">
          <Shield class="w-6 h-6 text-rose-400" />
          <h2 class="text-xl font-bold text-white">Your Rights</h2>
        </div>
        
        <div class="space-y-4 text-slate-300">
          <p>Because we don't store personal data, traditional "data rights" work differently here:</p>
          <ul class="space-y-3">
            <li>
              <strong class="text-white">Right to Access:</strong> 
              <span class="text-slate-400">There's no personal data to access. Your nullifier is just a random string with no link to you.</span>
            </li>
            <li>
              <strong class="text-white">Right to Deletion:</strong> 
              <span class="text-slate-400">We can't delete what we don't have. Blockchain records are permanent by design—but they contain no personal data.</span>
            </li>
            <li>
              <strong class="text-white">Right to Portability:</strong> 
              <span class="text-slate-400">All data is public and verifiable. You can export blockchain records anytime.</span>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Contact -->
      <div class="bg-gradient-to-r from-purple-500/10 to-emerald-500/10 border border-purple-500/20 rounded-2xl p-6 text-center">
        <h2 class="text-xl font-bold text-white mb-4">Questions About Privacy?</h2>
        <p class="text-slate-300 mb-6">
          We're happy to explain our privacy architecture in more detail.
        </p>
        <a 
          href="/feedback" 
          class="inline-flex items-center gap-2 bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg transition-colors"
        >
          Contact Us
        </a>
      </div>
      
      <!-- Last Updated -->
      <p class="text-center text-slate-500 text-sm">
        Last updated: December 2024
      </p>
      
    </div>
  </section>
</main>

<Footer />
