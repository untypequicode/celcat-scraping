<script setup lang="ts">
const props = defineProps<{
  url: string
  copied: boolean
}>()

const emit = defineEmits<{
  copy: []
}>()
</script>

<template>
  <div class="bg-ink/[0.03] p-6 dark:bg-paper/[0.04] sm:p-8">
    <p class="mb-6 font-mono text-[11px] uppercase tracking-[0.3em] text-mist dark:text-smoke">
      Résultat
    </p>

    <div v-if="!props.url" class="py-10 text-center text-sm text-mist dark:text-smoke">
      Le lien apparaîtra ici.
    </div>

    <div v-else class="space-y-5">
      <div class="break-all bg-ink px-4 py-3 font-mono text-[11px] leading-relaxed text-paper dark:bg-paper dark:text-graphite">
        {{ props.url }}
      </div>

      <div class="grid grid-cols-2 gap-2">
        <button
          type="button"
          class="bg-signal py-3 font-mono text-xs uppercase tracking-wide text-paper transition-opacity hover:opacity-90"
          @click="emit('copy')"
        >
          {{ copied ? 'Copié ✓' : 'Copier' }}
        </button>
        <a
          :href="props.url"
          target="_blank"
          rel="noopener"
          class="flex items-center justify-center bg-ink/[0.06] py-3 text-center font-mono text-xs uppercase tracking-wide transition-colors hover:bg-ink/10 dark:bg-paper/[0.08] dark:hover:bg-paper/[0.14]"
        >
          Ouvrir
        </a>
      </div>
    </div>
  </div>
</template>
