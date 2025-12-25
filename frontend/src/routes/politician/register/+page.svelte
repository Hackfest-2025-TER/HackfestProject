<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { credential, authStore } from '$lib/stores';
	import { get } from 'svelte/store';
	import { CheckCircle, AlertCircle, UserCheck, Loader2, ArrowRight, Shield } from 'lucide-svelte';

	interface RegistrationData {
		nullifier: string;
		name: string;
		party: string;
		position: string;
		bio: string;
		image_url: string;
		election_commission_id: string;
	}

	let formData: RegistrationData = {
		nullifier: '',
		name: '',
		party: '',
		position: '',
		bio: '',
		image_url: '',
		election_commission_id: ''
	};

	let loading = false;
	let error = '';
	let success = false;
	let politicianId: number | null = null;
	let applicationStatus = '';
	let credentialVerified = false;

	onMount(() => {
		// Check if user has ZK credential
		const cred = get(credential);
		if (!cred || !cred.nullifier) {
			error = 'You must authenticate as a citizen first. Redirecting...';
			setTimeout(() => goto('/auth'), 2000);
			return;
		}
		formData.nullifier = cred.nullifier;
		credentialVerified = true;
	});

	async function handleSubmit() {
		loading = true;
		error = '';

		// Validation
		if (!formData.name.trim()) {
			error = 'Full name is required';
			loading = false;
			return;
		}

		try {
			const response = await fetch('http://localhost:8000/api/politicians/register', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					nullifier: formData.nullifier,
					name: formData.name.trim(),
					party: formData.party.trim() || null,
					position: formData.position.trim() || null,
					bio: formData.bio.trim() || null,
					image_url: formData.image_url.trim() || null,
					election_commission_id: formData.election_commission_id.trim() || null
				})
			});

			const data = await response.json();

			if (response.ok) {
				success = true;
				politicianId = data.politician.id;
				applicationStatus = data.politician.application_status;
				
				// Update auth store to mark user as politician
				const currentCred = get(credential);
				if (currentCred) {
					authStore.setCredential({
						...currentCred,
						isPolitician: true,
						politicianId: data.politician.id,
						politicianSlug: data.politician.slug
					});
				}
			} else {
				error = data.detail || 'Registration failed. Please try again.';
			}
		} catch (err) {
			error = 'Network error. Please ensure the backend is running on port 8000.';
			console.error(err);
		} finally {
			loading = false;
		}
	}

	function resetForm() {
		formData = {
			nullifier: formData.nullifier,
			name: '',
			party: '',
			position: '',
			bio: '',
			image_url: '',
			election_commission_id: ''
		};
		error = '';
		success = false;
	}
</script>

