<template>
    <header class="relative overflow-hidden">
        <div
            class="mx-auto max-w-6xl px-6 pt-10 pb-16 sm:px-10 sm:pt-20 sm:pb-28"
        >
            <div
                class="mb-10 flex flex-wrap items-center justify-between gap-y-4 sm:mb-16"
            >
                <p
                    class="font-mono text-[10px] uppercase tracking-[0.2em] text-mist dark:text-smoke sm:text-[11px] sm:tracking-[0.35em]"
                >
                    Celcat &rarr; ICS<span class="hidden sm:inline">
                        &mdash; Édition 01</span
                    >
                </p>
                <ThemeToggle />
            </div>

            <div
                class="grid grid-cols-1 items-end gap-8 lg:grid-cols-12 lg:gap-6"
            >
                <h1
                    class="font-serif text-5xl leading-[0.95] tracking-tight sm:text-7xl lg:col-span-9 lg:text-[6.5rem] lg:leading-[0.92]"
                >
                    Ton emploi<br />
                    du temps,<br />
                    <span class="italic text-signal">enfin lisible.</span>
                </h1>
                <p
                    class="text-sm leading-relaxed text-mist dark:text-smoke lg:col-span-3 lg:border-l lg:border-ink/10 lg:pl-6 sm:text-base lg:dark:border-paper/10"
                >
                    Génère une URL de calendrier à partir de ton Celcat &mdash;
                    compatible Google Calendar, Apple Calendar, Outlook et tout
                    autre client au format ICS.
                </p>
            </div>
        </div>

        <!-- Touches constructivistes : blocs géométriques qui cassent la grille (masqués sur mobile pour rester sobre) -->
        <div
            class="pointer-events-none absolute -bottom-12 -left-10 -z-10 hidden h-28 w-56 rotate-[-6deg] bg-ink/90 sm:block"
        />
        <div
            class="pointer-events-none absolute right-[-2rem] top-8 -z-10 hidden h-16 w-16 rotate-12 bg-signal sm:right-4 sm:block"
        />
    </header>
</template>
