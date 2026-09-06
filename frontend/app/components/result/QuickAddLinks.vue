<script setup lang="ts">
const props = defineProps<{
  url: string
  calendarName: string
}>()

const webcalUrl = computed(() => props.url.replace(/^https?:\/\//, 'webcal://'))
const googleCalendarUrl = computed(
  () => `https://calendar.google.com/calendar/render?cid=${encodeURIComponent(props.url)}`
)
const outlookUrl = computed(
  () =>
    `https://outlook.live.com/calendar/0/addfromweb?url=${encodeURIComponent(props.url)}&name=${encodeURIComponent(
      props.calendarName || 'Celcat'
    )}`
)
</script>

<template>
  <div>
    <p class="mb-3 border-t border-ink/10 pt-6 font-mono text-[11px] uppercase tracking-[0.3em] text-mist dark:border-paper/10 dark:text-smoke">
      Ajout rapide
    </p>
    <div class="space-y-2">
      <a
        :href="googleCalendarUrl"
        target="_blank"
        rel="noopener"
        class="flex items-center justify-between bg-ink/[0.03] px-4 py-3 text-xs font-medium uppercase tracking-wide transition-colors hover:bg-ink/[0.07] dark:bg-paper/[0.04] dark:hover:bg-paper/[0.09]"
      >
        Google Calendar <span class="text-signal">&rarr;</span>
      </a>
      <a
        :href="webcalUrl"
        class="flex items-center justify-between bg-ink/[0.03] px-4 py-3 text-xs font-medium uppercase tracking-wide transition-colors hover:bg-ink/[0.07] dark:bg-paper/[0.04] dark:hover:bg-paper/[0.09]"
      >
        Apple Calendar (webcal) <span class="text-signal">&rarr;</span>
      </a>
      <a
        :href="outlookUrl"
        target="_blank"
        rel="noopener"
        class="flex items-center justify-between bg-ink/[0.03] px-4 py-3 text-xs font-medium uppercase tracking-wide transition-colors hover:bg-ink/[0.07] dark:bg-paper/[0.04] dark:hover:bg-paper/[0.09]"
      >
        Outlook.com <span class="text-signal">&rarr;</span>
      </a>
    </div>
    <p class="mt-3 text-[11px] leading-snug text-mist dark:text-smoke">
      Ces raccourcis pré-remplissent l'ajout de calendrier mais leur comportement dépend des
      applications. En cas d'échec, utilise l'ajout manuel « à partir d'une URL » avec le lien
      ci-dessus.
    </p>
  </div>
</template>
