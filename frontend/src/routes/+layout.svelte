<script lang="ts">
  import "../app.css";
  import "$lib/polyfills"; // Import polyfills for ZK libraries
  import { onMount } from "svelte";
  import { authStore } from "$lib/stores";
  import { checkCredential } from "$lib/api";
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import { page } from "$app/stores";

  // Determine header variant based on current route
  $: headerVariant =
    $page.url.pathname === "/"
      ? "transparent"
      : $page.url.pathname.startsWith("/citizen")
        ? "citizen"
        : $page.url.pathname.startsWith("/representative")
          ? "politician"
          : "default";

  // Validate and sync auth state from backend on mount
  onMount(async () => {
    // Check if we have a stored credential
    const storedAuth = $authStore;

    if (storedAuth.isAuthenticated && storedAuth.credential?.nullifier) {
      try {
        // Validate credential with backend and sync voting history
        const result = await checkCredential(storedAuth.credential.nullifier);

        if (result.valid) {
          // Sync voting history from backend
          const backendVotes = result.used_votes.map(String);
          const currentVotes = storedAuth.credential.usedVotes || [];

          // Merge votes (backend is source of truth)
          const mergedVotes = [...new Set([...currentVotes, ...backendVotes])];

          // Update local votes storage for VoteBox
          const localVotes = JSON.parse(
            localStorage.getItem("user_votes") || "{}",
          );
          backendVotes.forEach((id: string) => {
            if (!localVotes[id]) {
              localVotes[id] = "kept"; // Default if type unknown
            }
          });
          localStorage.setItem("user_votes", JSON.stringify(localVotes));

          // Update auth store if votes changed or politician status updated
          if (
            mergedVotes.length !== currentVotes.length ||
            result.is_politician !== storedAuth.credential.isPolitician
          ) {
            authStore.setCredential({
              ...storedAuth.credential,
              usedVotes: mergedVotes,
              isPolitician: result.is_politician,
              politicianId: result.politician_id,
              politicianSlug: result.politician_slug,
            });
          }
        } else {
          // Credential no longer valid - log out
          console.warn("Stored credential is no longer valid, logging out");
          authStore.logout();
        }
      } catch (error) {
        // Backend unreachable - keep local state but don't block
        console.warn("Could not validate credential with backend:", error);
      }
    }
  });
</script>

<Header variant={headerVariant} />

<slot />

{#if !$authStore.isAuthenticated}
  <Footer />
{/if}
