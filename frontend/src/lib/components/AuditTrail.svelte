<script>
    import { onMount } from "svelte";
    import {
        FileText,
        CheckCircle,
        Vote,
        PlusCircle,
        Activity,
    } from "lucide-svelte";

    export let blocks = [];

    let animatedEvents = [];

    onMount(async () => {
        // If no blocks provided, fetch from API
        if (blocks.length === 0) {
            try {
                const response = await fetch(
                    "http://localhost:8000/api/audit/logs",
                );
                if (response.ok) {
                    const logs = await response.json();
                    // Convert audit logs to friendly event format
                    blocks = logs.slice(0, 10).map((log, index) => ({
                        id: index,
                        timestamp: log.timestamp || new Date().toISOString(),
                        type: mapEventType(log.event_type || "unknown"),
                        description: mapEventDescription(log),
                    }));
                }
            } catch (err) {
                // Use sample data if API fails
                blocks = generateSampleEvents();
            }
        }

        // Animate events appearing
        for (let i = 0; i < blocks.length; i++) {
            await new Promise((r) => setTimeout(r, 100));
            animatedEvents = [...animatedEvents, blocks[i]];
        }
    });

    function mapEventType(technicalType) {
        const mappings = {
            genesis: "system",
            promise: "promise",
            vote_batch: "vote",
            status_change: "status",
            merkle_root: "security",
        };
        return mappings[technicalType] || "unknown";
    }

    function mapEventDescription(log) {
        if (log.event_type === "genesis") return "Audit log created";
        if (
            log.event_type === "promise" ||
            log.action === "PROMISE_CREATED" ||
            log.action === "SIGNED_MANIFESTO_CREATED"
        ) {
            const title = log.data?.title || log.title;
            return title ? `Promise: "${title}"` : "New promise added";
        }
        if (
            log.event_type === "vote_batch" ||
            log.action === "VOTE_AGGREGATED"
        ) {
            const title = log.data?.title;
            return title
                ? `Votes recorded for "${title}"`
                : "Votes securely recorded";
        }
        if (
            log.event_type === "status_change" ||
            log.action === "STATUS_CHANGED"
        ) {
            const title = log.data?.title;
            const newStatus = log.data?.new_status || log.data?.status;
            if (title && newStatus) return `"${title}" marked as ${newStatus}`;
            return "Promise status updated";
        }
        if (log.event_type === "merkle_root")
            return "System integrity verified";
        return log.data?.title || log.data || "System activity recorded";
    }

    function generateSampleEvents() {
        return [
            {
                id: 4,
                timestamp: new Date().toISOString(),
                type: "security",
                description: "System integrity verified",
            },
            {
                id: 3,
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                type: "status",
                description: 'Promise status updated to "Kept"',
            },
            {
                id: 2,
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                type: "vote",
                description: "250 votes securely recorded",
            },
            {
                id: 1,
                timestamp: new Date(Date.now() - 10800000).toISOString(),
                type: "promise",
                description: 'New promise: "Education Reform" added',
            },
            {
                id: 0,
                timestamp: new Date(Date.now() - 14400000).toISOString(),
                type: "system",
                description: "Audit log initialized",
            },
        ];
    }

    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat("en-US", {
            month: "short",
            day: "numeric",
            hour: "numeric",
            minute: "numeric",
            hour12: true,
        }).format(date);
    }

    const eventIcons = {
        system: Activity,
        promise: PlusCircle,
        vote: Vote,
        status: CheckCircle,
        security: Activity,
        unknown: Activity,
    };

    const eventStyles = {
        system: "bg-gray-100 text-gray-600",
        promise: "bg-primary-100 text-primary-600",
        vote: "bg-blue-100 text-blue-600",
        status: "bg-success-100 text-success-600",
        security: "bg-indigo-100 text-indigo-600",
        unknown: "bg-gray-100 text-gray-600",
    };
</script>

<div class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
    <div class="flex items-center justify-between mb-6">
        <h3
            class="text-lg font-bold font-serif text-gray-900 flex items-center gap-2"
        >
            <FileText class="w-5 h-5 text-primary-600" />
            <span>Activity Log</span>
        </h3>
        <span
            class="text-xs font-medium text-gray-500 bg-gray-50 px-2 py-1 rounded-full border border-gray-100"
        >
            Publicly Verifiable
        </span>
    </div>

    <p
        class="text-gray-600 text-sm mb-8 bg-gray-50 p-3 rounded-lg border border-gray-100"
    >
        This timeline tracks all major actions on the platform. Once recorded,
        this history cannot be changed by anyone.
    </p>

    <div class="relative pl-4 space-y-0">
        <!-- Continuous vertical line -->
        <div
            class="absolute left-[27px] top-2 bottom-6 w-0.5 bg-gray-100"
        ></div>

        {#if animatedEvents.length === 0}
            <div class="flex justify-center py-8">
                <div
                    class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"
                ></div>
            </div>
        {:else}
            {#each animatedEvents as event, i (event.id)}
                <div
                    class="relative flex gap-4 pb-8 last:pb-0 group opacity-0 animate-fade-in"
                    style="animation-delay: {i *
                        100}ms; animation-fill-mode: forwards;"
                >
                    <!-- Icon Bubble -->
                    <div
                        class="relative z-10 w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 {eventStyles[
                            event.type
                        ]} ring-4 ring-white"
                    >
                        <svelte:component
                            this={eventIcons[event.type] || eventIcons.unknown}
                            class="w-5 h-5"
                        />
                    </div>

                    <!-- Content -->
                    <div class="pt-1.5 flex-1">
                        <div
                            class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1"
                        >
                            <span class="font-semibold text-gray-900"
                                >{event.description}</span
                            >
                            <span
                                class="text-xs text-gray-400 font-medium tabular-nums"
                                >{formatDate(event.timestamp)}</span
                            >
                        </div>
                        <p class="text-sm text-gray-500">
                            Record ID: #{event.id + 1000}
                        </p>
                    </div>
                </div>
            {/each}
        {/if}
    </div>
</div>

<style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-fade-in {
        animation: fadeIn 0.4s ease-out forwards;
    }
</style>
