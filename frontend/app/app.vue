<script setup lang="ts">
const {
    mode,
    celcatUrl,
    baseUrl,
    resourceType,
    resourceId,
    urlError,
    detected,
    start,
    end,
    calendarName,
    cookie,
    errors,
    attempted,
    generatedUrl,
    copied,
    generate,
    copyLink,
} = useCalendarForm();

useSiteSeo();
</script>

<template>
    <div class="min-h-screen font-sans">
        <LayoutDisclaimerBar />
        <LayoutSiteHeader />

        <main class="relative mx-auto max-w-6xl px-6 py-12 sm:px-10 sm:py-24">
            <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-12">
                <section class="space-y-14 sm:space-y-20 lg:col-span-7">
                    <FormSourceStep
                        v-model:mode="mode"
                        v-model:celcat-url="celcatUrl"
                        v-model:base-url="baseUrl"
                        v-model:resource-type="resourceType"
                        v-model:resource-id="resourceId"
                        :url-error="urlError"
                        :detected="detected"
                    />

                    <FormPeriodStep v-model:start="start" v-model:end="end" />

                    <FormAdvancedOptions
                        v-model:calendar-name="calendarName"
                        v-model:cookie="cookie"
                    />

                    <div class="space-y-4">
                        <button
                            type="button"
                            class="w-full bg-ink px-8 py-4 text-center font-mono text-xs uppercase tracking-[0.2em] text-paper transition-colors hover:bg-signal dark:bg-paper dark:text-graphite dark:hover:bg-signal dark:hover:text-paper sm:w-auto"
                            @click="generate"
                        >
                            Générer le lien &rarr;
                        </button>

                        <ul
                            v-if="attempted && errors.length"
                            class="space-y-1 font-mono text-xs uppercase tracking-wide text-signal"
                        >
                            <li v-for="err in errors" :key="err">
                                &mdash; {{ err }}
                            </li>
                        </ul>
                    </div>
                </section>

                <aside class="lg:col-span-5">
                    <div class="space-y-10 lg:sticky lg:top-10">
                        <ResultPanel
                            :url="generatedUrl"
                            :copied="copied"
                            @copy="copyLink"
                        />
                        <ResultQuickAddLinks
                            v-if="generatedUrl"
                            :url="generatedUrl"
                            :calendar-name="calendarName || resourceId"
                        />
                    </div>
                </aside>
            </div>
        </main>

        <LayoutSiteFooter />
    </div>
</template>
