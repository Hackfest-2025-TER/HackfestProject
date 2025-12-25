<script lang="ts">
  import {
    ChevronDown,
    HelpCircle,
    Shield,
    Lock,
    Vote,
    Eye,
    Users,
    AlertTriangle,
  } from "lucide-svelte";

  interface FAQ {
    question: string;
    answer: string;
    category: string;
  }

  const faqs: FAQ[] = [
    // General
    {
      category: "General",
      question: "What is PromiseThread?",
      answer:
        "PromiseThread is a platform for tracking political promises. It uses advanced technology to make promises permanent and enables anonymous citizen feedback. The goal is transparent political accountability while protecting voter privacy.",
    },
    {
      category: "General",
      question: "Who can use this platform?",
      answer:
        "Anyone can browse and view promises. To provide feedback on promises, you need to verify yourself as a citizen using our secure verification system. Representatives can create and sign promises using their secure accounts.",
    },
    {
      category: "General",
      question:
        "Is this platform affiliated with any government or political party?",
      answer:
        "No. PromiseThread is an independent, non-partisan platform. We do not endorse any political party or candidate. Our goal is simply to provide transparent tracking of political promises.",
    },

    // Privacy
    {
      category: "Privacy",
      question: "How is my privacy protected when giving feedback?",
      answer:
        "We use advanced cryptographic techniques to verify you are a citizen without knowing who you are. You receive an anonymous identifier that cannot be traced back to your identity. Your feedback is linked to this identifier, not to you personally.",
    },
    {
      category: "Privacy",
      question: "What data do you store about me?",
      answer:
        "We store zero personal information about citizens who provide feedback. When you verify, we only store your anonymous identifier. This cannot be reversed to reveal your identity. There is no link between your real identity and your feedback.",
    },
    {
      category: "Privacy",
      question: "Can anyone see how I voted?",
      answer:
        "No. Individual feedback is linked to anonymous identifiers, not real identities. Only aggregate totals are visible. Even we cannot determine how any specific person voted.",
    },

    // How It Works
    {
      category: "How It Works",
      question: "How are promises kept safe from tampering?",
      answer:
        "When a promise is published, we create a unique digital fingerprint of its content. This fingerprint is stored permanently. If anyone tries to change the promise, the fingerprint would not match, immediately exposing the tampering.",
    },
    {
      category: "How It Works",
      question: "Can I verify data myself?",
      answer:
        "Yes! All promise data is publicly verifiable. Our verification page provides tools to compare promise content with stored fingerprints. You can confirm that promises have not been altered since publication.",
    },

    // Feedback
    {
      category: "Feedback",
      question: "How does feedback work?",
      answer:
        'After verifying as a citizen, you can mark any promise as "Being Kept" or "Not Being Kept" once its review period has started. Each citizen can provide feedback once per promise. Community consensus is shown as a percentage.',
    },
    {
      category: "Feedback",
      question: "What is a grace period?",
      answer:
        "A grace period is the time between when a promise is made and when feedback opens. This gives politicians time to work on their promises before being evaluated. Typically 6-12 months depending on the promise.",
    },
    {
      category: "Feedback",
      question: "Can I change my feedback?",
      answer:
        "No, feedback is permanent once submitted. This ensures the integrity of the community consensus and prevents manipulation of results over time.",
    },
    {
      category: "Feedback",
      question: "How do you prevent fake accounts?",
      answer:
        "Your anonymous identifier is unique and verified. The system checks if your identifier has already been used before accepting new feedback. This prevents abuse while maintaining anonymity.",
    },

    // Representatives
    {
      category: "Representatives",
      question: "How do politicians post promises?",
      answer:
        "Representatives receive a secure account with digital signing capability. They write their promise, sign it digitally (in their browser), and submit it. The signature proves authorship without exposing any private credentials.",
    },
    {
      category: "Representatives",
      question: "Can politicians edit their promises after posting?",
      answer:
        "No. Once a promise is signed and recorded, it cannot be edited. The digital fingerprint of the promise is permanently stored. Any alteration would produce a different fingerprint, immediately exposing the tampering.",
    },

    // Security
    {
      category: "Security",
      question: "How do I know you're not manipulating results?",
      answer:
        "You don't have to trust us—verify! All data is cryptographically secured. You can independently verify promise fingerprints and check that records match. Our code is open source. The math doesn't lie.",
    },
    {
      category: "Security",
      question: "What if your servers are compromised?",
      answer:
        "Critical data like fingerprints and signatures are cryptographically protected. Attackers could not alter promise content without the fingerprint mismatch being detected. They could not forge signatures without private keys.",
    },
  ];

  let openFAQ: number | null = null;
  let activeCategory = "All";

  $: filteredFAQs =
    activeCategory === "All"
      ? faqs
      : faqs.filter((f) => f.category === activeCategory);

  const categories = ["All", ...new Set(faqs.map((f) => f.category))];

  const categoryIcons: Record<string, any> = {
    General: HelpCircle,
    Privacy: Shield,
    "How It Works": Lock,
    Feedback: Vote,
    Representatives: Users,
    Security: AlertTriangle,
  };
</script>

<svelte:head>
  <title>FAQ - PromiseThread</title>
  <meta
    name="description"
    content="Frequently asked questions about PromiseThread - the political promise tracking platform."
  />
</svelte:head>

<main class="min-h-screen bg-gray-50">
  <!-- Hero -->
  <section class="py-16 bg-gradient-to-br from-primary-700 to-primary-800">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div
        class="inline-flex items-center gap-2 bg-white/20 border border-white/30 rounded-full px-4 py-2 mb-6"
      >
        <HelpCircle class="w-4 h-4 text-white" />
        <span class="text-white text-sm font-medium">Help Center</span>
      </div>
      <h1 class="text-4xl font-bold font-serif text-white mb-4">
        Frequently Asked Questions
      </h1>
      <p class="text-xl text-white/90">
        Everything you need to know about PromiseThread
      </p>
    </div>
  </section>

  <!-- Category Filters -->
  <section class="pb-8 pt-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex flex-wrap justify-center gap-2">
        {#each categories as category}
          <button
            on:click={() => (activeCategory = category)}
            class="px-4 py-2 rounded-full text-sm font-medium transition-all
              {activeCategory === category
              ? 'bg-primary-700 text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'}"
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
          <div
            class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
          >
            <button
              on:click={() => (openFAQ = openFAQ === i ? null : i)}
              class="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0"
                >
                  <svelte:component
                    this={categoryIcons[faq.category] || HelpCircle}
                    class="w-4 h-4 text-primary-600"
                  />
                </div>
                <span class="text-gray-900 font-medium">{faq.question}</span>
              </div>
              <ChevronDown
                class="w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ml-4
                  {openFAQ === i ? 'rotate-180' : ''}"
              />
            </button>

            {#if openFAQ === i}
              <div class="px-6 pb-4">
                <div class="pl-11 text-gray-600 leading-relaxed">
                  {faq.answer}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Contact CTA -->
      <div class="mt-12 text-center">
        <p class="text-gray-500 mb-4">Still have questions?</p>
        <a
          href="/feedback"
          class="inline-flex items-center gap-2 bg-primary-700 hover:bg-primary-800 text-white px-6 py-3 rounded-lg transition-colors"
        >
          Send us a message
        </a>
      </div>
    </div>
  </section>
</main>
