<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { credential, authStore } from "$lib/stores";
	import { get } from "svelte/store";
	import {
		CheckCircle,
		AlertCircle,
		UserCheck,
		Loader2,
		ArrowRight,
		Shield,
	} from "lucide-svelte";

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
		nullifier: "",
		name: "",
		party: "",
		position: "",
		bio: "",
		image_url: "",
		election_commission_id: "",
	};

	let loading = false;
	let error = "";
	let success = false;
	let representativeId: number | null = null;
	let applicationStatus = "";
	let credentialVerified = false;

	onMount(() => {
		// Check if user has ZK credential
		const cred = get(credential);
		if (!cred || !cred.nullifier) {
			error = "You must authenticate as a citizen first. Redirecting...";
			setTimeout(() => goto("/auth"), 2000);
			return;
		}
		formData.nullifier = cred.nullifier;
		credentialVerified = true;
	});

	async function handleSubmit() {
		loading = true;
		error = "";

		// Validation
		if (!formData.name.trim()) {
			error = "Full name is required";
			loading = false;
			return;
		}

		try {
			const response = await fetch(
				"http://localhost:8000/api/representatives/register",
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						nullifier: formData.nullifier,
						name: formData.name.trim(),
						party: formData.party.trim() || null,
						position: formData.position.trim() || null,
						bio: formData.bio.trim() || null,
						image_url: formData.image_url.trim() || null,
						election_commission_id:
							formData.election_commission_id.trim() || null,
					}),
				},
			);

			const data = await response.json();

			if (response.ok) {
				success = true;
				representativeId = data.representative.id;
				applicationStatus = data.representative.application_status;

				// Update auth store to mark user as representative
				const currentCred = get(credential);
				if (currentCred) {
					authStore.setCredential({
						...currentCred,
						isRepresentative: true,
						representativeId: data.representative.id,
						representativeSlug: data.representative.slug,
					});
				}
			} else {
				error = data.detail || "Registration failed. Please try again.";
			}
		} catch (err) {
			error =
				"Network error. Please ensure the backend is running on port 8000.";
			console.error(err);
		} finally {
			loading = false;
		}
	}

	function resetForm() {
		formData = {
			nullifier: formData.nullifier,
			name: "",
			party: "",
			position: "",
			bio: "",
			image_url: "",
			election_commission_id: "",
		};
		error = "";
		success = false;
	}
</script>

