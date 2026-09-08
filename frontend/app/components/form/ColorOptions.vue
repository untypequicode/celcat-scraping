<script setup lang="ts">
import { DEFAULT_COLORS } from "~/utils/defaultColors";

const enabled = defineModel<boolean>("enabled", { required: true });
const colors = defineModel<{ type: string; color: string }[]>("colors", {
    required: true,
});

const open = ref(false);

function addColor() {
    colors.value.push({ type: "", color: "#009DE0" });
}

function removeColor(index: number) {
    colors.value.splice(index, 1);
}

function resetToDefaults() {
    colors.value = JSON.parse(JSON.stringify(DEFAULT_COLORS));
}
</script>

<template>
    <div>
        <button
            type="button"
            class="block w-full text-left"
            @click="open = !open"
        >
            <FormStepHeading :number="4" title="Couleurs (Optionnel)">
                <span
                    class="font-mono text-xl leading-none text-mist dark:text-smoke"
                >
                    {{ open ? "−" : "+" }}
                </span>
            </FormStepHeading>
        </button>

        <div
            v-if="open"
            class="space-y-6 border-l-[3px] border-ink/10 pl-5 dark:border-paper/10"
        >
            <label class="flex items-center gap-3 cursor-pointer">
                <input
                    type="checkbox"
                    v-model="enabled"
                    class="h-4 w-4 accent-signal"
                />
                <span class="text-sm font-medium"
                    >Activer les couleurs personnalisées</span
                >
            </label>

            <div v-if="enabled" class="space-y-4">
                <p class="text-xs text-mist dark:text-smoke">
                    Si activé, les couleurs d'origine de Celcat seront ignorées.
                    Seuls les types définis ci-dessous auront une couleur.
                </p>

                <div class="space-y-3">
                    <!-- Remplacer le contenu du v-for par ceci -->
                    <div
                        v-for="(item, index) in colors"
                        :key="index"
                        class="flex gap-3 items-center"
                    >
                        <span
                            class="group relative flex w-full bg-ink/[0.04] dark:bg-paper/[0.06]"
                        >
                            <span
                                class="absolute inset-y-0 left-0 w-[3px] bg-transparent transition-colors group-focus-within:bg-signal"
                            />
                            <input
                                v-model="item.type"
                                type="text"
                                placeholder="Ex: TD Machine"
                                class="w-full bg-transparent px-4 py-3 text-sm outline-none placeholder:text-mist/60 dark:placeholder:text-smoke/50"
                            />
                        </span>

                        <div
                            class="relative flex shrink-0 items-center justify-center"
                        >
                            <input
                                v-model="item.color"
                                type="color"
                                class="h-11 w-14 cursor-pointer appearance-none rounded border-0 bg-transparent p-0 outline-none"
                            />
                        </div>

                        <button
                            type="button"
                            @click="removeColor(index)"
                            class="p-2 text-mist transition-colors hover:text-signal dark:text-smoke"
                            title="Supprimer"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                <div class="flex gap-4 pt-2">
                    <button
                        type="button"
                        @click="addColor"
                        class="font-mono text-[11px] uppercase tracking-wide text-signal hover:underline"
                    >
                        + Ajouter un type
                    </button>
                    <button
                        type="button"
                        @click="resetToDefaults"
                        class="font-mono text-[11px] uppercase tracking-wide text-mist hover:underline dark:text-smoke"
                    >
                        ↺ Réinitialiser par défaut
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
