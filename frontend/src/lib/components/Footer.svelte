<script>
  import { Shield, Github, Twitter } from 'lucide-svelte';
</script>

<footer class="footer-main">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
      <!-- Brand -->
      <div class="col-span-1 md:col-span-2">
        <div class="flex items-center space-x-2 mb-4">
          <Shield class="w-8 h-8 text-emerald-400" />
          <span class="text-xl font-bold text-white">PromiseThread</span>
        </div>
        <p class="text-slate-300 mb-4">
          A platform where citizens can track election promises and share their feedback — 
          all while keeping their identity completely private.
        </p>
        <div class="flex space-x-4">
          <a href="https://github.com" class="text-slate-400 hover:text-emerald-400 transition-colors">
            <Github class="w-5 h-5" />
          </a>
          <a href="https://twitter.com" class="text-slate-400 hover:text-emerald-400 transition-colors">
            <Twitter class="w-5 h-5" />
          </a>
        </div>
      </div>
      
      <!-- Quick Links -->
      <div>
        <h3 class="text-white font-semibold mb-4">Explore</h3>
        <ul class="space-y-2">
          <li><a href="/manifestos" class="text-slate-300 hover:text-emerald-400 transition-colors">View Promises</a></li>
          <li><a href="/politicians" class="text-slate-300 hover:text-emerald-400 transition-colors">Politicians</a></li>
          <li><a href="/auth" class="text-slate-300 hover:text-emerald-400 transition-colors">Verify as Citizen</a></li>
        </ul>
      </div>
      
      <!-- Resources -->
      <div>
        <h3 class="text-white font-semibold mb-4">Help</h3>
        <ul class="space-y-2">
          <li><a href="/feedback" class="text-slate-300 hover:text-emerald-400 transition-colors">Give Feedback</a></li>
          <li><a href="/privacy" class="text-slate-300 hover:text-emerald-400 transition-colors">How We Protect Your Privacy</a></li>
          <li><a href="/guide" class="text-slate-300 hover:text-emerald-400 transition-colors">Citizen Guide</a></li>
        </ul>
      </div>
    </div>
    
    <div class="border-t border-slate-700 mt-8 pt-8 text-center">
      <p class="text-slate-400 text-sm">
        © 2024 PromiseThread. Democracy works better when promises are remembered.
      </p>
    </div>
  </div>
</footer>

<style>
  .footer-main {
    background: #082770;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: auto;
  }
</style>
