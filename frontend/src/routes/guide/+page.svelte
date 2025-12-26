<script lang="ts">
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import {
    Shield,
    Lock,
    Users,
    Vote,
    Eye,
    EyeOff,
    FileText,
    CheckCircle,
    XCircle,
    Clock,
    Hash,
    Link2,
    Database,
    ChevronRight,
    ChevronDown,
    Fingerprint,
    Key,
    Globe,
    ArrowRight,
    Layers,
    AlertTriangle,
    Zap,
    BookOpen,
  } from "lucide-svelte";

  // Accordion state
  let openSection: string | null = "overview";

  function toggleSection(section: string) {
    openSection = openSection === section ? null : section;
  }

  // Interactive demo state
  let demoStep = 0;
  let demoHash = "";
  let isHashing = false;

  async function runHashDemo() {
    const sampleText = "Build 100 new schools in rural areas by 2027";
    isHashing = true;
    demoStep = 1;

    await new Promise((r) => setTimeout(r, 800));

    // Compute real SHA256
    const encoder = new TextEncoder();
    const data = encoder.encode(sampleText);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    demoHash =
      "0x" + hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

    demoStep = 2;
    isHashing = false;
  }

  function resetDemo() {
    demoStep = 0;
    demoHash = "";
  }
</script>

<svelte:head>
  <title>How It Works - PromiseThread</title>
  <meta
    name="description"
    content="Learn how PromiseThread uses blockchain and zero-knowledge proofs to create transparent political accountability while protecting citizen privacy."
  />
</svelte:head>

<Header />

