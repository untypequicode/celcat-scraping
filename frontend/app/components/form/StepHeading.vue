<script setup lang="ts">
const props = defineProps<{
    number: number;
    title: string;
}>();

const formattedNumber = computed(() => String(props.number).padStart(2, "0"));
</script>

<template>
    <div class="mb-8 flex items-end gap-3 sm:gap-5">
        <span
            class="select-none font-serif text-5xl italic leading-none text-signal sm:text-7xl"
        >
            {{ formattedNumber }}
        </span>
        <div class="flex items-center gap-3 pb-1 sm:pb-2">
            <span>
                <span
                    class="mb-1 block font-mono text-[11px] uppercase tracking-[0.3em] text-mist dark:text-smoke"
                >
                    Étape {{ number }}
                </span>
                <span class="font-serif text-2xl sm:text-3xl">{{ title }}</span>
            </span>
            <slot />
        </div>
    </div>
</template>
