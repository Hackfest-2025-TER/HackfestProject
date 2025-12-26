<script>
  import { Shield } from "lucide-svelte";
</script>

<footer class="bg-gray-50 border-t border-gray-200 mt-auto">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
      <!-- Brand -->
      <div class="col-span-1 md:col-span-2">
        <div class="flex items-center space-x-2 mb-4">
          <div class="bg-primary-700 p-1.5 rounded-lg text-white">
            <Shield class="w-5 h-5 fill-current" />
          </div>
          <span class="text-xl font-bold font-serif text-gray-900"
            >WaachaPatra</span
          >
        </div>
        <p class="text-gray-500 text-sm leading-relaxed max-w-sm">
          A citizen-led platform to track political promises and hold leaders
          accountable. Built for transparency, designed for privacy.
        </p>
      </div>

      <!-- Quick Links -->
      <div>
        <h3
          class="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wider"
        >
          Explore
        </h3>
        <ul class="space-y-3">
          <li>
            <a
              href="/manifestos"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Promises</a
            >
          </li>
          <li>
            <a
              href="/representatives"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Representatives</a
            >
          </li>
          <li>
            <a
              href="/audit-trail"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Audit Trail</a
            >
          </li>
          <li>
            <a
              href="/citizen"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Citizen Portal</a
            >
          </li>
        </ul>
      </div>

      <!-- Resources -->
      <div>
        <h3
          class="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wider"
        >
          Resources
        </h3>
        <ul class="space-y-3">
          <li>
            <a
              href="/guide"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Guide</a
            >
          </li>
          <li>
            <a
              href="/faq"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >FAQ</a
            >
          </li>
          <li>
            <a
              href="/privacy"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >Privacy Policy</a
            >
          </li>
          <li>
            <a
              href="/about"
              class="text-gray-600 hover:text-primary-700 transition-colors text-sm font-medium"
              >About Us</a
            >
          </li>
        </ul>
      </div>
    </div>

    <div
      class="border-t border-gray-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-4"
    >
      <p class="text-gray-400 text-xs">
        &copy; 2025 WaachaPatra. All rights reserved.
      </p>
      <a href="/privacy" class="text-gray-400 hover:text-gray-600 text-xs"
        >Privacy Policy</a
      >
    </div>
  </div>
</footer>