<svelte:head>
	<title>Register as Representative - WaachaPatra</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 py-12 px-4">
	<div class="max-w-4xl mx-auto">
		<!-- Header Section -->
		<div class="text-center mb-12">
			<div class="flex justify-center mb-6">
				<div class="p-4 bg-primary-50 rounded-full">
					<UserCheck class="w-12 h-12 text-primary-600" />
				</div>
			</div>
			<h1
				class="text-4xl md:text-5xl font-bold font-serif text-gray-900 mb-3"
			>
				Register as Representative
			</h1>
			<p class="text-lg text-gray-600 mb-4 max-w-2xl mx-auto">
				Join WaachaPatra and make your political commitments
				transparent and accountable.
			</p>
			<div
				class="mt-6 flex items-center justify-center gap-3 text-sm text-success-700 font-medium bg-success-50 py-2 px-4 rounded-full inline-flex mx-auto border border-success-200"
			>
				<CheckCircle class="w-5 h-5" />
				<span>Instant Verification - No Admin Approval Needed</span>
			</div>
		</div>

		<!-- Credential Status Card -->
		{#if credentialVerified}
			<div
				class="mb-8 bg-success-50 border border-success-200 rounded-xl p-4 flex items-start gap-4 shadow-sm"
			>
				<div
					class="p-2 bg-white rounded-lg border border-success-100 shadow-sm"
				>
					<Shield class="w-6 h-6 text-success-600" />
				</div>
				<div>
					<p class="font-semibold text-success-800">
						✓ Citizen Verified
					</p>
					<p class="text-sm text-success-700 mt-1">
						Your citizenship has been verified securely. You can now
						register as a representative.
					</p>
				</div>
			</div>
		{/if}

		<!-- Success State -->
		{#if success}
			<div class="space-y-6">
				<!-- Success Message -->
				<div
					class="bg-white border border-gray-200 rounded-2xl p-8 text-center shadow-lg"
				>
					<div class="mb-6">
						<div
							class="w-20 h-20 bg-success-50 rounded-full flex items-center justify-center mx-auto"
						>
							<CheckCircle class="w-12 h-12 text-success-600" />
						</div>
					</div>
					<h2 class="text-3xl font-bold text-gray-900 mb-3">
						🎉 Registration Complete!
					</h2>
					<p class="text-gray-600 mb-8 text-lg">
						You are now a verified representative in the WaachaPatra
						network.
					</p>

					<!-- Representative Details Card -->
					<div
						class="bg-gray-50 rounded-xl p-6 mb-8 text-left max-w-md mx-auto border border-gray-200"
					>
						<div class="mb-4">
							<p
								class="text-xs uppercase tracking-wide text-gray-500 font-semibold"
							>
								Representative ID
							</p>
							<p
								class="text-3xl font-bold text-primary-700 font-mono mt-1"
							>
								#{representativeId}
							</p>
						</div>
						<div class="border-t border-gray-200 pt-4">
							<p
								class="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2"
							>
								Application Status
							</p>
							<div class="flex items-center gap-2">
								<CheckCircle class="w-5 h-5 text-success-600" />
								<span
									class="text-lg font-semibold text-success-700 capitalize"
									>{applicationStatus}</span
								>
							</div>
						</div>
					</div>

					<!-- Info Box -->
					<div
						class="bg-primary-50 border border-primary-100 rounded-xl p-6 mb-8 text-left"
					>
						<p class="text-sm text-primary-800 leading-relaxed">
							<strong>🔐 How This Works:</strong> Your credential automatically
							verified your citizenship without revealing your personal
							history. This ensures a fair and open platform. You can
							now immediately start creating and posting promises!
						</p>
					</div>

					<!-- Next Steps -->
					<div class="mb-8">
						<p
							class="text-gray-900 text-sm font-semibold mb-4 uppercase tracking-wide"
						>
							Next Steps
						</p>
						<div class="space-y-3 text-left max-w-md mx-auto">
							<div
								class="flex gap-4 items-start p-3 rounded-lg hover:bg-gray-50 transition-colors"
							>
								<div
									class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 text-sm font-bold"
								>
									1
								</div>
								<div>
									<p class="text-gray-900 font-medium">
										Visit your dashboard
									</p>
									<p class="text-sm text-gray-500">
										Manage your profile and promises
									</p>
								</div>
							</div>
							<div
								class="flex gap-4 items-start p-3 rounded-lg hover:bg-gray-50 transition-colors"
							>
								<div
									class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 text-sm font-bold"
								>
									2
								</div>
								<div>
									<p class="text-gray-900 font-medium">
										Create your first promise
									</p>
									<p class="text-sm text-gray-500">
										Post your political promises with clear
										deadlines
									</p>
								</div>
							</div>
							<div
								class="flex gap-4 items-start p-3 rounded-lg hover:bg-gray-50 transition-colors"
							>
								<div
									class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 text-sm font-bold"
								>
									3
								</div>
								<div>
									<p class="text-gray-900 font-medium">
										Community discussion
									</p>
									<p class="text-sm text-gray-500">
										Citizens discuss and hold you
										accountable
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Action Buttons -->
					<div class="flex gap-4 justify-center flex-wrap">
						<a
							href="/representative/dashboard"
							class="px-8 py-3 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-xl font-semibold transition-all shadow-sm flex items-center gap-2 no-underline"
						>
							<ArrowRight class="w-4 h-4" />
							Go to Dashboard
						</a>
						<a
							href="/representative/new-manifesto"
							class="px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-all shadow-md hover:shadow-lg flex items-center gap-2 no-underline"
						>
							<ArrowRight class="w-4 h-4" />
							Create First Promise
						</a>
					</div>
				</div>
			</div>
		{:else}
			<!-- Registration Form -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
				<!-- Main Form -->
				<div class="lg:col-span-2">
					<div
						class="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm"
					>
						<h2
							class="text-2xl font-bold text-gray-900 mb-6 font-serif"
						>
							Your Information
						</h2>
						<form
							on:submit|preventDefault={handleSubmit}
							class="space-y-6"
						>
							<!-- Name -->
							<div>
								<label
									for="name"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Full Name <span class="text-red-500">*</span
									>
								</label>
								<input
									id="name"
									type="text"
									bind:value={formData.name}
									required
									placeholder="Your full legal name as per voter registry"
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition shadow-sm"
								/>
								<p class="text-xs text-gray-500 mt-1">
									Must match your voter registry entry for
									verification
								</p>
							</div>

							<!-- Party -->
							<div>
								<label
									for="party"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Political Party
								</label>
								<input
									id="party"
									type="text"
									bind:value={formData.party}
									placeholder="e.g., Progressive Party, Independent"
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition shadow-sm"
								/>
							</div>

							<!-- Position -->
							<div>
								<label
									for="position"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Position / Office Seeking
								</label>
								<input
									id="position"
									type="text"
									bind:value={formData.position}
									placeholder="e.g., Mayor Candidate, State Representative"
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition shadow-sm"
								/>
							</div>

							<!-- Election Commission ID -->
							<div>
								<label
									for="ec_id"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Election Commission ID <span
										class="text-gray-400 font-normal"
										>(Optional)</span
									>
								</label>
								<input
									id="ec_id"
									type="text"
									bind:value={formData.election_commission_id}
									placeholder="e.g., EC-2025-KA-12345"
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition shadow-sm"
								/>
								<p class="text-xs text-gray-500 mt-1">
									Your official registration ID with the
									election commission
								</p>
							</div>

							<!-- Bio -->
							<div>
								<label
									for="bio"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Biography
								</label>
								<textarea
									id="bio"
									bind:value={formData.bio}
									rows="4"
									placeholder="Tell voters about your background, experience, achievements, and why you're running..."
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition resize-none shadow-sm"
								/>
								<p class="text-xs text-gray-500 mt-1">
									Maximum 500 characters recommended
								</p>
							</div>

							<!-- Image URL -->
							<div>
								<label
									for="image"
									class="block text-sm font-semibold text-gray-700 mb-2"
								>
									Profile Image URL <span
										class="text-gray-400 font-normal"
										>(Optional)</span
									>
								</label>
								<input
									id="image"
									type="url"
									bind:value={formData.image_url}
									placeholder="https://example.com/your-profile-photo.jpg"
									class="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition shadow-sm"
								/>
								<p class="text-xs text-gray-500 mt-1">
									Use a professional headshot (JPEG or PNG)
								</p>
							</div>

							<!-- Error Message -->
							{#if error}
								<div
									class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
								>
									<AlertCircle
										class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
									/>
									<div>
										<p class="text-red-700 font-semibold">
											Error
										</p>
										<p class="text-red-600 text-sm mt-1">
											{error}
										</p>
									</div>
								</div>
							{/if}

							<!-- Submit Button -->
							<div class="pt-4">
								<button
									type="submit"
									disabled={loading ||
										!formData.name ||
										!credentialVerified}
									class="w-full py-4 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 text-lg transform hover:-translate-y-0.5 active:translate-y-0"
								>
									{#if loading}
										<Loader2 class="w-5 h-5 animate-spin" />
										Registering & Verifying...
									{:else}
										<CheckCircle class="w-5 h-5" />
										Register as Representative
									{/if}
								</button>
							</div>
						</form>
					</div>
				</div>

				<!-- Info Sidebar -->
				<div class="lg:col-span-1 space-y-6">
					<!-- How It Works -->
					<div
						class="bg-primary-50 border border-primary-100 rounded-2xl p-6"
					>
						<h3
							class="font-bold text-primary-800 mb-4 flex items-center gap-2"
						>
							<CheckCircle class="w-5 h-5" />
							How It Works
						</h3>
						<ol class="space-y-4 text-sm text-gray-600">
							<li class="flex gap-3">
								<span
									class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-primary-100 text-primary-700 font-bold text-xs"
									>1</span
								>
								<span>Verify citizenship (already done)</span>
							</li>
							<li class="flex gap-3">
								<span
									class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-primary-100 text-primary-700 font-bold text-xs"
									>2</span
								>
								<span>Fill this form with your information</span
								>
							</li>
							<li class="flex gap-3">
								<span
									class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-primary-100 text-primary-700 font-bold text-xs"
									>3</span
								>
								<span>Auto-verified instantly</span>
							</li>
							<li class="flex gap-3">
								<span
									class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-primary-100 text-primary-700 font-bold text-xs"
									>4</span
								>
								<span>Start posting promises</span>
							</li>
						</ol>
					</div>

					<!-- Key Benefits -->
					<div
						class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm"
					>
						<h3 class="font-bold text-gray-900 mb-4">Benefits</h3>
						<ul class="space-y-3 text-sm text-gray-600">
							<li class="flex gap-2">
								<span class="text-success-600 flex-shrink-0"
									>✓</span
								>
								<span>No waiting period</span>
							</li>
							<li class="flex gap-2">
								<span class="text-success-600 flex-shrink-0"
									>✓</span
								>
								<span>Immutable promises</span>
							</li>
							<li class="flex gap-2">
								<span class="text-success-600 flex-shrink-0"
									>✓</span
								>
								<span>Community accountability</span>
							</li>

							<li class="flex gap-2">
								<span class="text-success-600 flex-shrink-0"
									>✓</span
								>
								<span>Privacy protected</span>
							</li>
						</ul>
					</div>

					<!-- Privacy Notice -->
					<div
						class="bg-gray-50 border border-gray-200 rounded-2xl p-6"
					>
						<h3
							class="font-bold text-gray-900 mb-2 text-sm flex items-center gap-2"
						>
							<Shield class="w-4 h-4 text-gray-500" />
							Privacy Notice
						</h3>
						<p class="text-xs text-gray-500 leading-relaxed">
							Your registration is tied to your verified
							credential. Your name and party information are
							public, but your underlying identity remains
							protected.
						</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- Back Link -->
		<div class="text-center mt-8">
			<button
				on:click={() => goto("/representatives")}
				class="text-gray-500 hover:text-primary-600 transition-colors flex items-center justify-center gap-2 bg-transparent border-none cursor-pointer mx-auto"
			>
				← View All Representatives
			</button>
		</div>
	</div>
</div>

<style>
	.no-underline {
		text-decoration: none;
	}

	.no-underline:hover {
		text-decoration: none;
	}
</style>
