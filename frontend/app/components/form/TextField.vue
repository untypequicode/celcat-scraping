<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    placeholder?: string
    type?: string
    mono?: boolean
  }>(),
  {
    placeholder: '',
    type: 'text',
    mono: false
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
      <input
        v-model="model"
        :type="type"
        :placeholder="placeholder"
        :class="[
          'w-full bg-transparent px-4 py-3 text-sm outline-none placeholder:text-mist/60 dark:placeholder:text-smoke/50',
          mono ? 'font-mono' : 'font-sans'
        ]"
      />
    </span>
  </label>
</template>
