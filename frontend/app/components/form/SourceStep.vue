<script setup lang="ts">
import type { ResourceType } from "~/composables/useCelcatUrlParser";
import type { SourceMode } from "~/composables/useCalendarForm";

defineProps<{
    urlError: string;
    detected: {
        baseUrl: string;
        resourceType: ResourceType;
        resourceId: string;
    } | null;
}>();

const mode = defineModel<SourceMode>("mode", { required: true });
const celcatUrl = defineModel<string>("celcatUrl", { required: true });
const baseUrl = defineModel<string>("baseUrl", { required: true });
const resourceType = defineModel<ResourceType>("resourceType", {
    required: true,
});
const resourceId = defineModel<string>("resourceId", { required: true });
const RESOURCE_TYPE_OPTIONS: { value: ResourceType; label: string }[] = [
    { value: "group", label: "Groupe" },
    { value: "module", label: "Matière" },
    { value: "room", label: "Salle" },
];
</script>

<template>
    <div>
        <FormStepHeading :number="1" title="Source" />

        <div class="mb-8 flex w-fit bg-ink/[0.04] p-1 dark:bg-paper/[0.06]">
            <button
                type="button"
                class="px-4 py-2 font-mono text-xs uppercase tracking-wide transition-colors"
                :class="
                    mode === 'url'
                        ? 'bg-ink text-paper dark:bg-paper dark:text-graphite'
                        : 'text-mist dark:text-smoke'
                "
                @click="mode = 'url'"
            >
                Lien Celcat
            </button>
            <button
                type="button"
                class="px-4 py-2 font-mono text-xs uppercase tracking-wide transition-colors"
                :class="
                    mode === 'manual'
                        ? 'bg-ink text-paper dark:bg-paper dark:text-graphite'
                        : 'text-mist dark:text-smoke'
                "
                @click="mode = 'manual'"
            >
                Manuel
            </button>
        </div>

        <div v-if="mode === 'url'" class="space-y-4">
            <FormTextField
                v-model="celcatUrl"
                label="Lien Celcat (copié depuis la barre d'adresse)"
                placeholder="https://celcat.u-bordeaux.fr/calendar/cal?...&fid0=..."
                mono
            />

            <p
                v-if="urlError"
                class="font-mono text-xs uppercase tracking-wide text-signal"
            >
                {{ urlError }}
            </p>
            <div
                v-else-if="detected"
                class="space-y-1 border-l-[3px] border-signal bg-ink/[0.03] px-4 py-3 font-mono text-xs dark:bg-paper/[0.05]"
            >
                <p>
                    <span class="text-mist dark:text-smoke"
                        >Ressource détectée&nbsp;:</span
                    >
                    {{ detected.resourceId }}
                    <span class="text-mist dark:text-smoke"
                        >({{
                            RESOURCE_TYPE_OPTIONS.find(
                                (o) => o.value === detected.resourceType,
                            )?.label
                        }})</span
                    >
                </p>
                <p>
                    <span class="text-mist dark:text-smoke"
                        >Instance&nbsp;:</span
                    >
                    {{ detected.baseUrl }}
                </p>
            </div>
        </div>

        <div v-else class="space-y-4">
            <label class="block">
                <span
                    class="mb-2 block font-mono text-[11px] uppercase tracking-[0.25em] text-mist dark:text-smoke"
                >
                    Type de ressource
                </span>
                <span class="flex bg-ink/[0.04] dark:bg-paper/[0.06]">
                    <select
                        v-model="resourceType"
                        class="w-full bg-transparent px-4 py-3 text-sm outline-none"
                    >
                        <option
                            v-for="opt in RESOURCE_TYPE_OPTIONS"
                            :key="opt.value"
                            :value="opt.value"
                        >
                            {{ opt.label }}
                        </option>
                    </select>
                </span>
            </label>
            <FormTextField
                v-model="resourceId"
                label="Identifiant (federation id)"
                placeholder="M1 CMI OSIA parcours OPTIM"
            />
            <FormTextField
                v-model="baseUrl"
                label="URL de l'instance Celcat"
                placeholder="https://celcat.u-bordeaux.fr/calendar"
                mono
            />
        </div>
    </div>
</template>
