<script lang="ts">
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import {
    Shield,
    Eye,
    EyeOff,
    Lock,
    Database,
    Server,
    CheckCircle,
    XCircle,
    AlertTriangle,
    Fingerprint,
  } from "lucide-svelte";
</script>

<svelte:head>
  <title>Privacy Policy - WaachaPatra</title>
  <meta
    name="description"
    content="Learn how WaachaPatra protects your privacy using advanced cryptographic techniques."
  />
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50">
  <!-- Hero -->
  <section class="py-16 bg-gradient-to-br from-primary-700 to-primary-800">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <div
        class="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-6"
      >
        <Shield class="w-8 h-8 text-white" />
      </div>
      <h1 class="text-4xl font-bold font-serif text-white mb-4">
        Privacy Policy
      </h1>
      <p class="text-xl text-white/90">
        Your privacy isn't just a policy—it's built into our architecture.
      </p>
    </div>
  </section>

  <!-- TL;DR -->
  <section class="py-12">
    <div class="max-w-4xl mx-auto px-4">
      <div class="bg-success-50 border border-success-200 rounded-2xl p-6">
        <h2 class="text-lg font-semibold text-success-700 mb-4">
          TL;DR - The Short Version
        </h2>
        <ul class="space-y-2 text-gray-700">
          <li class="flex items-start gap-2">
            <CheckCircle
              class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
            />
            <span
              >We store <strong>zero personal information</strong> about citizens
              who provide feedback</span
            >
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle
              class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
            />
            <span
              >Your identity is protected by <strong
                >advanced cryptography</strong
              ></span
            >
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle
              class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
            />
            <span
              >We <strong>cannot see</strong> how you voted, even if we wanted to</span
            >
          </li>
          <li class="flex items-start gap-2">
            <CheckCircle
              class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
            />
            <span
              >No tracking, no cookies for analytics, no third-party data
              sharing</span
            >
          </li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Main Content -->
  <section class="pb-20">
    <div class="max-w-4xl mx-auto px-4 space-y-8">
      <!-- What We Collect -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center"
          >
            <Database class="w-5 h-5 text-blue-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">What We Store</h2>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h3
              class="text-success-700 font-medium mb-3 flex items-center gap-2"
            >
              <CheckCircle class="w-4 h-4" /> We Store
            </h3>
            <ul class="space-y-2 text-gray-600 text-sm">
              <li>• Anonymous identifiers (random, not traceable)</li>
              <li>• Secure credential hashes (cannot be reversed)</li>
              <li>• Feedback records linked to anonymous IDs</li>
              <li>• Public comments (anonymous)</li>
              <li>• Promise text and digital signatures</li>
            </ul>
          </div>
          <div>
            <h3 class="text-error-600 font-medium mb-3 flex items-center gap-2">
              <XCircle class="w-4 h-4" /> We Don't Store
            </h3>
            <ul class="space-y-2 text-gray-600 text-sm">
              <li>• Your name or real identity</li>
              <li>• Your voter ID or registration number</li>
              <li>• Your location or IP address</li>
              <li>• Any link between you and your feedback</li>
              <li>• Browser fingerprints or device info</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- How Privacy Works -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center"
          >
            <Fingerprint class="w-5 h-5 text-purple-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">
            How Your Privacy is Protected
          </h2>
        </div>

        <p class="text-gray-600 mb-4">
          When you verify as a citizen, we use advanced cryptographic
          techniques. This means:
        </p>

        <div class="bg-gray-50 rounded-xl p-4 border border-gray-200 mb-4">
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <div
                class="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5"
              >
                <span class="text-primary-700 text-xs font-bold">1</span>
              </div>
              <p class="text-gray-700 text-sm">
                You prove you're a registered citizen <strong
                  >without revealing which citizen you are</strong
                >
              </p>
            </div>
            <div class="flex items-start gap-3">
              <div
                class="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5"
              >
                <span class="text-primary-700 text-xs font-bold">2</span>
              </div>
              <p class="text-gray-700 text-sm">
                We receive a cryptographic proof that verifies eligibility, but
                contains <strong>no identifying information</strong>
              </p>
            </div>
            <div class="flex items-start gap-3">
              <div
                class="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5"
              >
                <span class="text-primary-700 text-xs font-bold">3</span>
              </div>
              <p class="text-gray-700 text-sm">
                You get an anonymous credential that <strong
                  >cannot be traced back</strong
                > to your real identity
              </p>
            </div>
          </div>
        </div>

        <p class="text-gray-500 text-sm">
          This is mathematically guaranteed—not a policy we might change, but a
          fundamental property of the technology.
        </p>
      </div>

      <!-- Visibility -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center"
          >
            <Eye class="w-5 h-5 text-amber-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">
            What's Public vs. Private
          </h2>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-amber-50 rounded-xl p-4 border border-amber-100">
            <div class="flex items-center gap-2 mb-3">
              <Eye class="w-5 h-5 text-amber-600" />
              <h3 class="text-gray-900 font-medium">Public (Everyone Sees)</h3>
            </div>
            <ul class="space-y-1 text-gray-600 text-sm">
              <li>• Promise text and commitments</li>
              <li>• Representative signatures</li>
              <li>• Feedback aggregates (totals)</li>
              <li>• Discussion comments</li>
              <li>• Verification records</li>
            </ul>
          </div>
          <div class="bg-purple-50 rounded-xl p-4 border border-purple-100">
            <div class="flex items-center gap-2 mb-3">
              <EyeOff class="w-5 h-5 text-purple-600" />
              <h3 class="text-gray-900 font-medium">Private (No One Sees)</h3>
            </div>
            <ul class="space-y-1 text-gray-600 text-sm">
              <li>• Your real identity</li>
              <li>• How you voted</li>
              <li>• Your voter registration ID</li>
              <li>• Which identifier belongs to you</li>
              <li>• Any personal information</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Data Security -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-success-50 flex items-center justify-center"
          >
            <Lock class="w-5 h-5 text-success-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">Data Security</h2>
        </div>

        <div class="space-y-4 text-gray-600">
          <p>
            Our security model assumes the worst case: what if our servers are
            completely compromised?
          </p>
          <div class="bg-warning-50 border border-warning-200 rounded-xl p-4">
            <div class="flex gap-3">
              <AlertTriangle
                class="w-5 h-5 text-warning-600 flex-shrink-0 mt-0.5"
              />
              <div>
                <h4 class="text-warning-700 font-medium mb-1">
                  Even if we're hacked:
                </h4>
                <ul class="text-sm space-y-1 text-gray-700">
                  <li>
                    • Attackers cannot determine your real identity from
                    anonymous IDs
                  </li>
                  <li>• Permanent records remain tamper-proof</li>
                  <li>
                    • Signatures cannot be forged (private keys are never
                    stored)
                  </li>
                  <li>• Feedback tallies cannot be altered</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Third Parties -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-cyan-50 flex items-center justify-center"
          >
            <Server class="w-5 h-5 text-cyan-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">Third Parties</h2>
        </div>

        <div class="space-y-4 text-gray-600">
          <p>We minimize third-party dependencies:</p>
          <ul class="space-y-2">
            <li class="flex items-start gap-2">
              <CheckCircle
                class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
              />
              <span
                ><strong class="text-gray-900">No Google Analytics</strong> or tracking
                scripts</span
              >
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle
                class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
              />
              <span
                ><strong class="text-gray-900">No advertising networks</strong
                ></span
              >
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle
                class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
              />
              <span
                ><strong class="text-gray-900">No social media pixels</strong
                ></span
              >
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle
                class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5"
              />
              <span
                ><strong class="text-gray-900">No data brokers</strong> or selling
                of information</span
              >
            </li>
          </ul>
        </div>
      </div>

      <!-- Your Rights -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div
            class="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center"
          >
            <Shield class="w-5 h-5 text-rose-600" />
          </div>
          <h2 class="text-xl font-bold text-gray-900">Your Rights</h2>
        </div>

        <div class="space-y-4 text-gray-600">
          <p>
            Because we don't store personal data, traditional "data rights" work
            differently here:
          </p>
          <ul class="space-y-3">
            <li>
              <strong class="text-gray-900">Right to Access:</strong>
              <span class="text-gray-500"
                >There's no personal data to access. Your identifier is just a
                random string with no link to you.</span
              >
            </li>
            <li>
              <strong class="text-gray-900">Right to Deletion:</strong>
              <span class="text-gray-500"
                >We can't delete what we don't have. Permanent records contain
                no personal data anyway.</span
              >
            </li>
            <li>
              <strong class="text-gray-900">Right to Portability:</strong>
              <span class="text-gray-500"
                >All data is public and verifiable. You can verify records
                anytime.</span
              >
            </li>
          </ul>
        </div>
      </div>

      <!-- Contact -->
      <div
        class="bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-100 rounded-2xl p-6 text-center"
      >
        <h2 class="text-xl font-bold text-gray-900 mb-4">
          Questions About Privacy?
        </h2>
        <p class="text-gray-600 mb-6">
          We're happy to explain our privacy architecture in more detail.
        </p>
        <a
          href="https://twitter.com/promisethread"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-2 bg-primary-700 hover:bg-primary-800 text-white px-6 py-3 rounded-lg transition-colors"
        >
          Contact Us on Twitter
        </a>
      </div>

      <!-- Last Updated -->
      <p class="text-center text-gray-500 text-sm">
        Last updated: December 2024
      </p>
    </div>
  </section>
</main>

<Footer />