<svelte:head>
	<title>Register as Politician - PromiseThread</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12 px-4">
	<div class="max-w-4xl mx-auto">
		<!-- Header Section -->
		<div class="text-center mb-12">
			<div class="flex justify-center mb-6">
				<div class="p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full shadow-lg">
					<UserCheck class="w-12 h-12 text-white" />
				</div>
			</div>
			<h1 class="text-5xl font-bold text-white mb-3">Register as Politician</h1>
			<p class="text-lg text-slate-300 mb-4">
				Join PromiseThread and make your political commitments transparent and accountable
			</p>
			<div class="mt-6 flex items-center justify-center gap-3 text-sm text-green-400 font-medium">
				<CheckCircle class="w-5 h-5" />
				<span>Instant Verification via Zero-Knowledge Proofs - No Admin Approval Needed</span>
			</div>
		</div>

		<!-- Credential Status Card -->
		{#if credentialVerified}
			<div class="mb-8 bg-green-500/10 border border-green-500/30 rounded-lg p-4 flex items-start gap-4">
				<div class="p-2 bg-green-500/20 rounded-lg">
					<Shield class="w-6 h-6 text-green-400" />
				</div>
				<div>
					<p class="font-semibold text-green-400">✓ Citizen Verified</p>
					<p class="text-sm text-slate-300 mt-1">
						Your ZK credential has verified your citizenship. You can now register as a politician.
					</p>
				</div>
			</div>
		{/if}

		<!-- Success State -->
		{#if success}
			<div class="space-y-6">
				<!-- Success Message -->
				<div class="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/50 rounded-lg p-8 text-center">
					<div class="mb-6">
						<CheckCircle class="w-16 h-16 text-green-400 mx-auto animate-bounce" />
					</div>
					<h2 class="text-3xl font-bold text-white mb-3">🎉 Registration Complete!</h2>
					<p class="text-slate-300 mb-6 text-lg">
						You are now a verified politician in the PromiseThread network.
					</p>

					<!-- Politician Details Card -->
					<div class="bg-slate-800/50 rounded-lg p-6 mb-8 text-left max-w-md mx-auto border border-slate-700">
						<div class="mb-4">
							<p class="text-xs uppercase tracking-wide text-slate-400 font-semibold">Politician ID</p>
							<p class="text-3xl font-bold text-blue-400 font-mono mt-1">#{politicianId}</p>
						</div>
						<div class="border-t border-slate-700 pt-4">
							<p class="text-xs uppercase tracking-wide text-slate-400 font-semibold mb-2">Application Status</p>
							<div class="flex items-center gap-2">
								<CheckCircle class="w-5 h-5 text-green-400" />
								<span class="text-lg font-semibold text-green-400 capitalize">{applicationStatus}</span>
							</div>
						</div>
					</div>

					<!-- Info Box -->
					<div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-8">
						<p class="text-sm text-blue-300 leading-relaxed">
							<strong>🔐 How This Works:</strong> Your ZK credential automatically verified your citizenship without revealing your identity.
							This is true decentralization - no central authority controls who can participate. You can now immediately start
							creating and posting manifestos on PromiseThread!
						</p>
					</div>

					<!-- Next Steps -->
					<div class="mb-6">
						<p class="text-slate-400 text-sm font-medium mb-4">Next Steps</p>
						<div class="space-y-2 text-left max-w-md mx-auto">
							<div class="flex gap-3 items-start">
								<div class="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">1</div>
								<div>
									<p class="text-slate-300 font-medium">Visit your dashboard</p>
									<p class="text-xs text-slate-400">Manage your profile and manifestos</p>
								</div>
							</div>
							<div class="flex gap-3 items-start">
								<div class="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">2</div>
								<div>
									<p class="text-slate-300 font-medium">Create your first manifesto</p>
									<p class="text-xs text-slate-400">Post your political promises with clear deadlines</p>
								</div>
							</div>
							<div class="flex gap-3 items-start">
								<div class="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">3</div>
								<div>
									<p class="text-slate-300 font-medium">Community discussion</p>
									<p class="text-xs text-slate-400">Citizens discuss and hold you accountable</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Action Buttons -->
					<div class="flex gap-3 justify-center flex-wrap">
						<a
							href="/politician/dashboard"
							class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors flex items-center gap-2 no-underline"
						>
							<ArrowRight class="w-4 h-4" />
							Go to Dashboard
						</a>
						<a
							href="/politician/new-manifesto"
							class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors flex items-center gap-2 no-underline"
						>
							<ArrowRight class="w-4 h-4" />
							Create First Manifesto
						</a>
					</div>
				</div>
			</div>
		{:else}
			<!-- Registration Form -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
				<!-- Main Form -->
				<div class="lg:col-span-2">
					<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-8 backdrop-blur">
						<h2 class="text-2xl font-bold text-white mb-6">Your Information</h2>
						<form on:submit|preventDefault={handleSubmit} class="space-y-6">
							<!-- Name -->
							<div>
								<label for="name" class="block text-sm font-semibold text-slate-200 mb-2">
									Full Name <span class="text-red-400">*</span>
								</label>
								<input
									id="name"
									type="text"
									bind:value={formData.name}
									required
									placeholder="Your full legal name as per voter registry"
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
								/>
								<p class="text-xs text-slate-400 mt-1">
									Must match your voter registry entry for verification
								</p>
							</div>

							<!-- Party -->
							<div>
								<label for="party" class="block text-sm font-semibold text-slate-200 mb-2">
									Political Party
								</label>
								<input
									id="party"
									type="text"
									bind:value={formData.party}
									placeholder="e.g., Progressive Party, Independent"
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
								/>
							</div>

							<!-- Position -->
							<div>
								<label for="position" class="block text-sm font-semibold text-slate-200 mb-2">
									Position / Office Seeking
								</label>
								<input
									id="position"
									type="text"
									bind:value={formData.position}
									placeholder="e.g., Mayor Candidate, State Representative"
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
								/>
							</div>

							<!-- Election Commission ID -->
							<div>
								<label for="ec_id" class="block text-sm font-semibold text-slate-200 mb-2">
									Election Commission ID <span class="text-slate-400">(Optional)</span>
								</label>
								<input
									id="ec_id"
									type="text"
									bind:value={formData.election_commission_id}
									placeholder="e.g., EC-2025-KA-12345"
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
								/>
								<p class="text-xs text-slate-400 mt-1">
									Your official registration ID with the election commission
								</p>
							</div>

							<!-- Bio -->
							<div>
								<label for="bio" class="block text-sm font-semibold text-slate-200 mb-2">
									Biography
								</label>
								<textarea
									id="bio"
									bind:value={formData.bio}
									rows="4"
									placeholder="Tell voters about your background, experience, achievements, and why you're running..."
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none"
								/>
								<p class="text-xs text-slate-400 mt-1">
									Maximum 500 characters recommended
								</p>
							</div>

							<!-- Image URL -->
							<div>
								<label for="image" class="block text-sm font-semibold text-slate-200 mb-2">
									Profile Image URL <span class="text-slate-400">(Optional)</span>
								</label>
								<input
									id="image"
									type="url"
									bind:value={formData.image_url}
									placeholder="https://example.com/your-profile-photo.jpg"
									class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
								/>
								<p class="text-xs text-slate-400 mt-1">
									Use a professional headshot (JPEG or PNG)
								</p>
							</div>

							<!-- Error Message -->
							{#if error}
								<div class="bg-red-500/20 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
									<AlertCircle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
									<div>
										<p class="text-red-400 font-semibold">Error</p>
										<p class="text-red-300 text-sm mt-1">{error}</p>
									</div>
								</div>
							{/if}

							<!-- Submit Button -->
							<div class="pt-4">
								<button
									type="submit"
									disabled={loading || !formData.name || !credentialVerified}
									class="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 text-lg"
								>
									{#if loading}
										<Loader2 class="w-5 h-5 animate-spin" />
										Registering & Verifying...
									{:else}
										<CheckCircle class="w-5 h-5" />
										Register as Politician
									{/if}
								</button>
							</div>
						</form>
					</div>
				</div>

				<!-- Info Sidebar -->
				<div class="lg:col-span-1">
					<!-- How It Works -->
					<div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6 mb-6">
						<h3 class="font-bold text-blue-300 mb-4 flex items-center gap-2">
							<CheckCircle class="w-5 h-5" />
							How It Works
						</h3>
						<ol class="space-y-3 text-sm text-slate-300">
							<li class="flex gap-3">
								<span class="flex-shrink-0 font-bold text-blue-400">1</span>
								<span>Verify citizenship via ZK proof (already done)</span>
							</li>
							<li class="flex gap-3">
								<span class="flex-shrink-0 font-bold text-blue-400">2</span>
								<span>Fill this form with your information</span>
							</li>
							<li class="flex gap-3">
								<span class="flex-shrink-0 font-bold text-blue-400">3</span>
								<span>Auto-verified instantly</span>
							</li>
							<li class="flex gap-3">
								<span class="flex-shrink-0 font-bold text-blue-400">4</span>
								<span>Start posting manifestos</span>
							</li>
						</ol>
					</div>

					<!-- Key Benefits -->
					<div class="bg-purple-500/10 border border-purple-500/30 rounded-lg p-6 mb-6">
						<h3 class="font-bold text-purple-300 mb-4">Benefits</h3>
						<ul class="space-y-2 text-sm text-slate-300">
							<li class="flex gap-2">
								<span class="text-green-400 flex-shrink-0">✓</span>
								<span>No waiting period</span>
							</li>
							<li class="flex gap-2">
								<span class="text-green-400 flex-shrink-0">✓</span>
								<span>Immutable promises</span>
							</li>
							<li class="flex gap-2">
								<span class="text-green-400 flex-shrink-0">✓</span>
								<span>Community accountability</span>
							</li>
							<li class="flex gap-2">
								<span class="text-green-400 flex-shrink-0">✓</span>
								<span>Transparent voting</span>
							</li>
							<li class="flex gap-2">
								<span class="text-green-400 flex-shrink-0">✓</span>
								<span>Privacy protected</span>
							</li>
						</ul>
					</div>

					<!-- Privacy Notice -->
					<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
						<h3 class="font-bold text-slate-200 mb-3 text-sm">Privacy Notice</h3>
						<p class="text-xs text-slate-400 leading-relaxed">
							Your registration is tied to your ZK credential, not your real identity. Your name and party
							information are public, but your identity remains anonymous through cryptography.
						</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- Back Link -->
		<div class="text-center mt-8">
			<a
				href="/politicians"
				class="text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-2"
			>
				← View All Politicians
			</a>
		</div>
	</div>
</div>

<style>
	:global(body) {
		@apply bg-slate-950;
	}
	
	.no-underline {
		text-decoration: none;
	}
	
	.no-underline:hover {
		text-decoration: none;
	}
</style>