<script lang="ts">
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import {
    User,
    Camera,
    Save,
    Building2,
    MapPin,
    Calendar,
    Globe,
    Twitter,
    Mail,
    Phone,
    FileText,
    Shield,
    AlertCircle,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  // Representative session
  let representativeSession: any = null;
  let isLoading = true;
  let isSaving = false;
  let error = "";
  let success = "";

  // Form data
  let profile = {
    name: "",
    party: "",
    position: "",
    bio: "",
    province: "",
    district: "",
    website: "",
    twitter: "",
    email: "",
    phone: "",
  };

  // Positions list
  const positions = [
    "Prime Minister",
    "Minister",
    "Member of Parliament",
    "Chief Minister",
    "Provincial Assembly Member",
    "Mayor",
    "Deputy Mayor",
    "Ward Chairperson",
    "Other",
  ];

  // Parties list
  const parties = [
    "Nepali Congress",
    "CPN-UML",
    "CPN-MC",
    "RSP",
    "RPP",
    "JSP",
    "Independent",
    "Other",
  ];

  // Provinces
  const provinces = [
    "Koshi Province",
    "Madhesh Province",
    "Bagmati Province",
    "Gandaki Province",
    "Lumbini Province",
    "Karnali Province",
    "Sudurpashchim Province",
  ];

  onMount(async () => {
    const session = localStorage.getItem("representative_session");
    if (!session) {
      goto("/representative/login");
      return;
    }
    representativeSession = JSON.parse(session);

    // Load profile data (in production, fetch from API)
    profile.name = representativeSession.name || "";
    profile.party = representativeSession.party || "";
    profile.email = representativeSession.email || "";

    isLoading = false;
  });

  async function handleSave() {
    isSaving = true;
    error = "";
    success = "";

    try {
      // In production, save to API
      // await updateRepresentativeProfile(representativeSession.id, profile);

      // Update local session
      const updatedSession = { ...representativeSession, ...profile };
      localStorage.setItem(
        "representative_session",
        JSON.stringify(updatedSession),
      );
      representativeSession = updatedSession;

      success = "Profile updated successfully!";
      setTimeout(() => (success = ""), 3000);
    } catch (e: any) {
      error = e.message || "Failed to save profile";
    } finally {
      isSaving = false;
    }
  }
</script>

<svelte:head>
  <title>Edit Profile - WaachaPatra</title>
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-3xl mx-auto px-4">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Edit Profile</h1>
      <p class="text-gray-600">Update your public profile information</p>
    </div>

    {#if isLoading}
      <div class="text-center py-12">
        <div
          class="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mx-auto"
        ></div>
      </div>
    {:else}
      <form on:submit|preventDefault={handleSave} class="space-y-6">
        <!-- Status Messages -->
        {#if error}
          <div
            class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
          >
            <AlertCircle class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <span class="text-red-700">{error}</span>
          </div>
        {/if}

        {#if success}
          <div
            class="bg-success-50 border border-success-200 rounded-xl p-4 flex items-start gap-3"
          >
            <Shield class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
            <span class="text-success-700">{success}</span>
          </div>
        {/if}

        <!-- Profile Photo Section -->
        <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Profile Photo
          </h2>
          <div class="flex items-center gap-6">
            <div
              class="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-3xl font-bold text-primary-700"
            >
              {profile.name ? profile.name[0] : "P"}
            </div>
            <div>
              <button
                type="button"
                class="inline-flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                <Camera class="w-4 h-4" />
                Upload Photo
              </button>
              <p class="text-gray-500 text-sm mt-2">JPG, PNG up to 2MB</p>
            </div>
          </div>
        </div>

        <!-- Basic Information -->
        <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Basic Information
          </h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label
                for="name"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Full Name *</label
              >
              <div class="relative">
                <User
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                  type="text"
                  id="name"
                  bind:value={profile.name}
                  required
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label
                for="party"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Political Party *</label
              >
              <div class="relative">
                <Building2
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <select
                  id="party"
                  bind:value={profile.party}
                  required
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 focus:border-primary-500 outline-none appearance-none transition-colors"
                >
                  <option value="">Select Party</option>
                  {#each parties as party}
                    <option value={party}>{party}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div>
              <label
                for="position"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Current Position</label
              >
              <div class="relative">
                <FileText
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <select
                  id="position"
                  bind:value={profile.position}
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 focus:border-primary-500 outline-none appearance-none transition-colors"
                >
                  <option value="">Select Position</option>
                  {#each positions as pos}
                    <option value={pos}>{pos}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div>
              <label
                for="province"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Province</label
              >
              <div class="relative">
                <MapPin
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <select
                  id="province"
                  bind:value={profile.province}
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 focus:border-primary-500 outline-none appearance-none transition-colors"
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
            <label
              for="bio"
              class="block text-sm font-semibold text-gray-700 mb-2">Bio</label
            >
            <textarea
              id="bio"
              bind:value={profile.bio}
              rows="4"
              placeholder="Tell citizens about your background, experience, and vision..."
              class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none resize-none transition-colors"
            ></textarea>
          </div>
        </div>

        <!-- Contact Information -->
        <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Contact Information
          </h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label
                for="email"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Email</label
              >
              <div class="relative">
                <Mail
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                  type="email"
                  id="email"
                  bind:value={profile.email}
                  placeholder="contact@email.com"
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label
                for="phone"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Phone</label
              >
              <div class="relative">
                <Phone
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                  type="tel"
                  id="phone"
                  bind:value={profile.phone}
                  placeholder="+977-..."
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label
                for="website"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Website</label
              >
              <div class="relative">
                <Globe
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                  type="url"
                  id="website"
                  bind:value={profile.website}
                  placeholder="https://..."
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label
                for="twitter"
                class="block text-sm font-semibold text-gray-700 mb-2"
                >Twitter/X</label
              >
              <div class="relative">
                <Twitter
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                />
                <input
                  type="text"
                  id="twitter"
                  bind:value={profile.twitter}
                  placeholder="@username"
                  class="w-full bg-white border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Note about verification -->
        <div class="bg-primary-50 border border-primary-100 rounded-xl p-6">
          <div class="flex gap-3">
            <Shield class="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 class="text-primary-800 font-semibold mb-1">
                Profile Verification
              </h3>
              <p class="text-gray-600 text-sm leading-relaxed">
                Your profile information is publicly visible. Citizens use this
                to identify you and track your commitments. All changes are
                logged for transparency.
              </p>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="flex justify-end gap-4 pb-8">
          <a
            href="/representative/dashboard"
            class="px-6 py-3 text-gray-500 hover:text-gray-900 transition-colors bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium no-underline flex items-center"
          >
            Cancel
          </a>
          <button
            type="submit"
            disabled={isSaving}
            class="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white px-6 py-3 rounded-lg transition-all font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            {#if isSaving}
              <div
                class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
              ></div>
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
