<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { ChevronDown, HelpCircle, Shield, Lock, Vote, Eye, Users, AlertTriangle } from 'lucide-svelte';
  
  interface FAQ {
    question: string;
    answer: string;
    category: string;
  }
  
  const faqs: FAQ[] = [
    // General
    {
      category: 'General',
      question: 'What is PromiseThread?',
      answer: 'PromiseThread is a decentralized platform for tracking political promises. It uses blockchain technology to make promises immutable and zero-knowledge proofs to enable anonymous citizen voting. The goal is transparent political accountability while protecting voter privacy.'
    },
    {
      category: 'General',
      question: 'Who can use this platform?',
      answer: 'Anyone can browse and view promises. To vote on promises, you need to verify yourself as a citizen using our zero-knowledge proof system. Politicians can create and sign promises using their cryptographic wallets.'
    },
    {
      category: 'General',
      question: 'Is this platform affiliated with any government or political party?',
      answer: 'No. PromiseThread is an independent, non-partisan platform. We do not endorse any political party or candidate. Our goal is simply to provide transparent tracking of political promises.'
    },
    
    // Privacy
    {
      category: 'Privacy',
      question: 'How is my privacy protected when voting?',
      answer: 'We use zero-knowledge proofs (ZKP) to verify you are a citizen without knowing who you are. You receive an anonymous "nullifier" that cannot be traced back to your identity. Your vote is linked to this nullifier, not to you personally.'
    },
    {
      category: 'Privacy',
      question: 'What data do you store about me?',
      answer: 'We store zero personal information about voters. When you verify, we only store your anonymous nullifier and credential hash. These cannot be reversed to reveal your identity. There is no link between your real identity and your voting activity.'
    },
    {
      category: 'Privacy',
      question: 'Can anyone see how I voted?',
      answer: 'No. Individual votes are linked to anonymous nullifiers, not real identities. Only vote aggregates (totals) are visible. Even we cannot determine how any specific person voted.'
    },
    
    // Blockchain
    {
      category: 'Blockchain',
      question: 'Why use blockchain?',
      answer: 'Blockchain provides immutability—once data is recorded, it cannot be changed or deleted. This means politicians cannot alter their promises after the fact, and vote results cannot be manipulated. Anyone can verify the data independently.'
    },
    {
      category: 'Blockchain',
      question: 'What goes on the blockchain vs. the database?',
      answer: 'ON-CHAIN: Promise hashes, digital signatures, vote aggregates, timestamps. OFF-CHAIN: Full promise text, discussion threads, individual vote records (anonymous). This hybrid approach keeps costs low while maintaining security where it matters.'
    },
    {
      category: 'Blockchain',
      question: 'Which blockchain do you use?',
      answer: 'We use an Ethereum-compatible blockchain (currently a local Hardhat network for development, with plans to deploy to Polygon or similar L2 for production). This ensures low transaction costs while maintaining security.'
    },
    {
      category: 'Blockchain',
      question: 'Can I verify blockchain data myself?',
      answer: 'Yes! All blockchain data is public. You can query our smart contracts directly using any Web3 library or blockchain explorer. Our verification page provides tools to compare local hashes with on-chain data.'
    },
    
    // Voting
    {
      category: 'Voting',
      question: 'How does voting work?',
      answer: 'After verifying as a citizen, you can vote "Kept" or "Broken" on any promise whose grace period has ended. Each citizen can vote once per promise (but can change their vote). Votes are tallied, and if 60%+ vote "Kept", the promise is marked fulfilled.'
    },
    {
      category: 'Voting',
      question: 'What is a grace period?',
      answer: 'A grace period is the time between when a promise is made and when voting opens. This gives politicians time to work on their promises before being evaluated. Typically 6-12 months depending on the promise.'
    },
    {
      category: 'Voting',
      question: 'Can I change my vote?',
      answer: 'Yes, you can change your vote as long as the voting period is still open. Your previous vote will be replaced with your new vote. The system tracks your latest vote only.'
    },
    {
      category: 'Voting',
      question: 'How do you prevent double voting?',
      answer: 'Your anonymous nullifier is unique and can only vote once per promise. The system checks if your nullifier has already voted before accepting a new vote. This prevents Sybil attacks while maintaining anonymity.'
    },
    
    // Politicians
    {
      category: 'Politicians',
      question: 'How do politicians post promises?',
      answer: 'Politicians receive a cryptographic wallet (key pair). They write their promise, sign it with their private key (in their browser), and submit it. The signature proves authorship without the platform ever seeing the private key.'
    },
    {
      category: 'Politicians',
      question: 'Can politicians edit their promises after posting?',
      answer: 'No. Once a promise is signed and recorded on blockchain, it cannot be edited. The hash of the promise text is permanently stored. Any alteration would produce a different hash, immediately exposing the tampering.'
    },
    {
      category: 'Politicians',
      question: 'What if a politician loses their key?',
      answer: 'We support key rotation. A politician can request a new key, which will be logged publicly. All promises signed with the old key remain valid and verifiable. New promises will use the new key.'
    },
    
    // Security
    {
      category: 'Security',
      question: 'What if your servers are hacked?',
      answer: 'Critical data (hashes, signatures, vote totals) lives on blockchain, which we don\'t control. Hackers could not alter promise text without the hash mismatch being detected. They could not forge signatures without private keys. Vote aggregates on blockchain remain tamper-proof.'
    },
    {
      category: 'Security',
      question: 'How do I know you\'re not manipulating results?',
      answer: 'You don\'t have to trust us—verify! All blockchain data is public. You can independently compute hashes, verify signatures, and check vote tallies. Our code is open source. The math doesn\'t lie.'
    },
    {
      category: 'Security',
      question: 'What cryptographic algorithms do you use?',
      answer: 'SHA-256 for hashing, ECDSA (secp256k1) for signatures, and zk-SNARKs (Groth16) for zero-knowledge proofs. These are industry-standard, battle-tested algorithms used by Bitcoin, Ethereum, and Zcash.'
    }
  ];
  
  let openFAQ: number | null = null;
  let activeCategory = 'All';
  
  $: filteredFAQs = activeCategory === 'All' 
    ? faqs 
    : faqs.filter(f => f.category === activeCategory);
  
  const categories = ['All', ...new Set(faqs.map(f => f.category))];
  
  const categoryIcons: Record<string, any> = {
    'General': HelpCircle,
    'Privacy': Shield,
    'Blockchain': Lock,
    'Voting': Vote,
    'Politicians': Users,
    'Security': AlertTriangle
  };
