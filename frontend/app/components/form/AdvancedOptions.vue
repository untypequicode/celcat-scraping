<script setup lang="ts">
const calendarName = defineModel<string>("calendarName", { required: true });
const cookie = defineModel<string>("cookie", { required: true });

const open = ref(false);
</script>

<template>
    <div>
        <button type="button" class="block text-left" @click="open = !open">
            <FormStepHeading :number="3" title="Options avancées">
                <span
                    class="font-mono text-xl leading-none text-mist dark:text-smoke"
                    >{{ open ? "−" : "+" }}</span
                >
            </FormStepHeading>
        </button>

        <div
            v-if="open"
            class="space-y-6 border-l-[3px] border-ink/10 pl-5 dark:border-paper/10"
        >
            <FormTextField
                v-model="calendarName"
                label="Nom du calendrier (optionnel)"
                placeholder="Ex : Mon emploi du temps"
            />

            <div>
                <FormTextArea
                    v-model="cookie"
                    label="Cookie de session Celcat (optionnel)"
                    placeholder="cle1=valeur1; cle2=valeur2; ..."
                    :rows="3"
                />
                <p
                    class="mt-3 text-xs leading-relaxed text-mist dark:text-smoke"
                >
                    À fournir uniquement si le serveur n'a pas déjà une session
                    configurée. Récupération manuelle&nbsp;: ouvre ton Celcat
                    connecté dans le navigateur &rarr; outils développeur (F12)
                    &rarr; onglet Réseau &rarr; requête
                    <code
                        class="bg-ink px-1 font-mono text-paper dark:bg-paper dark:text-graphite"
                        >GetCalendarData</code
                    >
                    &rarr; copie la valeur de l'en-tête
                    <code
                        class="bg-ink px-1 font-mono text-paper dark:bg-paper dark:text-graphite"
                        >Cookie</code
                    >.
                    <strong class="text-signal"
                        >Ne partage jamais le lien généré</strong
                    >
                    s'il contient ce cookie&nbsp;: il donne accès à ta session
                    Celcat.
                </p>
            </div>
        </div>
    </div>
</template>
