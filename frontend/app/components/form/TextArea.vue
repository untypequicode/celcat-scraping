<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    placeholder?: string
    rows?: number
  }>(),
  {
    placeholder: '',
    rows: 3
  }
)

const model = defineModel<string>({ required: true })
</script>

<template>
  <label class="block">
    <span class="mb-2 block font-mono text-[11px] uppercase tracking-[0.25em] text-mist dark:text-smoke">
      {{ label }}
    </span>
    <span class="group relative flex bg-ink/[0.04] dark:bg-paper/[0.06]">
      <span
        class="absolute inset-y-0 left-0 w-[3px] bg-transparent transition-colors group-focus-within:bg-signal"
      />
      <textarea
        v-model="model"
        :rows="rows"
        :placeholder="placeholder"
        class="w-full resize-none bg-transparent px-4 py-3 font-mono text-xs outline-none placeholder:text-mist/60 dark:placeholder:text-smoke/50"
      />
    </span>
  </label>
</template>