</script>

<svelte:head>
  <title>FAQ - PromiseThread</title>
  <meta name="description" content="Frequently asked questions about PromiseThread - the decentralized political promise tracking platform." />
</svelte:head>

<Header />

<main class="min-h-screen bg-white">
  <!-- Hero -->
  <section class="py-16 bg-gradient-to-br from-[#082770] to-[#0a3490]">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div class="inline-flex items-center gap-2 bg-white/20 border border-white/30 rounded-full px-4 py-2 mb-6">
        <HelpCircle class="w-4 h-4 text-white" />
        <span class="text-white text-sm font-medium">Help Center</span>
      </div>
      <h1 class="text-4xl font-bold text-white mb-4">Frequently Asked Questions</h1>
      <p class="text-xl text-white/90">
        Everything you need to know about PromiseThread
      </p>
    </div>
  </section>
  
  <!-- Category Filters -->
  <section class="pb-8 pt-8 bg-gray-50">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex flex-wrap justify-center gap-2">
        {#each categories as category}
          <button
            on:click={() => activeCategory = category}
            class="px-4 py-2 rounded-full text-sm font-medium transition-all
              {activeCategory === category 
                ? 'bg-emerald-500 text-white' 
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}"
          >
            {category}
          </button>
        {/each}
      </div>
    </div>
  </section>
  
  <!-- FAQ List -->
  <section class="pb-20">
    <div class="max-w-3xl mx-auto px-4">
      <div class="space-y-3">
        {#each filteredFAQs as faq, i}
          <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
            <button
              on:click={() => openFAQ = openFAQ === i ? null : i}
              class="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-800/80 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">
                  <svelte:component 
                    this={categoryIcons[faq.category] || HelpCircle} 
                    class="w-4 h-4 text-emerald-400" 
                  />
                </div>
                <span class="text-white font-medium">{faq.question}</span>
              </div>
              <ChevronDown 
                class="w-5 h-5 text-slate-400 transition-transform flex-shrink-0 ml-4
                  {openFAQ === i ? 'rotate-180' : ''}" 
              />
            </button>
            
            {#if openFAQ === i}
              <div class="px-6 pb-4">
                <div class="pl-11 text-slate-300 leading-relaxed">
                  {faq.answer}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
      
      <!-- Contact CTA -->
      <div class="mt-12 text-center">
        <p class="text-slate-400 mb-4">Still have questions?</p>
        <a 
          href="/feedback" 
          class="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg transition-colors"
        >
          Send us a message
        </a>
      </div>
    </div>
  </section>
</main>

<Footer />
