<script>
    import { FileText, ChevronRight, Shield } from "lucide-svelte";

    export let representative = {
        id: 1,
        name: "Representative Name",
        title: "Member of Parliament",
        party: "Independent",
        image_url: "",
        integrity_score: 0,
        manifestos: 0,
        verified: false,
        slug: "",
    };

    function getScoreColor(score) {
        if (score >= 80) return "text-success-600";
        if (score >= 60) return "text-warning-600";
        return "text-error-600";
    }

    function getBarColor(score) {
        if (score >= 80) return "bg-success-500";
        if (score >= 60) return "bg-warning-500";
        return "bg-error-500";
    }

    function handleImageError(event) {
        event.target.style.display = "none";
        event.target.nextElementSibling.style.display = "flex";
    }
</script>

<a
    href="/representatives/{representative.slug || representative.id}"
    class="group relative flex flex-col bg-white rounded-xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 border border-gray-200 hover:border-primary-200 overflow-hidden"
>
    <div class="p-6 flex flex-col gap-4">
        <!-- Top Row: Avatar & Score -->
        <div class="flex justify-between items-start">
            <div class="relative w-14 h-14 flex-shrink-0">
                <div
                    class="w-full h-full rounded-full overflow-hidden border border-gray-100 bg-gray-50"
                >
                    {#if representative.image_url}
                        <img
                            src={representative.image_url}
                            alt={representative.name}
                            class="w-full h-full object-cover"
                            on:error={handleImageError}
                        />
                        <div
                            class="hidden w-full h-full items-center justify-center bg-primary-100 text-primary-700 font-bold"
                        >
                            {representative.name.charAt(0)}
                        </div>
                    {:else}
                        <div
                            class="w-full h-full flex items-center justify-center bg-primary-100 text-primary-700 font-bold"
                        >
                            {representative.name.charAt(0)}
                        </div>
                    {/if}
                </div>
                {#if representative.verified}
                    <div
                        class="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5 shadow-sm text-primary-600"
                    >
                        <Shield class="w-3.5 h-3.5 fill-primary-50" />
                    </div>
                {/if}
            </div>

            <div class="text-right">
                <div
                    class="text-2xl font-bold {getScoreColor(
                        representative.integrity_score,
                    )}"
                >
                    {representative.integrity_score}%
                </div>
                <div
                    class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider"
                >
                    Trust Score
                </div>
            </div>
        </div>

        <!-- Info -->
        <div>
            <h3
                class="text-lg font-bold text-gray-900 group-hover:text-primary-700 transition-colors line-clamp-1"
            >
                {representative.name}
            </h3>
            <p class="text-sm text-gray-500 line-clamp-1">
                {representative.title}
            </p>
            <div class="mt-2">
                <span
                    class="inline-flex items-center px-2 py-1 rounded-md bg-gray-50 text-xs font-medium text-gray-600 border border-gray-100"
                >
                    {representative.party}
                </span>
            </div>
        </div>

        <!-- Meta -->
        <div
            class="flex items-center justify-between pt-4 mt-auto border-t border-gray-50"
        >
            <div
                class="flex items-center gap-1.5 text-xs font-medium text-gray-500"
            >
                <FileText class="w-3.5 h-3.5" />
                <span>{representative.manifestos} Promises</span>
            </div>
            <span
                class="text-primary-600 text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity flex items-center"
            >
                View Profile <ChevronRight class="w-3 h-3 ml-0.5" />
            </span>
        </div>
    </div>

    <!-- Bottom Integrity Bar -->
    <div class="absolute bottom-0 left-0 w-full h-1 bg-gray-100">
        <div
            class="h-full {getBarColor(representative.integrity_score)}"
            style="width: {representative.integrity_score}%"
        ></div>
    </div>
</a>
