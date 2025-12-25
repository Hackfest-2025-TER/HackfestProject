<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { 
    User, Camera, Save, Building2, MapPin, Calendar,
    Globe, Twitter, Mail, Phone, FileText, Shield, AlertCircle
  } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  // Politician session
  let politicianSession: any = null;
  let isLoading = true;
  let isSaving = false;
  let error = '';
  let success = '';
  
  // Form data
  let profile = {
    name: '',
    party: '',
    position: '',
    bio: '',
    province: '',
    district: '',
    website: '',
    twitter: '',
    email: '',
    phone: ''
  };
  
  // Positions list
  const positions = [
    'Prime Minister',
    'Minister',
    'Member of Parliament',
    'Chief Minister',
    'Provincial Assembly Member',
    'Mayor',
    'Deputy Mayor',
    'Ward Chairperson',
    'Other'
  ];
  
  // Parties list
  const parties = [
    'Nepali Congress',
    'CPN-UML',
    'CPN-MC',
    'RSP',
    'RPP',
    'JSP',
    'Independent',
    'Other'
  ];
  
  // Provinces
  const provinces = [
    'Koshi Province',
    'Madhesh Province',
    'Bagmati Province',
    'Gandaki Province',
    'Lumbini Province',
    'Karnali Province',
    'Sudurpashchim Province'
  ];
  
  onMount(async () => {
    const session = localStorage.getItem('politician_session');
    if (!session) {
      goto('/politician/login');
      return;
    }
    politicianSession = JSON.parse(session);
    
    // Load profile data (in production, fetch from API)
    profile.name = politicianSession.name || '';
    profile.party = politicianSession.party || '';
    profile.email = politicianSession.email || '';
    
    isLoading = false;
  });
  
  async function handleSave() {
    isSaving = true;
    error = '';
    success = '';
    
    try {
      // In production, save to API
      // await updatePoliticianProfile(politicianSession.id, profile);
      
      // Update local session
      const updatedSession = { ...politicianSession, ...profile };
      localStorage.setItem('politician_session', JSON.stringify(updatedSession));
      politicianSession = updatedSession;
      
      success = 'Profile updated successfully!';
      setTimeout(() => success = '', 3000);
    } catch (e: any) {
      error = e.message || 'Failed to save profile';
    } finally {
      isSaving = false;
    }
  }
</script>

<svelte:head>
  <title>Edit Profile - PromiseThread</title>
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-3xl mx-auto px-4">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">Edit Profile</h1>
      <p class="text-slate-400">Update your public profile information</p>
    </div>
    
    {#if isLoading}
      <div class="text-center py-12">
        <div class="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto"></div>
      </div>
    {:else}
      <form on:submit|preventDefault={handleSave} class="space-y-6">
        <!-- Status Messages -->
        {#if error}
          <div class="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <span class="text-red-400">{error}</span>
          </div>
        {/if}
        
        {#if success}
          <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4 flex items-start gap-3">
            <Shield class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span class="text-emerald-400">{success}</span>
          </div>
        {/if}
        
        <!-- Profile Photo Section -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Profile Photo</h2>
          <div class="flex items-center gap-6">
            <div class="w-24 h-24 rounded-full bg-slate-700 flex items-center justify-center text-3xl font-bold text-white">
              {profile.name ? profile.name[0] : 'P'}
            </div>
            <div>
              <button
                type="button"
                class="inline-flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Camera class="w-4 h-4" />
                Upload Photo
              </button>
              <p class="text-slate-500 text-sm mt-2">JPG, PNG up to 2MB</p>
            </div>
          </div>
        </div>
        
        <!-- Basic Information -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Basic Information</h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label for="name" class="block text-sm font-medium text-slate-300 mb-2">Full Name *</label>
              <div class="relative">
                <User class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  id="name"
                  bind:value={profile.name}
                  required
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
            
            <div>
              <label for="party" class="block text-sm font-medium text-slate-300 mb-2">Political Party *</label>
              <div class="relative">
                <Building2 class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <select
                  id="party"
                  bind:value={profile.party}
                  required
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none appearance-none"
                >
                  <option value="">Select Party</option>
                  {#each parties as party}
                    <option value={party}>{party}</option>
                  {/each}
                </select>
              </div>
            </div>
            
            <div>
              <label for="position" class="block text-sm font-medium text-slate-300 mb-2">Current Position</label>
              <div class="relative">
                <FileText class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <select
                  id="position"
                  bind:value={profile.position}
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none appearance-none"
                >
                  <option value="">Select Position</option>
                  {#each positions as pos}
                    <option value={pos}>{pos}</option>
                  {/each}
                </select>
              </div>
            </div>
            
            <div>
              <label for="province" class="block text-sm font-medium text-slate-300 mb-2">Province</label>
              <div class="relative">
                <MapPin class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <select
                  id="province"
                  bind:value={profile.province}
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none appearance-none"
                >
                  <option value="">Select Province</option>
                  {#each provinces as prov}
                    <option value={prov}>{prov}</option>
                  {/each}
                </select>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <label for="bio" class="block text-sm font-medium text-slate-300 mb-2">Bio</label>
            <textarea
              id="bio"
              bind:value={profile.bio}
              rows="4"
              placeholder="Tell citizens about your background, experience, and vision..."
              class="w-full bg-slate-900/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none"
            ></textarea>
          </div>
        </div>
        
        <!-- Contact Information -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Contact Information</h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label for="email" class="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <div class="relative">
                <Mail class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  id="email"
                  bind:value={profile.email}
                  placeholder="contact@email.com"
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
            
            <div>
              <label for="phone" class="block text-sm font-medium text-slate-300 mb-2">Phone</label>
              <div class="relative">
                <Phone class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  id="phone"
                  bind:value={profile.phone}
                  placeholder="+977-..."
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
            
            <div>
              <label for="website" class="block text-sm font-medium text-slate-300 mb-2">Website</label>
              <div class="relative">
                <Globe class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="url"
                  id="website"
                  bind:value={profile.website}
                  placeholder="https://..."
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
            
            <div>
              <label for="twitter" class="block text-sm font-medium text-slate-300 mb-2">Twitter/X</label>
              <div class="relative">
                <Twitter class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  id="twitter"
                  bind:value={profile.twitter}
                  placeholder="@username"
                  class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Note about verification -->
        <div class="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
          <div class="flex gap-3">
            <Shield class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 class="text-blue-400 font-medium mb-1">Profile Verification</h3>
              <p class="text-slate-400 text-sm">
                Your profile information is publicly visible. Citizens use this to identify you and track your commitments.
                All changes are logged for transparency.
              </p>
            </div>
          </div>
        </div>
        
        <!-- Submit -->
        <div class="flex justify-end gap-4">
          <a 
            href="/politician/dashboard"
            class="px-6 py-3 text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </a>
          <button
            type="submit"
            disabled={isSaving}
            class="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-500/50 text-white px-6 py-3 rounded-lg transition-colors font-medium"
          >
            {#if isSaving}
              <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Saving...
            {:else}
              <Save class="w-5 h-5" />
              Save Changes
            {/if}
          </button>
        </div>
      </form>
    {/if}
  </div>
</main>

<Footer />