<main class="min-h-screen bg-white">
  <!-- Hero Section -->
  <section
    class="relative py-20 overflow-hidden bg-gradient-to-br from-primary-700 to-primary-600"
  >
    <div
      class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent"
    ></div>
    <div class="max-w-6xl mx-auto px-4 relative">
      <div class="text-center mb-12">
        <div
          class="inline-flex items-center gap-2 bg-white/20 border border-white/30 rounded-full px-4 py-2 mb-6"
        >
          <BookOpen class="w-4 h-4 text-white" />
          <span class="text-white text-sm font-medium">Educational Guide</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold font-serif text-white mb-6">
          How PromiseThread Works
        </h1>
        <p class="text-xl text-white/90 max-w-3xl mx-auto">
          A transparent platform where promises are permanent, votes are
          anonymous, and trust is built through cryptography—not blind faith.
        </p>
      </div>

      <!-- Quick Navigation Cards -->
      <div class="grid md:grid-cols-4 gap-4 mt-12">
        <a
          href="#overview"
          class="group bg-white border border-gray-200 rounded-xl p-4 hover:border-primary-500 hover:shadow-md transition-all"
        >
          <Globe class="w-8 h-8 text-emerald-500 mb-3" />
          <h3 class="text-primary-700 font-semibold mb-1">Overview</h3>
          <p class="text-gray-600 text-sm">The big picture</p>
        </a>
        <a
          href="#blockchain"
          class="group bg-white border border-gray-200 rounded-xl p-4 hover:border-primary-500 hover:shadow-md transition-all"
        >
          <Link2 class="w-8 h-8 text-blue-500 mb-3" />
          <h3 class="text-primary-700 font-semibold mb-1">Data Integrity</h3>
          <p class="text-gray-600 text-sm">Permanent records</p>
        </a>
        <a
          href="#zkp"
          class="group bg-white border border-gray-200 rounded-xl p-4 hover:border-primary-500 hover:shadow-md transition-all"
        >
          <Fingerprint class="w-8 h-8 text-purple-500 mb-3" />
          <h3 class="text-primary-700 font-semibold mb-1">Privacy</h3>
          <p class="text-gray-600 text-sm">Anonymous feedback</p>
        </a>
        <a
          href="#voting"
          class="group bg-white border border-gray-200 rounded-xl p-4 hover:border-primary-500 hover:shadow-md transition-all"
        >
          <Vote class="w-8 h-8 text-amber-500 mb-3" />
          <h3 class="text-primary-700 font-semibold mb-1">Feedback</h3>
          <p class="text-gray-600 text-sm">Fair evaluation</p>
        </a>
      </div>
    </div>
  </section>

  <!-- Main Content -->
  <section class="py-16 bg-gray-50">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Section 1: Overview -->
      <div id="overview" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center"
          >
            <Globe class="w-5 h-5 text-emerald-500" />
          </div>
          <h2 class="text-2xl font-bold text-primary-700">The Big Picture</h2>
        </div>

        <div
          class="bg-white border border-gray-200 rounded-2xl p-6 mb-6 shadow-sm"
        >
          <h3 class="text-lg font-semibold text-primary-700 mb-4">
            The Problem We Solve
          </h3>
          <div class="space-y-4 text-gray-700">
            <p>
              Representatives make promises during elections. After winning, these
              promises often get
              <span class="text-amber-600 font-medium">changed</span>,
              <span class="text-amber-600 font-medium">forgotten</span>, or
              <span class="text-amber-600 font-medium">denied</span>. Citizens
              have no reliable way to track what was promised vs. what was
              delivered.
            </p>
            <p>
              Traditional tracking systems have a fatal flaw: whoever controls
              the database can
              <span class="text-red-600 font-medium">alter records</span>. Even
              with good intentions, there's no
              <em>proof</em> that records haven't been tampered with.
            </p>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
          <h3 class="text-lg font-semibold text-primary-700 mb-4">
            Our Solution
          </h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="flex gap-4">
              <div
                class="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center flex-shrink-0"
              >
                <Lock class="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <h4 class="text-primary-700 font-medium mb-1">
                  Immutable Promises
                </h4>
                <p class="text-gray-600 text-sm">
                  Once published, promises are cryptographically locked on
                  blockchain. No one—not even us—can change them.
                </p>
              </div>
            </div>
            <div class="flex gap-4">
              <div
                class="w-10 h-10 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-center flex-shrink-0"
              >
                <EyeOff class="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h4 class="text-primary-700 font-medium mb-1">
                  Anonymous Voting
                </h4>
                <p class="text-gray-600 text-sm">
                  Zero-knowledge proofs let citizens vote without revealing
                  their identity. Privacy is guaranteed cryptographically.
                </p>
              </div>
            </div>
            <div class="flex gap-4">
              <div
                class="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center flex-shrink-0"
              >
                <Eye class="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h4 class="text-primary-700 font-medium mb-1">
                  Transparent Results
                </h4>
                <p class="text-gray-600 text-sm">
                  Vote tallies are public. Anyone can verify the count. Results
                  can't be manipulated.
                </p>
              </div>
            </div>
            <div class="flex gap-4">
              <div
                class="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center flex-shrink-0"
              >
                <Clock class="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h4 class="text-primary-700 font-medium mb-1">Fair Timing</h4>
                <p class="text-gray-600 text-sm">
                  Grace periods prevent premature judgment. Voting only opens
                  after representatives have time to deliver.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 2: Blockchain Explained -->
      <div id="blockchain" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center"
          >
            <Link2 class="w-5 h-5 text-blue-600" />
          </div>
          <h2 class="text-2xl font-bold text-white">
            How Blockchain Makes Promises Permanent
          </h2>
        </div>

        <div
          class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 mb-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">What is a Hash?</h3>
          <p class="text-slate-300 mb-4">
            A hash is like a digital fingerprint. Feed any text into a hash
            function, and you get a unique fixed-length code. Even changing one
            letter produces a completely different hash.
          </p>

          <!-- Interactive Hash Demo -->
          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-slate-400">Interactive Demo</span>
              {#if demoStep > 0}
                <button
                  on:click={resetDemo}
                  class="text-xs text-slate-500 hover:text-slate-300"
                  >Reset</button
                >
              {/if}
            </div>

            {#if demoStep === 0}
              <div class="text-center py-4">
                <p class="text-slate-300 mb-4">
                  Click to see how a promise becomes a hash:
                </p>
                <button
                  on:click={runHashDemo}
                  class="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  Generate Hash
                </button>
              </div>
            {:else if demoStep === 1}
              <div class="text-center py-4">
                <div class="animate-pulse">
                  <Hash class="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                  <p class="text-slate-400">Computing SHA-256 hash...</p>
                </div>
              </div>
            {:else}
              <div class="space-y-4">
                <div>
                  <span class="text-xs text-slate-500 uppercase tracking-wide"
                    >Input (Promise Text)</span
                  >
                  <div
                    class="bg-slate-800 rounded-lg p-3 mt-1 text-slate-300 text-sm font-mono"
                  >
                    "Build 100 new schools in rural areas by 2027"
                  </div>
                </div>
                <div class="flex justify-center">
                  <ArrowRight class="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <span class="text-xs text-slate-500 uppercase tracking-wide"
                    >Output (SHA-256 Hash)</span
                  >
                  <div
                    class="bg-slate-800 rounded-lg p-3 mt-1 text-emerald-600 text-xs font-mono break-all"
                  >
                    {demoHash}
                  </div>
                </div>
                <p class="text-xs text-slate-500 text-center">
                  This exact hash will be produced by anyone, anywhere, using
                  the same text.
                </p>
              </div>
            {/if}
          </div>
        </div>

        <div
          class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 mb-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">
            What Goes On the Blockchain?
          </h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4
                class="text-emerald-600 font-medium mb-3 flex items-center gap-2"
              >
                <CheckCircle class="w-4 h-4" /> On-Chain (Permanent)
              </h4>
              <ul class="space-y-2 text-slate-300 text-sm">
                <li class="flex items-start gap-2">
                  <span class="text-emerald-600 mt-1">•</span>
                  Promise hash (fingerprint)
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-emerald-600 mt-1">•</span>
                  Representative's digital signature
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-emerald-600 mt-1">•</span>
                  Vote aggregates (Kept: 60%, Broken: 40%)
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-emerald-600 mt-1">•</span>
                  Timestamps and status changes
                </li>
              </ul>
            </div>
            <div>
              <h4
                class="text-blue-600 font-medium mb-3 flex items-center gap-2"
              >
                <Database class="w-4 h-4" /> Off-Chain (Database)
              </h4>
              <ul class="space-y-2 text-slate-300 text-sm">
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 mt-1">•</span>
                  Full promise text
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 mt-1">•</span>
                  Discussion threads
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 mt-1">•</span>
                  Evidence links
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 mt-1">•</span>
                  User interface data
                </li>
              </ul>
            </div>
          </div>
          <div class="mt-4 p-3 bg-slate-900/50 rounded-lg">
            <p class="text-slate-400 text-sm">
              <strong class="text-white">Why this split?</strong> Blockchain storage
              is expensive and slow. We store only what needs to be tamper-proof.
              The database handles everything else efficiently. The hash links them:
              if database text doesn't match the blockchain hash, we know it's been
              altered.
            </p>
          </div>
        </div>

        <!-- Blockchain Visualization -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            How Blocks Are Linked
          </h3>
          <div class="overflow-x-auto pb-4">
            <div class="flex gap-4 min-w-max">
              {#each [{ name: "Genesis", hash: "abc123...", prev: "000000..." }, { name: "Block 1", hash: "def456...", prev: "abc123..." }, { name: "Block 2", hash: "ghi789...", prev: "def456..." }, { name: "Block 3", hash: "jkl012...", prev: "ghi789..." }] as block, i}
                <div class="flex items-center gap-2">
                  <div
                    class="bg-slate-900 border border-slate-600 rounded-lg p-4 w-40"
                  >
                    <div class="text-emerald-600 font-medium text-sm mb-2">
                      {block.name}
                    </div>
                    <div class="text-xs space-y-1">
                      <div class="text-slate-500">Hash:</div>
                      <div class="text-slate-300 font-mono">{block.hash}</div>
                      <div class="text-slate-500 mt-2">Prev Hash:</div>
                      <div class="text-slate-300 font-mono">{block.prev}</div>
                    </div>
                  </div>
                  {#if i < 3}
                    <ChevronRight class="w-5 h-5 text-slate-600" />
                  {/if}
                </div>
              {/each}
            </div>
          </div>
          <p class="text-slate-400 text-sm mt-4">
            Each block contains the hash of the previous block. Changing any
            block would break this chain, making tampering immediately
            detectable.
          </p>
        </div>
      </div>

      <!-- Section 3: Zero-Knowledge Proofs -->
      <div id="zkp" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-purple-50 border border-purple-200 flex items-center justify-center"
          >
            <Fingerprint class="w-5 h-5 text-purple-600" />
          </div>
          <h2 class="text-2xl font-bold text-white">
            Zero-Knowledge Proofs: Privacy Magic
          </h2>
        </div>

        <div
          class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 mb-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">
            What is Zero-Knowledge?
          </h3>
          <p class="text-slate-300 mb-4">
            A zero-knowledge proof lets you prove something is true <em
              >without revealing the underlying information</em
            >.
          </p>

          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <h4 class="text-purple-600 font-medium mb-3">
              Real-World Analogy: The Cave
            </h4>
            <div class="space-y-3 text-slate-300 text-sm">
              <p>
                Imagine a circular cave with a locked door in the middle. You
                want to prove you have the key
                <em>without showing the key</em>.
              </p>
              <ol class="list-decimal list-inside space-y-2 pl-2">
                <li>
                  You enter the cave and go left or right (your choice, kept
                  secret)
                </li>
                <li>I stand outside and shout which side to exit from</li>
                <li>
                  If you have the key, you can always exit from the side I
                  choose
                </li>
                <li>
                  If you don't have the key, you have only 50% chance of
                  guessing right
                </li>
              </ol>
              <p class="text-purple-600">
                After 20 rounds with 100% success, I'm mathematically convinced
                you have the key—but I never saw it.
              </p>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            How We Use ZKP for Voting
          </h3>

          <div class="relative">
            <!-- Timeline -->
            <div
              class="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-700"
            ></div>

            <div class="space-y-8">
              <!-- Step 1 -->
              <div class="relative flex gap-4">
                <div
                  class="w-12 h-12 rounded-full bg-purple-50 border border-purple-200 flex items-center justify-center z-10 border-2 border-slate-800"
                >
                  <span class="text-purple-600 font-bold">1</span>
                </div>
                <div
                  class="flex-1 bg-slate-900/50 rounded-xl p-4 border border-slate-600"
                >
                  <h4 class="text-white font-medium mb-2">
                    Prove You're a Citizen
                  </h4>
                  <p class="text-slate-400 text-sm">
                    You prove you're in the voter registry WITHOUT revealing
                    which voter you are. The system learns "this is a valid
                    citizen" but not "this is John Doe."
                  </p>
                </div>
              </div>

              <!-- Step 2 -->
              <div class="relative flex gap-4">
                <div
                  class="w-12 h-12 rounded-full bg-purple-50 border border-purple-200 flex items-center justify-center z-10 border-2 border-slate-800"
                >
                  <span class="text-purple-600 font-bold">2</span>
                </div>
                <div
                  class="flex-1 bg-slate-900/50 rounded-xl p-4 border border-slate-600"
                >
                  <h4 class="text-white font-medium mb-2">
                    Get Anonymous Credential
                  </h4>
                  <p class="text-slate-400 text-sm">
                    You receive a unique "nullifier" — a random-looking
                    identifier that can't be traced back to you. This is your
                    voting ticket.
                  </p>
                </div>
              </div>

              <!-- Step 3 -->
              <div class="relative flex gap-4">
                <div
                  class="w-12 h-12 rounded-full bg-purple-50 border border-purple-200 flex items-center justify-center z-10 border-2 border-slate-800"
                >
                  <span class="text-purple-600 font-bold">3</span>
                </div>
                <div
                  class="flex-1 bg-slate-900/50 rounded-xl p-4 border border-slate-600"
                >
                  <h4 class="text-white font-medium mb-2">Vote Anonymously</h4>
                  <p class="text-slate-400 text-sm">
                    Your vote is linked to your nullifier, not your identity.
                    The system prevents double voting by checking if that
                    nullifier already voted—but never knows who you are.
                  </p>
                </div>
              </div>

              <!-- Step 4 -->
              <div class="relative flex gap-4">
                <div
                  class="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center z-10 border-2 border-slate-800"
                >
                  <span class="text-emerald-600 font-bold">4</span>
                </div>
                <div
                  class="flex-1 bg-slate-900/50 rounded-xl p-4 border border-slate-600"
                >
                  <h4 class="text-white font-medium mb-2">
                    Results are Aggregated
                  </h4>
                  <p class="text-slate-400 text-sm">
                    Only vote TOTALS go on blockchain. Individual votes stay in
                    the database, linked to anonymous nullifiers. No one can
                    reconstruct who voted for what.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 4: Voting Process -->
      <div id="voting" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-amber-50 border border-amber-200 flex items-center justify-center"
          >
            <Vote class="w-5 h-5 text-amber-600" />
          </div>
          <h2 class="text-2xl font-bold text-white">The Voting Process</h2>
        </div>

        <div
          class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 mb-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">
            Grace Periods: Fair Evaluation
          </h3>
          <p class="text-slate-300 mb-4">
            We don't let voting open immediately. Representatives need time to work
            on their promises.
          </p>

          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <div class="flex items-center gap-4 mb-4">
              <div class="flex-1">
                <div class="flex justify-between text-xs text-slate-500 mb-1">
                  <span>Promise Made</span>
                  <span>Voting Opens</span>
                  <span>Deadline</span>
                </div>
                <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-amber-500 to-emerald-500 w-1/3"
                  ></div>
                </div>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-4 text-center">
              <div>
                <Clock class="w-5 h-5 text-amber-600 mx-auto mb-1" />
                <span class="text-xs text-slate-400">Day 0</span>
              </div>
              <div>
                <Vote class="w-5 h-5 text-emerald-600 mx-auto mb-1" />
                <span class="text-xs text-slate-400">After Grace Period</span>
              </div>
              <div>
                <CheckCircle class="w-5 h-5 text-blue-600 mx-auto mb-1" />
                <span class="text-xs text-slate-400">Final Status</span>
              </div>
            </div>
          </div>
        </div>

        <div
          class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 mb-6"
        >
          <h3 class="text-lg font-semibold text-white mb-4">Vote Types</h3>
          <div class="grid md:grid-cols-2 gap-4">
            <div
              class="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4"
            >
              <div class="flex items-center gap-3 mb-2">
                <CheckCircle class="w-6 h-6 text-emerald-600" />
                <span class="text-white font-medium">Promise Kept</span>
              </div>
              <p class="text-slate-400 text-sm">
                The representative has fulfilled this promise as stated, or made
                significant verifiable progress.
              </p>
            </div>
            <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <div class="flex items-center gap-3 mb-2">
                <XCircle class="w-6 h-6 text-red-400" />
                <span class="text-white font-medium">Promise Broken</span>
              </div>
              <p class="text-slate-400 text-sm">
                The promise was not kept, abandoned, or the opposite action was
                taken.
              </p>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            Consensus Threshold
          </h3>
          <p class="text-slate-300 mb-4">
            A promise's final status is determined by community consensus:
          </p>
          <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-400">Threshold for "Kept"</span>
              <span class="text-emerald-600 font-bold">≥ 60%</span>
            </div>
            <div class="h-3 bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-500 w-3/5"></div>
            </div>
            <p class="text-xs text-slate-500 mt-2">
              If 60% or more vote "Kept", the promise is marked as fulfilled.
              Otherwise, it's marked as broken.
            </p>
          </div>
        </div>
      </div>

      <!-- Section 5: Digital Signatures -->
      <div id="signatures" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-rose-500/20 flex items-center justify-center"
          >
            <Key class="w-5 h-5 text-rose-400" />
          </div>
          <h2 class="text-2xl font-bold text-white">
            Digital Signatures: Proof of Authorship
          </h2>
        </div>

        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            How Representatives Sign Promises
          </h3>

          <div class="space-y-4">
            <div class="flex gap-4 items-start">
              <div
                class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center flex-shrink-0"
              >
                <span class="text-rose-400 font-bold text-sm">1</span>
              </div>
              <div>
                <h4 class="text-white font-medium">
                  Representative gets a unique wallet
                </h4>
                <p class="text-slate-400 text-sm">
                  A cryptographic key pair is generated. The private key is
                  given ONLY to the representative.
                </p>
              </div>
            </div>

            <div class="flex gap-4 items-start">
              <div
                class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center flex-shrink-0"
              >
                <span class="text-rose-400 font-bold text-sm">2</span>
              </div>
              <div>
                <h4 class="text-white font-medium">Promise is hashed</h4>
                <p class="text-slate-400 text-sm">
                  The promise text becomes a unique fingerprint (hash).
                </p>
              </div>
            </div>

            <div class="flex gap-4 items-start">
              <div
                class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center flex-shrink-0"
              >
                <span class="text-rose-400 font-bold text-sm">3</span>
              </div>
              <div>
                <h4 class="text-white font-medium">
                  Representative signs the hash
                </h4>
                <p class="text-slate-400 text-sm">
                  Using their private key (in their browser), they create a
                  digital signature.
                </p>
              </div>
            </div>

            <div class="flex gap-4 items-start">
              <div
                class="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0"
              >
                <span class="text-emerald-600 font-bold text-sm">4</span>
              </div>
              <div>
                <h4 class="text-white font-medium">Anyone can verify</h4>
                <p class="text-slate-400 text-sm">
                  The public key verifies the signature. Proof: only the
                  representative could have signed this promise.
                </p>
              </div>
            </div>
          </div>

          <div
            class="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl"
          >
            <div class="flex gap-3">
              <AlertTriangle
                class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5"
              />
              <div>
                <h4 class="text-amber-600 font-medium">Security Note</h4>
                <p class="text-slate-300 text-sm">
                  The private key NEVER touches our servers. Signing happens
                  entirely in the representative's browser. Even if our database is
                  compromised, no one can forge signatures.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 6: Verification -->
      <div id="verification" class="mb-16 scroll-mt-24">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center"
          >
            <Shield class="w-5 h-5 text-cyan-400" />
          </div>
          <h2 class="text-2xl font-bold text-white">
            Independent Verification
          </h2>
        </div>

        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            Don't Trust Us—Verify!
          </h3>
          <p class="text-slate-300 mb-4">
            Our system is designed so you don't need to trust us. Here's how to
            verify everything independently:
          </p>

          <div class="space-y-4">
            <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
              <h4 class="text-cyan-400 font-medium mb-2">
                1. Verify Promise Text
              </h4>
              <p class="text-slate-400 text-sm mb-2">
                Copy the promise text, compute SHA-256 hash locally, compare
                with blockchain hash.
              </p>
              <code
                class="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300"
              >
                echo -n "promise text" | shasum -a 256
              </code>
            </div>

            <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
              <h4 class="text-cyan-400 font-medium mb-2">
                2. Verify Blockchain Data
              </h4>
              <p class="text-slate-400 text-sm mb-2">
                Query the smart contract directly using any blockchain explorer
                or Web3 library.
              </p>
              <code
                class="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300"
              >
                Contract: 0xe7f1...0512 on Chain ID 31337
              </code>
            </div>

            <div class="bg-slate-900/50 rounded-xl p-4 border border-slate-600">
              <h4 class="text-cyan-400 font-medium mb-2">
                3. Verify Signatures
              </h4>
              <p class="text-slate-400 text-sm">
                Use any ECDSA verification tool to confirm the representative's
                address signed the hash.
              </p>
            </div>
          </div>

          <div class="mt-6">
            <a
              href="/verify"
              class="inline-flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <Shield class="w-5 h-5" />
              Go to Verification Tool
            </a>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div
        class="bg-gradient-to-r from-emerald-500/20 to-blue-500/20 border border-emerald-500/30 rounded-2xl p-8 text-center"
      >
        <h2 class="text-2xl font-bold text-white mb-4">
          Ready to Hold Representatives Accountable?
        </h2>
        <p class="text-slate-300 mb-6 max-w-xl mx-auto">
          Browse election promises, verify their authenticity, and cast your
          anonymous vote to help determine if representatives keep their word.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <a
            href="/manifestos"
            class="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2"
          >
            <FileText class="w-5 h-5" />
            View Promises
          </a>
          <a
            href="/auth"
            class="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2"
          >
            <Fingerprint class="w-5 h-5" />
            Get Verified
          </a>
        </div>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
  :global(html) {
    scroll-behavior: smooth;
  }
</style>
