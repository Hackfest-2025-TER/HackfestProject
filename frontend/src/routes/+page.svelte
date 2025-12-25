<script lang="ts">
  import {
    FileText,
    Lock,
    Users,
    Shield,
    ArrowRight,
    CheckCircle,
    Activity,
    Globe,
    Database,
    Zap,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";

  let mounted = false;
  let networkStats: any = null;

  onMount(async () => {
    mounted = true;
    await loadNetworkStats();
  });

  async function loadNetworkStats() {
    try {
      const response = await fetch("http://localhost:8000/api/network/stats");
      if (response.ok) {
        networkStats = await response.json();
      }
    } catch (error) {
      console.error("Failed to load network stats:", error);
    }
  }
</script>

<svelte:head>
  <title>PromiseThread - The Future of Political Accountability</title>
</svelte:head>

<main class="min-h-screen bg-white overflow-hidden">
  <!-- Navigation -->
  <nav
    class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200"
  >
    <div class="container">
      <div class="flex justify-between items-center h-20">
        <a href="/" class="flex items-center space-x-3 group">
          <div class="bg-primary-700 p-2 rounded-lg text-white">
            <Shield class="w-6 h-6 fill-current" />
          </div>
          <span class="text-xl font-serif font-bold text-gray-900"
            >PromiseThread</span
          >
        </a>

        <div class="hidden md:flex items-center space-x-6">
          <a
            href="/manifestos"
            class="text-gray-600 hover:text-primary-700 font-medium transition-colors"
            >Promises</a
          >
          <a
            href="/representatives"
            class="text-gray-600 hover:text-primary-700 font-medium transition-colors"
            >Representatives</a
          >
          <a
            href="/audit-trail"
            class="text-gray-600 hover:text-primary-700 font-medium transition-colors"
            >Audit Trail</a
          >
          <a
            href="/auth"
            class="ml-4 px-5 py-2.5 bg-primary-700 hover:bg-primary-800 text-white font-semibold rounded-xl shadow-lg shadow-primary-700/20 transition-all hover:shadow-xl"
          >
            Verify Citizen
          </a>
        </div>
      </div>
    </div>
  </nav>

  <!-- Hero Section -->
  <section class="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute inset-0 z-0 overflow-hidden">
      <div
        class="absolute -top-24 -right-24 w-96 h-96 bg-primary-100 rounded-full blur-3xl opacity-50"
      ></div>
      <div
        class="absolute top-1/2 -left-24 w-72 h-72 bg-blue-100 rounded-full blur-3xl opacity-50"
      ></div>
    </div>

    <div class="container relative z-10">
      <div class="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
        <!-- Text Content -->
        <div class="max-w-2xl">
          <div
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-sm font-semibold mb-6"
          >
            <span class="relative flex h-2 w-2">
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"
              ></span>
            </span>
            Live Election Cycle 2025
          </div>

          <h1
            class="text-6xl lg:text-8xl font-black font-serif text-gray-900 leading-none mb-8 tracking-tight"
          >
            Democracy, <br />
            <span class="text-primary-700">Upgraded.</span>
          </h1>

          <p class="text-xl text-gray-600 mb-8 leading-relaxed">
            The first citizen-led platform that turns political promises into
            trackable, verified records. Hold leaders accountable without
            compromising your privacy.
          </p>

          <div class="flex flex-col sm:flex-row gap-4 mb-12">
            <a
              href="/manifestos"
              class="px-8 py-4 bg-primary-700 hover:bg-primary-800 text-white text-lg font-semibold rounded-xl shadow-lg shadow-primary-700/20 transition-all hover:shadow-xl inline-flex items-center gap-2"
            >
              Browse Promises
              <ArrowRight size={20} />
            </a>
            <a
              href="/auth"
              class="px-8 py-4 bg-white border-2 border-primary-200 text-primary-700 text-lg font-semibold rounded-xl hover:bg-primary-50 hover:border-primary-300 transition-all inline-flex items-center gap-2"
            >
              <Shield size={20} />
              Get Verified
            </a>
          </div>

          <div class="flex flex-wrap gap-8 py-8 border-t border-gray-100">
            <div class="flex items-center gap-2 text-gray-500 font-medium">
              <Shield size={18} class="text-primary-600" />
              <span>Privacy Preserved</span>
            </div>
            <div class="flex items-center gap-2 text-gray-500 font-medium">
              <Database size={18} class="text-primary-600" />
              <span>Permanent Record</span>
            </div>
            <div class="flex items-center gap-2 text-gray-500 font-medium">
              <Users size={18} class="text-primary-600" />
              <span>Community Verified</span>
            </div>
          </div>
        </div>

        <!-- Hero Visual -->
        <div class="relative lg:h-[600px] flex items-center justify-center">
          <div class="relative w-full max-w-md aspect-square">
            <!-- Central Card -->
            <div
              class="absolute inset-0 bg-white rounded-2xl shadow-2xl border border-gray-100 p-6 flex flex-col z-20 transform transition-transform hover:-translate-y-2 duration-500"
            >
              <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600"
                  >
                    <FileText size={20} />
                  </div>
                  <div>
                    <div class="h-2 w-24 bg-gray-200 rounded mb-1"></div>
                    <div class="h-2 w-16 bg-gray-100 rounded"></div>
                  </div>
                </div>
                <div
                  class="px-2 py-1 bg-success-50 text-success-700 text-xs font-bold rounded-full flex items-center gap-1"
                >
                  <CheckCircle size={12} /> Verified
                </div>
              </div>

              <div class="space-y-3 mb-6">
                <div class="h-2 w-full bg-gray-100 rounded"></div>
                <div class="h-2 w-full bg-gray-100 rounded"></div>
                <div class="h-2 w-3/4 bg-gray-100 rounded"></div>
              </div>

              <div
                class="mt-auto bg-gray-50 rounded-xl p-4 border border-gray-100"
              >
                <div class="flex justify-between items-end mb-2">
                  <span class="text-xs font-semibold text-gray-500"
                    >COMMUNITY CONSENSUS</span
                  >
                  <span class="text-lg font-bold text-primary-700">72%</span>
                </div>
                <div
                  class="w-full bg-gray-200 rounded-full h-2 overflow-hidden"
                >
                  <div
                    class="bg-primary-600 h-2 rounded-full"
                    style="width: 72%"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Floating Elements -->
            <div
              class="absolute -top-12 -right-12 bg-white p-4 rounded-xl shadow-xl border border-gray-100 z-10 animate-bounce"
              style="animation-duration: 3s;"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
                  <Users size={20} />
                </div>
                <div>
                  <p class="text-xs text-gray-500 font-semibold uppercase">
                    Votes Cast
                  </p>
                  <p class="text-xl font-bold text-gray-900">
                    {networkStats
                      ? networkStats.total_votes >= 1000
                        ? (networkStats.total_votes / 1000).toFixed(1) + "k"
                        : networkStats.total_votes
                      : "1,240"}
                  </p>
                </div>
              </div>
            </div>

            <div
              class="absolute -bottom-8 -left-8 bg-white p-4 rounded-xl shadow-xl border border-gray-100 z-30 animate-bounce"
              style="animation-duration: 4s;"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-success-100 text-success-600 rounded-lg">
                  <Shield size={20} />
                </div>
                <div>
                  <p class="text-xs text-gray-500 font-semibold uppercase">
                    Integrity Score
                  </p>
                  <p class="text-xl font-bold text-gray-900">
                    {networkStats
                      ? networkStats.integrity_score.toFixed(1) + "%"
                      : "100%"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Stats Strip -->
  <section class="py-10 bg-primary-700 text-white border-y border-primary-800">
    <div class="container">
      <div
        class="grid grid-cols-1 md:grid-cols-3 gap-8 divide-y md:divide-y-0 md:divide-x divide-primary-600/50"
      >
        <div class="text-center py-4">
          <span class="block text-4xl font-bold mb-1"
            >{networkStats
              ? (networkStats.total_voters || 0).toLocaleString()
              : "..."}</span
          >
          <span
            class="text-primary-200 text-sm font-medium uppercase tracking-wider"
            >Verified Citizens</span
          >
        </div>
        <div class="text-center py-4">
          <span class="block text-4xl font-bold mb-1"
            >{networkStats
              ? (networkStats.total_manifestos || 0).toLocaleString()
              : "..."}</span
          >
          <span
            class="text-primary-200 text-sm font-medium uppercase tracking-wider"
            >Promises Tracked</span
          >
        </div>
        <div class="text-center py-4">
          <span class="block text-4xl font-bold mb-1"
            >{networkStats
              ? (networkStats.total_votes || 0).toLocaleString()
              : "..."}</span
          >
          <span
            class="text-primary-200 text-sm font-medium uppercase tracking-wider"
            >Total Votes</span
          >
        </div>
      </div>
    </div>
  </section>

  <!-- Features Grid -->
  <section class="py-24 bg-gray-50">
    <div class="container">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2
          class="text-3xl md:text-5xl font-bold font-serif text-gray-900 mb-6"
        >
          Powerful Accountability Tools
        </h2>
        <p class="text-xl text-gray-600 leading-relaxed">
          Built for the modern voter. Simple enough for anyone, powerful enough
          for truth.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 grid-rows-[auto_auto]">
        <!-- Large Feature -->
        <div
          class="md:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-10 hover:shadow-md transition-shadow relative overflow-hidden group"
        >
          <div class="relative z-10">
            <div
              class="w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center text-primary-600 mb-6 group-hover:bg-primary-100 transition-colors"
            >
              <Database size={32} />
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-4">
              Immutable Promise Ledger
            </h3>
            <p class="text-lg text-gray-600 leading-relaxed max-w-xl">
              Every promise is recorded permanently. Representatives cannot
              delete or silently edit their commitments once they are live.
              History is preserved forever.
            </p>
          </div>
          <div class="absolute right-0 bottom-0 p-8 opacity-50 md:opacity-100">
            <div
              class="bg-gray-50 rounded-xl p-4 border border-gray-200 font-mono text-xs text-gray-500 w-64 shadow-inner"
            >
              <div class="flex justify-between mb-2">
                <span>Ref ID:</span>
                <span class="text-gray-900">8821...9a2</span>
              </div>
              <div class="flex justify-between mb-2">
                <span>Prev:</span> <span class="text-gray-900">3c14...b4e</span>
              </div>
              <div class="flex justify-between">
                <span>Status:</span>
                <span class="text-success-600 font-bold">Verified</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Medium Feature -->
        <div
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-10 hover:shadow-md transition-shadow group flex flex-col"
        >
          <div
            class="w-16 h-16 bg-success-50 rounded-2xl flex items-center justify-center text-success-600 mb-6 group-hover:bg-success-100 transition-colors"
          >
            <Shield size={32} />
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-4">Privacy First</h3>
          <p class="text-lg text-gray-600 leading-relaxed mb-8 flex-1">
            Prove you are a citizen without revealing who you are. Your vote is
            detailed, but your identity is yours.
          </p>
          <div class="mt-auto flex justify-center">
            <Shield size={80} class="text-success-100" />
          </div>
        </div>

        <!-- Small Features -->
        <div
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 hover:shadow-md transition-shadow group"
        >
          <div
            class="w-14 h-14 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600 mb-4 group-hover:bg-amber-100 transition-colors"
          >
            <Activity size={28} />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">
            Real-time Updates
          </h3>
          <p class="text-gray-600">
            Watch promise status updates live as they happen in the activity
            log.
          </p>
        </div>

        <div
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 hover:shadow-md transition-shadow group"
        >
          <div
            class="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600 mb-4 group-hover:bg-blue-100 transition-colors"
          >
            <Globe size={28} />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Open Access</h3>
          <p class="text-gray-600">
            All data is accessible via API for independent checking by anyone.
          </p>
        </div>

        <div
          class="bg-primary-700 rounded-2xl p-8 text-white flex flex-col justify-center items-start text-left"
        >
          <h3 class="text-2xl font-bold mb-4">Ready to start?</h3>
          <a
            href="/citizen"
            class="btn bg-white text-primary-700 hover:bg-gray-100 w-full justify-center text-lg"
            >Join Now</a
          >
        </div>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="py-24 bg-white">
    <div class="container">
      <div
        class="bg-primary-600 rounded-3xl p-8 md:p-16 text-center relative overflow-hidden"
      >
        <div class="relative z-10 max-w-2xl mx-auto">
          <h2 class="text-3xl md:text-5xl font-bold font-serif text-white mb-6">
            Ready to shape the future?
          </h2>
          <p class="text-primary-100 text-xl mb-10">
            Join thousands of citizens ensuring promises are more than just
            words.
          </p>
          <a
            href="/citizen"
            class="inline-flex items-center justify-center px-8 py-4 bg-white text-primary-700 font-bold rounded-xl hover:bg-gray-50 transition-transform hover:scale-105 shadow-lg text-lg"
          >
            <span>Go to Citizen Portal</span>
            <ArrowRight class="ml-2 w-6 h-6" />
          </a>
        </div>

        <!-- Decorative Background -->
        <div class="absolute top-0 right-0 -mt-10 -mr-10 opacity-10 text-white">
          <Zap size={200} />
        </div>
        <div
          class="absolute bottom-0 left-0 -mb-10 -ml-10 opacity-10 text-white"
        >
          <Activity size={200} />
        </div>
      </div>
    </div>
  </section>
</main>
