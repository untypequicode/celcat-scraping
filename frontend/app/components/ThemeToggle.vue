<script setup lang="ts">
const { scheme, toggle } = useColorScheme();
</script>

<template>
    <button
        type="button"
        role="switch"
        :aria-checked="scheme === 'dark'"
        aria-label="Basculer entre le thème clair et sombre"
        class="-m-2 shrink-0 p-2"
        @click="toggle"
    >
        <span class="relative block h-6 w-12 bg-ink/10 dark:bg-paper/10">
            <span
                class="absolute top-0.5 left-0.5 h-5 w-5 bg-signal transition-transform duration-200 ease-out"
                :class="scheme === 'dark' ? 'translate-x-6' : 'translate-x-0'"
            />
        </span>
    </button>
</template>
