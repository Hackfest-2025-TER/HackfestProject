<script>
  import { Shield } from 'lucide-svelte';
</script>

<footer class="footer-main">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Brand -->
      <div class="col-span-1">
        <div class="flex items-center space-x-2 mb-4">
          <Shield class="w-7 h-7 text-emerald-400" />
          <span class="text-lg font-bold text-white">PromiseThread</span>
        </div>
        <p class="text-slate-300 text-sm">
          Track election promises. Hold leaders accountable. Stay anonymous.
        </p>
      </div>
      
      <!-- Quick Links -->
      <div>
        <h3 class="text-white font-medium mb-3 text-sm">Explore</h3>
        <ul class="space-y-2">
          <li><a href="/manifestos" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Promises</a></li>
          <li><a href="/politicians" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Politicians</a></li>
          <li><a href="/citizen" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Citizen Portal</a></li>
        </ul>
      </div>
      
      <!-- Resources -->
      <div>
        <h3 class="text-white font-medium mb-3 text-sm">Help</h3>
        <ul class="space-y-2">
          <li><a href="/guide" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Guide</a></li>
          <li><a href="/faq" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">FAQ</a></li>
          <li><a href="/verify" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Verify Promise Hash</a></li>
          <li><a href="/verify-signature" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Verify Digital Signature</a></li>
          <li><a href="/feedback" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Feedback</a></li>
          <li><a href="/privacy" class="text-slate-300 hover:text-emerald-400 transition-colors text-sm">Privacy</a></li>
        </ul>
      </div>
    </div>
    
    <div class="border-t border-slate-700/50 mt-8 pt-6 text-center">
      <p class="text-slate-400 text-xs">
        PromiseThread. Democracy works better when promises are remembered.
      </p>
    </div>
  </div>
</footer>

<style>
  .footer-main {
    background: #0f172a;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    margin-top: auto;
  }
</style>
