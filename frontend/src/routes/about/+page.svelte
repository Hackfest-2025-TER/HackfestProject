<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { 
    Shield, Target, Users, Lock, Eye, Code, Heart,
    Github, Twitter, Globe, Mail, ExternalLink
  } from 'lucide-svelte';
</script>

<svelte:head>
  <title>About - PromiseThread</title>
  <meta name="description" content="Learn about PromiseThread's mission to create transparent political accountability through blockchain and zero-knowledge proofs." />
</svelte:head>

<Header />

<main class="min-h-screen bg-white">
  <!-- Hero -->
  <section class="py-20 bg-gradient-to-br from-[#082770] to-[#0a3490]">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div class="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-6">
        <Shield class="w-10 h-10 text-white" />
      </div>
      <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">About PromiseThread</h1>
      <p class="text-xl text-white/90 max-w-2xl mx-auto">
        A decentralized platform bringing transparency to political promises 
        while protecting citizen privacy through cryptography.
      </p>
    </div>
  </section>
  
  <!-- Mission -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <Target class="w-6 h-6 text-emerald-400" />
          </div>
          <h2 class="text-2xl font-bold text-white">Our Mission</h2>
        </div>
        <div class="space-y-4 text-slate-300 text-lg leading-relaxed">
          <p>
            Democracy works best when citizens can hold their representatives accountable. 
            But accountability requires memory—and in the age of information overload, 
            promises are easily forgotten, modified, or denied.
          </p>
          <p>
            <strong class="text-white">PromiseThread exists to solve this problem.</strong> 
            We create an immutable record of political promises that no one can alter after the fact. 
            We enable citizens to evaluate these promises anonymously, without fear of reprisal.
          </p>
          <p>
            Our goal is simple: <span class="text-emerald-400">transparent promises, private citizens, 
            trustworthy results.</span>
          </p>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Core Values -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <h2 class="text-2xl font-bold text-white text-center mb-12">Our Core Values</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mb-4">
            <Eye class="w-6 h-6 text-blue-400" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Transparency</h3>
          <p class="text-slate-400">
            All promises are public and permanent. Vote tallies are visible to everyone. 
            Our code is open source. We have nothing to hide.
          </p>
        </div>
        
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div class="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mb-4">
            <Lock class="w-6 h-6 text-purple-400" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Privacy</h3>
          <p class="text-slate-400">
            Citizens can participate without revealing their identity. Zero-knowledge proofs 
            ensure your vote counts without exposing who you are.
          </p>
        </div>
        
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div class="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center mb-4">
            <Shield class="w-6 h-6 text-amber-400" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Security</h3>
          <p class="text-slate-400">
            Blockchain makes records tamper-proof. Cryptographic signatures prevent forgery. 
            Even if our servers are compromised, the truth remains verifiable.
          </p>
        </div>
        
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center mb-4">
            <Users class="w-6 h-6 text-rose-400" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Non-Partisan</h3>
          <p class="text-slate-400">
            We don't take sides. Every politician's promises are treated equally. 
            The platform is a neutral ground for accountability.
          </p>
        </div>
      </div>
    </div>
  </section>
  
  <!-- How We're Different -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-gradient-to-r from-emerald-500/10 to-blue-500/10 border border-emerald-500/20 rounded-2xl p-8">
        <h2 class="text-2xl font-bold text-white mb-6 text-center">What Makes Us Different</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="text-4xl font-bold text-emerald-400 mb-2">0</div>
            <div class="text-slate-300">Personal data stored</div>
            <p class="text-slate-500 text-sm mt-2">
              We don't know who you are. By design.
            </p>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-blue-400 mb-2">∞</div>
            <div class="text-slate-300">Data retention</div>
            <p class="text-slate-500 text-sm mt-2">
              Blockchain records are permanent.
            </p>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-purple-400 mb-2">100%</div>
            <div class="text-slate-300">Verifiable</div>
            <p class="text-slate-500 text-sm mt-2">
              Don't trust—verify everything yourself.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Technology -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
          <Code class="w-6 h-6 text-cyan-400" />
        </div>
        <h2 class="text-2xl font-bold text-white">Our Technology Stack</h2>
      </div>
      
      <div class="grid md:grid-cols-2 gap-4">
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 class="text-white font-medium mb-2">Frontend</h3>
          <p class="text-slate-400 text-sm">SvelteKit, TypeScript, TailwindCSS</p>
        </div>
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 class="text-white font-medium mb-2">Backend</h3>
          <p class="text-slate-400 text-sm">FastAPI, Python, PostgreSQL</p>
        </div>
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 class="text-white font-medium mb-2">Blockchain</h3>
          <p class="text-slate-400 text-sm">Solidity, Hardhat, Web3.py</p>
        </div>
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 class="text-white font-medium mb-2">Zero-Knowledge</h3>
          <p class="text-slate-400 text-sm">Circom, SnarkJS, Groth16</p>
        </div>
      </div>
      
      <div class="mt-6 text-center">
        <a 
          href="https://github.com/promisethread" 
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <Github class="w-5 h-5" />
          View on GitHub
          <ExternalLink class="w-4 h-4" />
        </a>
      </div>
    </div>
  </section>
  
  <!-- Team -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="text-center mb-12">
        <div class="flex items-center justify-center gap-3 mb-4">
          <Heart class="w-6 h-6 text-rose-400" />
          <h2 class="text-2xl font-bold text-white">Built with ❤️ for Democracy</h2>
        </div>
        <p class="text-slate-400">
          PromiseThread is a hackathon project demonstrating how technology 
          can enhance democratic accountability.
        </p>
      </div>
      
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-8 text-center">
        <p class="text-slate-300 mb-6">
          This platform was created during a hackfest to explore the intersection of 
          blockchain, zero-knowledge proofs, and civic technology. Our goal is to 
          show what's possible when we apply cutting-edge cryptography to real-world 
          democratic challenges.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <a 
            href="/guide" 
            class="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg transition-colors"
          >
            Learn How It Works
          </a>
          <a 
            href="/faq" 
            class="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors"
          >
            Read FAQ
          </a>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Contact -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-8 text-center">
        <h2 class="text-2xl font-bold text-white mb-4">Get in Touch</h2>
        <p class="text-slate-400 mb-6">
          Questions, feedback, or want to contribute? We'd love to hear from you.
        </p>
        <div class="flex flex-wrap justify-center gap-6">
          <a href="/feedback" class="flex items-center gap-2 text-slate-300 hover:text-emerald-400 transition-colors">
            <Mail class="w-5 h-5" />
            Send Feedback
          </a>
          <a href="https://github.com/promisethread" target="_blank" rel="noopener" class="flex items-center gap-2 text-slate-300 hover:text-emerald-400 transition-colors">
            <Github class="w-5 h-5" />
            GitHub
          </a>
          <a href="https://twitter.com/promisethread" target="_blank" rel="noopener" class="flex items-center gap-2 text-slate-300 hover:text-emerald-400 transition-colors">
            <Twitter class="w-5 h-5" />
            Twitter
          </a>
        </div>
      </div>
    </div>
  </section>
</main>

<Footer />
