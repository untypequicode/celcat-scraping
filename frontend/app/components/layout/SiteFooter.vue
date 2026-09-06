<script setup lang="ts">
const REPO_URL = "https://github.com/untypequicode/celcat-scraping/";
</script>

<template>
    <footer
        class="relative mt-20 bg-ink text-paper dark:bg-paper/[0.03] dark:text-paper sm:mt-40"
    >
        <div
            class="mx-auto grid max-w-6xl grid-cols-1 gap-10 px-6 py-12 sm:gap-12 sm:px-10 sm:py-20 lg:grid-cols-12"
        >
            <div class="lg:col-span-7">
                <p
                    class="mb-4 font-mono text-[11px] uppercase tracking-[0.3em] text-paper/50 dark:text-paper/40"
                >
                    Avertissement
                </p>
                <p
                    class="max-w-xl font-serif text-lg leading-relaxed sm:text-2xl"
                >
                    Cet outil est un projet réalisé par des étudiants, à titre
                    personnel. Il n'est ni officiel, ni affilié, ni validé par
                    l'université ou par l'éditeur de Celcat. Il se contente de
                    reformater les données de ton emploi du temps existant au
                    format ICS standard.
                </p>
                <p
                    class="mt-6 max-w-xl text-sm leading-relaxed text-paper/60 dark:text-paper/50"
                >
                    Aucune garantie n'est fournie quant à l'exactitude, la
                    disponibilité ou la continuité du service : vérifie toujours
                    tes horaires sur la source officielle avant de te fier au
                    calendrier généré.
                </p>
            </div>

            <div
                class="flex flex-col justify-between gap-8 lg:col-span-5 lg:items-end lg:gap-0"
            >
                <div class="h-1 w-16 bg-signal" />
                <div class="text-left lg:text-right">
                    <a
                        :href="REPO_URL"
                        target="_blank"
                        rel="noopener"
                        class="inline-block font-mono text-xs uppercase tracking-wide text-paper underline decoration-signal decoration-2 underline-offset-4 transition-opacity hover:opacity-80"
                    >
                        Code source sur GitHub &rarr;
                    </a>
                    <p class="mt-4 font-mono text-xs text-paper/40">
                        Celcat &rarr; ICS<br />
                        Projet étudiant non officiel
                    </p>
                </div>
            </div>
        </div>
    </footer>
</template>
