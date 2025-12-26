<script lang="ts">
    import { onMount } from "svelte";
    import {
        Shield,
        Database,
        Search,
        RefreshCw,
        Terminal,
        ChevronRight,
        Check,
        AlertTriangle,
        Hash,
        Server,
        Clock,
        User,
        FileText,
        Copy,
        CheckCircle,
        XCircle,
    } from "lucide-svelte";
    import { getNetworkStats, getMerkleRoot } from "$lib/api";
    import { fade, slide } from "svelte/transition";

    // State
    let stats: any = null;
    let merkleRoot = "";
    let auditLogs: any[] = [];
    let isLoading = true;
    let activeTab = "ledger"; // ledger, verify-sig, verify-hash

    // Verification State
    let verifyOutput: Array<{
        type: "info" | "success" | "error" | "warning";
        message: string;
        detail?: string;
    }> = [];

    // Chain Verification
    let chainStatus: "idle" | "checking" | "secure" | "broken" = "idle";

    // Inputs
    let sigInput = { id: "", repId: "" };
    let hashInput = { id: "", text: "" };

    // Hash Verification Visual State
    let hashVerifying = false;
    let hashCurrentStep = 0;
    let hashResult: {
        valid: boolean;
        localHash: string;
        blockchainHash: string;
        error?: boolean;
        message?: string;
        manifesto?: any;
    } | null = null;

    // Signature Verification Visual State
    let sigVerifying = false;
    let sigCurrentStep = 0;
    let sigResult: {
        valid: boolean;
        hashMatches: boolean;
        signatureValid: boolean;
        computedHash: string;
        storedHash: string;
        signerAddress: string;
        recoveredSigner: string;
        representativeName: string;
        keyVersion: number;
        signedAt: string;
        blockchainConfirmed: boolean;
        error?: boolean;
        message?: string;
        legacy?: boolean;
    } | null = null;

    onMount(async () => {
        try {
            const [statsData, rootData, logsResponse] = await Promise.all([
                getNetworkStats(),
                getMerkleRoot(),
                fetch("http://localhost:8000/api/audit/logs?limit=50"),
            ]);

            stats = statsData;
            merkleRoot = rootData.merkle_root;

            if (logsResponse.ok) {
                const logsData = await logsResponse.json();
                auditLogs = logsData.logs || [];
            }

            // Auto-run chain check softly
            verifyChainDisplay();
        } catch (e) {
            console.error("Failed to load audit data:", e);
        } finally {
            isLoading = false;
        }
    });

    function formatTimestamp(ts: string): string {
        if (!ts) return "--:--";
        return new Date(ts).toLocaleString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
        });
    }

    // --- Logic ---

    async function verifyChainDisplay() {
        chainStatus = "checking";
        await new Promise((r) => setTimeout(r, 600)); // Visual delay

        let valid = true;
        for (let i = 0; i < auditLogs.length - 1; i++) {
            if (auditLogs[i].prev_hash !== auditLogs[i + 1].block_hash) {
                valid = false;
                break;
            }
        }
        chainStatus = valid ? "secure" : "broken";
    }

    async function verifySignature() {
        if (!sigInput.id || !sigInput.repId) return;

        sigVerifying = true;
        sigResult = null;
        sigCurrentStep = 1;

        try {
            // STEP 1: Fetch Manifesto
            const manRes = await fetch(
                `http://localhost:8000/api/manifestos/${sigInput.id}`,
            );
            if (!manRes.ok) throw new Error("Promise ID not found");
            const manifesto = await manRes.json();
            sigCurrentStep = 2;

            // Check Representative ID match
            if (
                String(manifesto.representative_id) !== String(sigInput.repId)
            ) {
                sigResult = {
                    valid: false,
                    hashMatches: false,
                    signatureValid: false,
                    computedHash: "",
                    storedHash: "",
                    signerAddress: "",
                    recoveredSigner: "",
                    representativeName: "",
                    keyVersion: 0,
                    signedAt: "",
                    blockchainConfirmed: false,
                    error: true,
                    message: `Promise #${sigInput.id} belongs to Rep ID ${manifesto.representative_id}, not ${sigInput.repId}.`,
                };
                sigVerifying = false;
                return;
            }

            await new Promise((r) => setTimeout(r, 400));

            // STEP 2: Call verification endpoint
            const res = await fetch(
                `http://localhost:8000/api/manifestos/${sigInput.id}/verify`,
            );
            const data = await res.json();
            sigCurrentStep = 3;

            await new Promise((r) => setTimeout(r, 400));

            // Check if legacy
            if (data.legacy_unverified) {
                sigResult = {
                    valid: false,
                    hashMatches: false,
                    signatureValid: false,
                    computedHash: "",
                    storedHash: "",
                    signerAddress: "",
                    recoveredSigner: "",
                    representativeName: data.representative_name || "",
                    keyVersion: 0,
                    signedAt: "",
                    blockchainConfirmed: false,
                    legacy: true,
                    message:
                        "This manifesto was created before the signature system.",
                };
                sigVerifying = false;
                return;
            }

            // Build result
            const results = data.verification_results || {};
            sigResult = {
                valid: data.verification_status === "AUTHENTIC",
                hashMatches: results.hash_matches === true,
                signatureValid: results.signature_valid === true,
                computedHash: data.computed_hash || "",
                storedHash: data.stored_hash || "",
                signerAddress:
                    data.representative_address || data.expected_signer || "",
                recoveredSigner: data.recovered_signer || "",
                representativeName: data.representative_name || "",
                keyVersion: data.key_version || 1,
                signedAt: data.signed_at || "",
                blockchainConfirmed: results.blockchain_recorded === true,
            };
        } catch (e: any) {
            sigResult = {
                valid: false,
                hashMatches: false,
                signatureValid: false,
                computedHash: "",
                storedHash: "",
                signerAddress: "",
                recoveredSigner: "",
                representativeName: "",
                keyVersion: 0,
                signedAt: "",
                blockchainConfirmed: false,
                error: true,
                message: e.message || "Verification failed",
            };
        } finally {
            sigVerifying = false;
        }
    }

    function resetSigVerification() {
        sigResult = null;
        sigCurrentStep = 0;
        sigInput = { id: "", repId: "" };
    }

    /**
     * STEP 1: Local Hash Computation (CRITICAL - happens in browser)
     * This is the most important part - the backend NEVER touches this value.
     * Even if the backend is malicious, this verification still works.
     */
    async function computeLocalHash(text: string): Promise<string> {
        const encoder = new TextEncoder();
        const data = encoder.encode(text);
        const hashBuffer = await crypto.subtle.digest("SHA-256", data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray
            .map((b) => b.toString(16).padStart(2, "0"))
            .join("");
        return "0x" + hashHex; // Full 64-char SHA256 hash (no truncation!)
    }

    /**
     * STEP 2: Fetch Blockchain Hash
     * Backend acts only as RPC proxy - not as authority.
     */
    async function fetchBlockchainHash(
        manifestoId: string,
    ): Promise<{ hash: string; manifesto: any }> {
        const response = await fetch(
            `http://localhost:8000/api/manifestos/${manifestoId}`,
        );
        if (!response.ok) {
            throw new Error("Failed to fetch blockchain hash");
        }
        const data = await response.json();
        return { hash: data.hash, manifesto: data };
    }

    async function verifyHash() {
        if (!hashInput.id || !hashInput.text) return;

        hashVerifying = true;
        hashResult = null;
        hashCurrentStep = 1;

        try {
            // STEP 1: Compute local hash (in browser - trustless)
            const localHash = await computeLocalHash(hashInput.text);
            hashCurrentStep = 2;

            await new Promise((r) => setTimeout(r, 400)); // Visual delay for UX

            // STEP 2: Fetch blockchain hash
            const blockchainData = await fetchBlockchainHash(hashInput.id);
            const blockchainHash = blockchainData.hash;
            hashCurrentStep = 3;

            await new Promise((r) => setTimeout(r, 400)); // Visual delay

            // STEP 3: Compare hashes
            const isValid = localHash === blockchainHash;

            hashResult = {
                valid: isValid,
                localHash,
                blockchainHash,
                manifesto: blockchainData.manifesto,
            };
        } catch (e: any) {
            hashResult = {
                valid: false,
                localHash: "",
                blockchainHash: "",
                error: true,
                message: e.message || "Verification failed",
            };
        } finally {
            hashVerifying = false;
        }
    }

    function copyHash(hash: string) {
        navigator.clipboard.writeText(hash);
    }

    function resetHashVerification() {
        hashResult = null;
        hashCurrentStep = 0;
        hashInput = { id: "", text: "" };
    }

    function addToConsole(
        type: "info" | "success" | "error" | "warning",
        message: string,
        detail?: string,
    ) {
        verifyOutput = [...verifyOutput, { type, message, detail }];
        // Keep last 12 messages for full verification display
        if (verifyOutput.length > 12) verifyOutput = verifyOutput.slice(-12);
    }

    function clearConsole() {
        verifyOutput = [];
    }
</script>

<svelte:head>
    <title>System Audit - WaachaPatra</title>
</svelte:head>

<main class="audit-system">
    <div class="container">
        <!-- Header: Minimal & Technical -->
        <header class="sys-header">
            <div class="sys-title">
                <Terminal class="icon" />
                <h1>System Audit Log</h1>
            </div>
            <div class="sys-status">
                <div class="metric">
                    <span class="label">Network Status</span>
                    <span class="value online"
                        ><span class="dot"></span> Active</span
                    >
                </div>
                <div class="metric">
                    <span class="label">Merkle Root</span>
                    <code class="mono-badge"
                        >{merkleRoot
                            ? merkleRoot.slice(0, 10) +
                              "..." +
                              merkleRoot.slice(-8)
                            : "SYNCING..."}</code
                    >
                </div>
                <div class="metric">
                    <span class="label">Chain Health</span>
                    {#if chainStatus === "checking"}
                        <span class="value warning">Scanning...</span>
                    {:else if chainStatus === "secure"}
                        <span class="value success"
                            ><Check class="icon-xs" /> Secure</span
                        >
                    {:else}
                        <span class="value error">Compromised</span>
                    {/if}
                </div>
            </div>
        </header>

        <div class="sys-grid">
            <!-- Left: The Ledger (Data Heavy, Minimal UI) -->
            <section class="sys-panel ledger-panel">
                <div class="panel-header">
                    <h2><Database class="icon-sm" /> Immutable Ledger</h2>
                    <span class="count">{auditLogs.length} Records</span>
                </div>

                <div class="table-container">
                    <table class="sys-table">
                        <thead>
                            <tr>
                                <th>Block</th>
                                <th>Timestamp</th>
                                <th>Action</th>
                                <th>Hash (Linked)</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#if isLoading}
                                <tr
                                    ><td colspan="5" class="loading-cell"
                                        >Initializing Ledger...</td
                                    ></tr
                                >
                            {:else if auditLogs.length === 0}
                                <tr
                                    ><td colspan="5" class="empty-cell"
                                        >No records found</td
                                    ></tr
                                >
                            {:else}
                                {#each auditLogs as log}
                                    <tr class="log-row">
                                        <td class="mono">#{log.block_number}</td
                                        >
                                        <td class="mono-dim"
                                            >{formatTimestamp(
                                                log.timestamp,
                                            )}</td
                                        >
                                        <td class="action-cell">
                                            <span
                                                class="action-badge {log.action.toLowerCase()}"
                                            >
                                                {log.action.includes("PROMISE")
                                                    ? "PROMISE"
                                                    : "EVENT"}
                                            </span>
                                            <span class="action-detail">
                                                {log.manifesto?.title ||
                                                    log.data?.title ||
                                                    log.action}
                                            </span>
                                        </td>
                                        <td class="hash-cell">
                                            <div class="hash-link">
                                                <span
                                                    class="hash-val"
                                                    title={log.block_hash}
                                                    >{log.block_hash.slice(
                                                        0,
                                                        10,
                                                    )}...</span
                                                >
                                                {#if log.prev_hash !== "0x0000000000000000000000000000000000000000000000000000000000000000"}
                                                    <span
                                                        class="link-icon"
                                                        title="Linked to previous"
                                                        >🔗</span
                                                    >
                                                {/if}
                                            </div>
                                        </td>
                                        <td>
                                            {#if log.manifesto?.blockchain_confirmed}
                                                <span
                                                    class="status-dot success"
                                                    title="Confirmed On-Chain"
                                                ></span>
                                            {:else}
                                                <span
                                                    class="status-dot pending"
                                                    title="Pending"
                                                ></span>
                                            {/if}
                                        </td>
                                    </tr>
                                {/each}
                            {/if}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Right: Verification Terminal -->
            <aside class="sys-panel tools-panel">
                <div class="panel-header">
                    <h2><Shield class="icon-sm" /> Verification Console</h2>
                </div>

                <div class="console-wrapper">
                    <!-- Tools Interface -->
                    <div class="tools-tabs">
                        <button
                            class="tool-tab"
                            class:active={activeTab === "ledger"}
                            on:click={() => (activeTab = "ledger")}
                        >
                            Chain Check
                        </button>
                        <button
                            class="tool-tab"
                            class:active={activeTab === "verify-sig"}
                            on:click={() => (activeTab = "verify-sig")}
                        >
                            Sig Verify
                        </button>
                        <button
                            class="tool-tab"
                            class:active={activeTab === "verify-hash"}
                            on:click={() => (activeTab = "verify-hash")}
                        >
                            Data Hash
                        </button>
                    </div>

                    <div class="tool-input-area">
                        {#if activeTab === "ledger"}
                            <div class="tool-description">
                                Validates the cryptographic integrity of the
                                entire blockchain history.
                            </div>
                            <button
                                class="sys-btn full"
                                on:click={() => {
                                    clearConsole();
                                    addToConsole(
                                        "info",
                                        "Running full ledger scan...",
                                    );
                                    verifyChainDisplay().then(() =>
                                        addToConsole(
                                            chainStatus === "secure"
                                                ? "success"
                                                : "error",
                                            `Scan Complete: Status ${chainStatus.toUpperCase()}`,
                                        ),
                                    );
                                }}
                            >
                                <RefreshCw class="icon-xs" /> Run Integrity Scan
                            </button>
                        {:else if activeTab === "verify-sig"}
                            {#if !sigResult}
                                <!-- Input Form -->
                                <div class="hash-steps-indicator">
                                    <div
                                        class="step-item"
                                        class:active={sigCurrentStep >= 1}
                                        class:complete={sigCurrentStep > 1}
                                    >
                                        <span class="step-num">1</span>
                                        <span class="step-label">Fetch</span>
                                    </div>
                                    <span class="step-arrow">→</span>
                                    <div
                                        class="step-item"
                                        class:active={sigCurrentStep >= 2}
                                        class:complete={sigCurrentStep > 2}
                                    >
                                        <span class="step-num">2</span>
                                        <span class="step-label">Verify</span>
                                    </div>
                                    <span class="step-arrow">→</span>
                                    <div
                                        class="step-item"
                                        class:active={sigCurrentStep >= 3}
                                    >
                                        <span class="step-num">3</span>
                                        <span class="step-label">Result</span>
                                    </div>
                                </div>
                                <div class="input-group">
                                    <label for="sig-rep-id"
                                        >Representative ID</label
                                    >
                                    <input
                                        id="sig-rep-id"
                                        type="number"
                                        bind:value={sigInput.repId}
                                        placeholder="e.g. 1"
                                        class="sys-input"
                                    />
                                </div>
                                <div class="input-group">
                                    <label for="sig-promise-id"
                                        >Promise ID</label
                                    >
                                    <input
                                        id="sig-promise-id"
                                        type="number"
                                        bind:value={sigInput.id}
                                        placeholder="e.g. 1"
                                        class="sys-input"
                                    />
                                </div>
                                <button
                                    class="sys-btn full"
                                    on:click={verifySignature}
                                    disabled={sigVerifying ||
                                        !sigInput.id ||
                                        !sigInput.repId}
                                >
                                    {#if sigVerifying}
                                        <RefreshCw class="icon-xs spin" /> Verifying...
                                    {:else}
                                        <Shield class="icon-xs" /> Verify Signature
                                    {/if}
                                </button>
                            {:else}
                                <!-- Visual Result Display -->
                                <div
                                    class="sig-result"
                                    class:valid={sigResult.valid}
                                    class:invalid={!sigResult.valid &&
                                        !sigResult.error &&
                                        !sigResult.legacy}
                                    class:error={sigResult.error}
                                    class:legacy={sigResult.legacy}
                                >
                                    {#if sigResult.error}
                                        <div class="result-header error">
                                            <XCircle size={28} />
                                            <div>
                                                <h4>Verification Error</h4>
                                                <p>{sigResult.message}</p>
                                            </div>
                                        </div>
                                    {:else if sigResult.legacy}
                                        <div class="result-header legacy">
                                            <AlertTriangle size={28} />
                                            <div>
                                                <h4>LEGACY</h4>
                                                <p>{sigResult.message}</p>
                                            </div>
                                        </div>
                                    {:else if sigResult.valid}
                                        <div class="result-header valid">
                                            <CheckCircle size={28} />
                                            <div>
                                                <h4>SIGNATURE VALID</h4>
                                                <p>
                                                    Signed by {sigResult.representativeName}
                                                </p>
                                            </div>
                                        </div>
                                    {:else}
                                        <div class="result-header invalid">
                                            <XCircle size={28} />
                                            <div>
                                                <h4>INVALID</h4>
                                                <p>
                                                    Signature verification
                                                    failed
                                                </p>
                                            </div>
                                        </div>
                                    {/if}

                                    {#if !sigResult.error && !sigResult.legacy}
                                        <!-- Verification Details -->
                                        <div class="sig-details">
                                            <div class="detail-row">
                                                <span class="detail-icon"
                                                    ><User size={16} /></span
                                                >
                                                <div class="detail-content">
                                                    <span class="detail-label"
                                                        >Signer</span
                                                    >
                                                    <code
                                                        class="detail-value"
                                                        title={sigResult.signerAddress}
                                                    >
                                                        {sigResult.signerAddress.slice(
                                                            0,
                                                            10,
                                                        )}...{sigResult.signerAddress.slice(
                                                            -6,
                                                        )}
                                                    </code>
                                                </div>
                                                <span
                                                    class="check-badge"
                                                    class:valid={sigResult.signatureValid}
                                                >
                                                    {sigResult.signatureValid
                                                        ? "✓"
                                                        : "✗"}
                                                </span>
                                            </div>

                                            <div class="detail-row">
                                                <span class="detail-icon"
                                                    ><Hash size={16} /></span
                                                >
                                                <div class="detail-content">
                                                    <span class="detail-label"
                                                        >Hash Match</span
                                                    >
                                                    <code
                                                        class="detail-value"
                                                        title={sigResult.storedHash}
                                                    >
                                                        {sigResult.storedHash.slice(
                                                            0,
                                                            14,
                                                        )}...
                                                    </code>
                                                </div>
                                                <span
                                                    class="check-badge"
                                                    class:valid={sigResult.hashMatches}
                                                >
                                                    {sigResult.hashMatches
                                                        ? "✓"
                                                        : "✗"}
                                                </span>
                                            </div>

                                            <div class="detail-row">
                                                <span class="detail-icon"
                                                    ><Shield size={16} /></span
                                                >
                                                <div class="detail-content">
                                                    <span class="detail-label"
                                                        >Key Version</span
                                                    >
                                                    <span class="detail-value"
                                                        >v{sigResult.keyVersion}</span
                                                    >
                                                </div>
                                            </div>

                                            {#if sigResult.signedAt}
                                                <div class="detail-row">
                                                    <span class="detail-icon"
                                                        ><Clock
                                                            size={16}
                                                        /></span
                                                    >
                                                    <div class="detail-content">
                                                        <span
                                                            class="detail-label"
                                                            >Signed At</span
                                                        >
                                                        <span
                                                            class="detail-value"
                                                            >{new Date(
                                                                sigResult.signedAt,
                                                            ).toLocaleString()}</span
                                                        >
                                                    </div>
                                                </div>
                                            {/if}

                                            {#if sigResult.blockchainConfirmed}
                                                <div
                                                    class="detail-row blockchain-badge"
                                                >
                                                    <span class="detail-icon"
                                                        ><Database
                                                            size={16}
                                                        /></span
                                                    >
                                                    <span class="detail-value"
                                                        >Recorded on Blockchain</span
                                                    >
                                                </div>
                                            {/if}
                                        </div>
                                    {/if}
                                </div>
                                <button
                                    class="sys-btn full secondary"
                                    on:click={resetSigVerification}
                                >
                                    Verify Another
                                </button>
                            {/if}
                        {:else if activeTab === "verify-hash"}
                            {#if !hashResult}
                                <!-- Input Form -->
                                <div class="hash-steps-indicator">
                                    <div
                                        class="step-item"
                                        class:active={hashCurrentStep >= 1}
                                        class:complete={hashCurrentStep > 1}
                                    >
                                        <span class="step-num">1</span>
                                        <span class="step-label"
                                            >Local Hash</span
                                        >
                                    </div>
                                    <span class="step-arrow">→</span>
                                    <div
                                        class="step-item"
                                        class:active={hashCurrentStep >= 2}
                                        class:complete={hashCurrentStep > 2}
                                    >
                                        <span class="step-num">2</span>
                                        <span class="step-label"
                                            >Blockchain</span
                                        >
                                    </div>
                                    <span class="step-arrow">→</span>
                                    <div
                                        class="step-item"
                                        class:active={hashCurrentStep >= 3}
                                    >
                                        <span class="step-num">3</span>
                                        <span class="step-label">Compare</span>
                                    </div>
                                </div>
                                <div class="input-group">
                                    <label for="hash-promise-id"
                                        >Promise ID</label
                                    >
                                    <input
                                        id="hash-promise-id"
                                        type="number"
                                        bind:value={hashInput.id}
                                        placeholder="e.g. 1"
                                        class="sys-input"
                                    />
                                </div>
                                <div class="input-group">
                                    <label for="hash-text">Original Text</label>
                                    <textarea
                                        id="hash-text"
                                        bind:value={hashInput.text}
                                        rows="3"
                                        class="sys-input"
                                        placeholder="Paste exact manifesto content here..."
                                    ></textarea>
                                    <span class="char-count"
                                        >{hashInput.text.length} characters</span
                                    >
                                </div>
                                <button
                                    class="sys-btn full"
                                    on:click={verifyHash}
                                    disabled={hashVerifying ||
                                        !hashInput.id ||
                                        !hashInput.text}
                                >
                                    {#if hashVerifying}
                                        <RefreshCw class="icon-xs spin" /> Verifying...
                                    {:else}
                                        <Search class="icon-xs" /> Verify Authenticity
                                    {/if}
                                </button>
                            {:else}
                                <!-- Visual Result Display -->
                                <div
                                    class="hash-result"
                                    class:valid={hashResult.valid}
                                    class:invalid={!hashResult.valid &&
                                        !hashResult.error}
                                    class:error={hashResult.error}
                                >
                                    {#if hashResult.error}
                                        <div class="result-header error">
                                            <AlertTriangle size={28} />
                                            <div>
                                                <h4>Verification Error</h4>
                                                <p>{hashResult.message}</p>
                                            </div>
                                        </div>
                                    {:else if hashResult.valid}
                                        <div class="result-header valid">
                                            <CheckCircle size={28} />
                                            <div>
                                                <h4>AUTHENTIC</h4>
                                                <p>
                                                    Content matches blockchain
                                                    record
                                                </p>
                                            </div>
                                        </div>
                                    {:else}
                                        <div class="result-header invalid">
                                            <XCircle size={28} />
                                            <div>
                                                <h4>TAMPERED</h4>
                                                <p>Hashes do NOT match</p>
                                            </div>
                                        </div>
                                    {/if}

                                    {#if !hashResult.error}
                                        <div class="hash-comparison">
                                            <div class="hash-box">
                                                <div class="hash-label">
                                                    Your Local Hash
                                                </div>
                                                <div class="hash-value">
                                                    <code
                                                        title={hashResult.localHash}
                                                        >{hashResult.localHash.slice(
                                                            0,
                                                            18,
                                                        )}...{hashResult.localHash.slice(
                                                            -6,
                                                        )}</code
                                                    >
                                                    <button
                                                        class="copy-btn"
                                                        on:click={() =>
                                                            copyHash(
                                                                hashResult.localHash,
                                                            )}
                                                        title="Copy"
                                                    >
                                                        <Copy size={12} />
                                                    </button>
                                                </div>
                                            </div>
                                            <div
                                                class="comparison-symbol"
                                                class:match={hashResult.valid}
                                            >
                                                {hashResult.valid ? "=" : "≠"}
                                            </div>
                                            <div class="hash-box">
                                                <div class="hash-label">
                                                    Blockchain Hash
                                                </div>
                                                <div class="hash-value">
                                                    <code
                                                        title={hashResult.blockchainHash}
                                                        >{hashResult.blockchainHash.slice(
                                                            0,
                                                            18,
                                                        )}...{hashResult.blockchainHash.slice(
                                                            -6,
                                                        )}</code
                                                    >
                                                    <button
                                                        class="copy-btn"
                                                        on:click={() =>
                                                            copyHash(
                                                                hashResult.blockchainHash,
                                                            )}
                                                        title="Copy"
                                                    >
                                                        <Copy size={12} />
                                                    </button>
                                                </div>
                                            </div>
                                        </div>

                                        {#if hashResult.manifesto}
                                            <div class="blockchain-info">
                                                <div class="info-row">
                                                    <span class="info-label"
                                                        >Block</span
                                                    >
                                                    <span class="info-value"
                                                        >#{hashResult.manifesto
                                                            .block_number ||
                                                            "N/A"}</span
                                                    >
                                                </div>
                                                <div class="info-row">
                                                    <span class="info-label"
                                                        >Chain</span
                                                    >
                                                    <span class="info-value"
                                                        >{hashResult.manifesto
                                                            .chain_name ||
                                                            "Local"}</span
                                                    >
                                                </div>
                                            </div>
                                        {/if}
                                    {/if}
                                </div>
                                <button
                                    class="sys-btn full secondary"
                                    on:click={resetHashVerification}
                                >
                                    Verify Another
                                </button>
                            {/if}
                        {/if}
                    </div>
                </div>
            </aside>
        </div>
    </div>
</main>

<style>
    :global(:root) {
        --sys-bg: #f8fafc;
        --sys-panel: #ffffff;
        --sys-border: #e2e8f0;
        --sys-text: #334155;
        --sys-text-dim: #94a3b8;
        --sys-primary: #0f172a;
        --sys-accent: #2563eb;
        --sys-mono: "JetBrains Mono", "Fira Code", "Roboto Mono", monospace;
    }

    .audit-system {
        background: var(--sys-bg);
        min-height: 100vh;
        padding: 2rem 0;
        font-family: "Inter", sans-serif;
        color: var(--sys-text);
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }

    /* Header */
    .sys-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--sys-border);
    }

    .sys-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .sys-title h1 {
        font-family: var(--sys-mono);
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        color: var(--sys-primary);
        margin: 0;
    }

    .sys-title .icon {
        width: 2rem;
        height: 2rem;
        color: var(--sys-accent);
    }

    .sys-status {
        display: flex;
        gap: 2rem;
    }

    .metric {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }

    .metric .label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--sys-text-dim);
        margin-bottom: 0.25rem;
    }

    .metric .value {
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    .value.online {
        color: #10b981;
    }
    .value.warning {
        color: #f59e0b;
    }
    .value.error {
        color: #ef4444;
    }

    .dot {
        width: 6px;
        height: 6px;
        background: currentColor;
        border-radius: 50%;
        box-shadow: 0 0 8px currentColor;
    }

    .mono-badge {
        font-family: var(--sys-mono);
        background: #e2e8f0;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8rem;
        color: var(--sys-primary);
    }

    /* Grid Layout */
    .sys-grid {
        display: grid;
        grid-template-columns: 1fr 450px;
        gap: 1.5rem;
        align-items: start;
    }

    @media (max-width: 900px) {
        .sys-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Panels */
    .sys-panel {
        background: var(--sys-panel);
        border: 1px solid var(--sys-border);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }

    .panel-header {
        background: #f1f5f9;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--sys-border);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .panel-header h2 {
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--sys-primary);
    }

    .count {
        font-size: 0.75rem;
        font-family: var(--sys-mono);
        background: white;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid var(--sys-border);
    }

    /* Table */
    .table-container {
        overflow-x: auto;
    }

    .sys-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }

    .sys-table th {
        text-align: left;
        padding: 0.75rem 1rem;
        border-bottom: 2px solid var(--sys-border);
        color: var(--sys-text-dim);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
    }

    .sys-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--sys-border);
        vertical-align: middle;
    }

    .log-row:last-child td {
        border-bottom: none;
    }
    .log-row:hover {
        background: #f8fafc;
    }

    .mono {
        font-family: var(--sys-mono);
        color: var(--sys-primary);
    }
    .mono-dim {
        font-family: var(--sys-mono);
        color: var(--sys-text-dim);
        font-size: 0.75rem;
    }

    .action-badge {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 2px;
        margin-right: 0.5rem;
        text-transform: uppercase;
    }

    .action-badge.promise {
        background: #dbeafe;
        color: #1e40af;
    }
    .action-badge.event {
        background: #f3f4f6;
        color: #374151;
    }

    .action-detail {
        font-weight: 500;
        color: var(--sys-primary);
    }

    .hash-cell {
        font-family: var(--sys-mono);
        font-size: 0.75rem;
    }

    .hash-link {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--sys-accent);
    }

    .link-icon {
        font-size: 0.7rem;
        opacity: 0.5;
    }

    .status-dot {
        display: block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .status-dot.success {
        background: #10b981;
    }
    .status-dot.pending {
        background: #fbbf24;
    }

    /* Verification Console */
    .tools-panel {
        display: flex;
        flex-direction: column;
        height: fit-content;
    }

    .console-screen {
        background: #1e293b; /* Dark terminal */
        color: #33ff00; /* Retro terminal green text */
        font-family: var(--sys-mono);
        font-size: 0.9rem;
        padding: 1.25rem;
        height: 380px;
        overflow-y: auto;
        border-bottom: 1px solid var(--sys-border);
    }

    .console-line {
        margin-bottom: 0.5rem;
        line-height: 1.4;
        word-break: break-all;
    }
    .console-line .prompt {
        color: #64748b;
        margin-right: 0.5rem;
    }

    .console-line.info {
        color: #e2e8f0;
    }
    .console-line.success {
        color: #4ade80;
    }
    .console-line.error {
        color: #f87171;
    }

    .console-detail {
        margin-top: 0.25rem;
        color: #94a3b8;
        padding-left: 1rem;
        font-size: 0.75rem;
    }

    .tools-tabs {
        display: flex;
        background: #f1f5f9;
        border-bottom: 1px solid var(--sys-border);
    }

    .tool-tab {
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--sys-text-dim);
        background: transparent;
        border: none;
        cursor: pointer;
        border-bottom: 2px solid transparent;
    }

    .tool-tab.active {
        color: var(--sys-accent);
        background: white;
        border-bottom-color: var(--sys-accent);
    }

    .tool-input-area {
        padding: 1.5rem;
        background: white;
    }

    .input-group {
        margin-bottom: 1rem;
    }

    .input-group label {
        display: block;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--sys-text);
        margin-bottom: 0.35rem;
    }

    .sys-input {
        width: 100%;
        padding: 0.5rem;
        background: #f8fafc;
        border: 1px solid var(--sys-border);
        border-radius: 4px;
        font-family: var(--sys-mono);
        font-size: 0.85rem;
        color: var(--sys-primary);
    }

    .sys-input:focus {
        outline: none;
        border-color: var(--sys-accent);
        background: white;
    }

    .sys-btn {
        padding: 0.6rem 1rem;
        background: var(--sys-primary);
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .sys-btn:hover {
        background: #334155;
    }
    .sys-btn:disabled {
        background: #cbd5e1;
        cursor: not-allowed;
    }
    .sys-btn.full {
        width: 100%;
    }

    .tool-description {
        font-size: 0.85rem;
        color: var(--sys-text-dim);
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    .icon-xs {
        width: 14px;
        height: 14px;
    }
    .icon-sm {
        width: 16px;
        height: 16px;
    }

    /* Hash Verification Visual UI */
    .hash-steps-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 1.25rem;
        padding: 0.75rem;
        background: #f1f5f9;
        border-radius: 8px;
    }

    .hash-steps-indicator .step-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.6rem;
        border-radius: 6px;
        opacity: 0.4;
        transition: all 0.3s;
    }

    .hash-steps-indicator .step-item.active {
        opacity: 1;
        background: rgba(37, 99, 235, 0.15);
    }

    .hash-steps-indicator .step-item.complete {
        opacity: 1;
        background: rgba(16, 185, 129, 0.15);
    }

    .hash-steps-indicator .step-num {
        width: 20px;
        height: 20px;
        background: var(--sys-accent);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
    }

    .hash-steps-indicator .step-item.complete .step-num {
        background: #10b981;
    }

    .hash-steps-indicator .step-label {
        font-size: 0.7rem;
        color: var(--sys-text);
        font-weight: 500;
    }

    .hash-steps-indicator .step-arrow {
        color: var(--sys-text-dim);
        font-size: 0.9rem;
    }

    .char-count {
        display: block;
        text-align: right;
        font-size: 0.7rem;
        color: var(--sys-text-dim);
        margin-top: 0.25rem;
    }

    /* Hash Result Display */
    .hash-result {
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
        border: 1px solid var(--sys-border);
    }

    .hash-result.valid {
        border-color: #10b981;
    }

    .hash-result.invalid {
        border-color: #ef4444;
    }

    .hash-result.error {
        border-color: #f59e0b;
    }

    .result-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
    }

    .result-header.valid {
        background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.15),
            rgba(16, 185, 129, 0.05)
        );
        color: #10b981;
    }

    .result-header.invalid {
        background: linear-gradient(
            135deg,
            rgba(239, 68, 68, 0.15),
            rgba(239, 68, 68, 0.05)
        );
        color: #ef4444;
    }

    .result-header.error {
        background: linear-gradient(
            135deg,
            rgba(245, 158, 11, 0.15),
            rgba(245, 158, 11, 0.05)
        );
        color: #f59e0b;
    }

    .result-header h4 {
        margin: 0;
        font-size: 1rem;
        font-weight: 700;
    }

    .result-header p {
        margin: 0.15rem 0 0;
        font-size: 0.8rem;
        opacity: 0.85;
    }

    /* Hash Comparison */
    .hash-comparison {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: #f8fafc;
    }

    .hash-box {
        width: 100%;
        background: white;
        border-radius: 8px;
        border: 1px solid var(--sys-border);
        padding: 0.75rem;
    }

    .hash-label {
        font-size: 0.75rem;
        color: var(--sys-text-dim);
        margin-bottom: 0.35rem;
        font-weight: 500;
    }

    .hash-value {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: #f1f5f9;
        padding: 0.5rem;
        border-radius: 4px;
    }

    .hash-value code {
        flex: 1;
        font-family: var(--sys-mono);
        font-size: 0.75rem;
        color: var(--sys-primary);
        word-break: break-all;
    }

    .copy-btn {
        background: var(--sys-border);
        border: none;
        border-radius: 4px;
        padding: 0.35rem;
        cursor: pointer;
        color: var(--sys-text-dim);
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .copy-btn:hover {
        background: #cbd5e1;
        color: var(--sys-primary);
    }

    .comparison-symbol {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ef4444;
        padding: 0.25rem;
    }

    .comparison-symbol.match {
        color: #10b981;
    }

    /* Blockchain Info */
    .blockchain-info {
        display: flex;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background: white;
        border-top: 1px solid var(--sys-border);
    }

    .info-row {
        display: flex;
        gap: 0.35rem;
        align-items: center;
    }

    .info-label {
        font-size: 0.7rem;
        color: var(--sys-text-dim);
        font-weight: 500;
    }

    .info-value {
        font-size: 0.75rem;
        color: var(--sys-primary);
        font-family: var(--sys-mono);
    }

    .sys-btn.secondary {
        background: #e2e8f0;
        color: var(--sys-primary);
    }

    .sys-btn.secondary:hover {
        background: #cbd5e1;
    }

    /* Spin animation */
    :global(.spin) {
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    /* Signature Verification Visual UI */
    .sig-result {
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
        border: 1px solid var(--sys-border);
    }

    .sig-result.valid {
        border-color: #10b981;
    }

    .sig-result.invalid {
        border-color: #ef4444;
    }

    .sig-result.error {
        border-color: #f59e0b;
    }

    .sig-result.legacy {
        border-color: #6b7280;
    }

    .result-header.legacy {
        background: linear-gradient(
            135deg,
            rgba(107, 114, 128, 0.15),
            rgba(107, 114, 128, 0.05)
        );
        color: #6b7280;
    }

    .sig-details {
        padding: 1rem;
        background: #f8fafc;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .detail-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0.75rem;
        background: white;
        border-radius: 6px;
        border: 1px solid var(--sys-border);
    }

    .detail-icon {
        font-size: 1rem;
    }

    .detail-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .detail-label {
        font-size: 0.7rem;
        color: var(--sys-text-dim);
        font-weight: 500;
    }

    .detail-value {
        font-size: 0.8rem;
        color: var(--sys-primary);
        font-family: var(--sys-mono);
    }

    .check-badge {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        background: #fecaca;
        color: #ef4444;
    }

    .check-badge.valid {
        background: #d1fae5;
        color: #10b981;
    }

    .detail-row.blockchain-badge {
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.1),
            rgba(99, 102, 241, 0.05)
        );
        border-color: #6366f1;
        color: #6366f1;
        justify-content: center;
        gap: 0.5rem;
    }

    .detail-row.blockchain-badge .detail-value {
        color: #6366f1;
        font-weight: 600;
    }
</style>
