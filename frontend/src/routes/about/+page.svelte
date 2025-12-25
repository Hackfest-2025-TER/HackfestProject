<script lang="ts">
  import {
    Shield,
    Target,
    Users,
    Lock,
    Eye,
    Code,
    Heart,
    Github,
    Twitter,
    Globe,
    Mail,
    ExternalLink,
  } from "lucide-svelte";
</script>

<svelte:head>
  <title>About - PromiseThread</title>
  <meta
    name="description"
    content="Learn about PromiseThread's mission to create transparent political accountability while protecting citizen privacy."
  />
</svelte:head>

<main class="min-h-screen bg-gray-50">
  <!-- Hero -->
  <section class="py-20 bg-gradient-to-br from-primary-700 to-primary-800">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div
        class="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-6"
      >
        <Shield class="w-10 h-10 text-white" />
      </div>
      <h1 class="text-4xl md:text-5xl font-bold font-serif text-white mb-6">
        About PromiseThread
      </h1>
      <p class="text-xl text-white/90 max-w-2xl mx-auto">
        A platform bringing transparency to political promises while protecting
        citizen privacy.
      </p>
    </div>
  </section>

  <!-- Mission -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-12 h-12 rounded-xl bg-success-50 flex items-center justify-center"
          >
            <Target class="w-6 h-6 text-success-600" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900">Our Mission</h2>
        </div>
        <div class="space-y-4 text-gray-600 text-lg leading-relaxed">
          <p>
            Democracy works best when citizens can hold their representatives
            accountable. But accountability requires memory—and in the age of
            information overload, promises are easily forgotten, modified, or
            denied.
          </p>
          <p>
            <strong class="text-gray-900"
              >PromiseThread exists to solve this problem.</strong
            >
            We create a permanent record of political promises that no one can alter
            after the fact. We enable citizens to evaluate these promises anonymously,
            without fear of reprisal.
          </p>
          <p>
            Our goal is simple: <span class="text-primary-700 font-semibold"
              >transparent promises, private citizens, trustworthy results.</span
            >
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Core Values -->
  <section class="py-16 bg-white">
    <div class="max-w-4xl mx-auto px-4">
      <h2 class="text-2xl font-bold text-gray-900 text-center mb-12">
        Our Core Values
      </h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <div
            class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center mb-4"
          >
            <Eye class="w-6 h-6 text-blue-600" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Transparency</h3>
          <p class="text-gray-600">
            All promises are public and permanent. Vote tallies are visible to
            everyone. Our code is open source. We have nothing to hide.
          </p>
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <div
            class="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center mb-4"
          >
            <Lock class="w-6 h-6 text-purple-600" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Privacy</h3>
          <p class="text-gray-600">
            Citizens can participate without revealing their identity. Advanced
            cryptography ensures your vote counts without exposing who you are.
          </p>
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <div
            class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center mb-4"
          >
            <Shield class="w-6 h-6 text-amber-600" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Security</h3>
          <p class="text-gray-600">
            Records are tamper-proof. Cryptographic signatures prevent forgery.
            Even if our servers are compromised, the truth remains verifiable.
          </p>
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <div
            class="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center mb-4"
          >
            <Users class="w-6 h-6 text-rose-600" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Non-Partisan</h3>
          <p class="text-gray-600">
            We don't take sides. Every politician's promises are treated
            equally. The platform is a neutral ground for accountability.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- How We're Different -->
  <section class="py-16">
    <div class="max-w-4xl mx-auto px-4">
      <div
        class="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-100 rounded-2xl p-8"
      >
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">
          What Makes Us Different
        </h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="text-4xl font-bold text-primary-700 mb-2">0</div>
            <div class="text-gray-700 font-medium">Personal data stored</div>
            <p class="text-gray-500 text-sm mt-2">
              We don't know who you are. By design.
            </p>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-blue-600 mb-2">∞</div>
            <div class="text-gray-700 font-medium">Data retention</div>
            <p class="text-gray-500 text-sm mt-2">Records are permanent.</p>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-purple-600 mb-2">100%</div>
            <div class="text-gray-700 font-medium">Verifiable</div>
            <p class="text-gray-500 text-sm mt-2">
              Don't trust—verify everything yourself.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Technology -->
  <section class="py-16 bg-white">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center gap-3 mb-8">
        <div
          class="w-12 h-12 rounded-xl bg-cyan-50 flex items-center justify-center"
        >
          <Code class="w-6 h-6 text-cyan-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Our Technology Stack</h2>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <h3 class="text-gray-900 font-medium mb-2">Frontend</h3>
          <p class="text-gray-600 text-sm">
            SvelteKit, TypeScript, TailwindCSS
          </p>
        </div>
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <h3 class="text-gray-900 font-medium mb-2">Backend</h3>
          <p class="text-gray-600 text-sm">FastAPI, Python, PostgreSQL</p>
        </div>
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <h3 class="text-gray-900 font-medium mb-2">Data Integrity</h3>
          <p class="text-gray-600 text-sm">
            Cryptographic hashing, Digital signatures
          </p>
        </div>
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <h3 class="text-gray-900 font-medium mb-2">Privacy</h3>
          <p class="text-gray-600 text-sm">Advanced cryptographic proofs</p>
        </div>
      </div>

      <div class="mt-6 text-center">
        <a
          href="https://github.com/promisethread"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-2 text-gray-500 hover:text-primary-700 transition-colors"
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
          <Heart class="w-6 h-6 text-rose-500" />
          <h2 class="text-2xl font-bold text-gray-900">
            Built with ❤️ for Democracy
          </h2>
        </div>
        <p class="text-gray-600">
          PromiseThread is a hackathon project demonstrating how technology can
          enhance democratic accountability.
        </p>
      </div>

      <div
        class="bg-white border border-gray-200 rounded-2xl p-8 text-center shadow-sm"
      >
        <p class="text-gray-600 mb-6">
          This platform was created during a hackfest to explore how we can
          apply modern technology to real-world democratic challenges. Our goal
          is to show what's possible when privacy meets transparency.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <a
            href="/guide"
            class="bg-primary-700 hover:bg-primary-800 text-white px-6 py-3 rounded-lg transition-colors"
          >
            Learn How It Works
          </a>
          <a
            href="/faq"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-3 rounded-lg transition-colors"
          >
            Read FAQ
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Contact -->
  <section class="py-16 bg-white">
    <div class="max-w-4xl mx-auto px-4">
      <div
        class="bg-gray-50 border border-gray-200 rounded-2xl p-8 text-center"
      >
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Get in Touch</h2>
        <p class="text-gray-600 mb-6">
          Questions, feedback, or want to contribute? We'd love to hear from
          you.
        </p>
        <div class="flex flex-wrap justify-center gap-6">
          <a
            href="/feedback"
            class="flex items-center gap-2 text-gray-600 hover:text-primary-700 transition-colors"
          >
            <Mail class="w-5 h-5" />
            Send Feedback
          </a>
          <a
            href="https://github.com/promisethread"
            target="_blank"
            rel="noopener"
            class="flex items-center gap-2 text-gray-600 hover:text-primary-700 transition-colors"
          >
            <Github class="w-5 h-5" />
            GitHub
          </a>
          <a
            href="https://twitter.com/promisethread"
            target="_blank"
            rel="noopener"
            class="flex items-center gap-2 text-gray-600 hover:text-primary-700 transition-colors"
          >
            <Twitter class="w-5 h-5" />
            Twitter
          </a>
        </div>
      </div>
    </div>
  </section>
</main>
