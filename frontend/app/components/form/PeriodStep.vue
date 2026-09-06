<script setup lang="ts">
const start = defineModel<string>("start", { required: true });
const end = defineModel<string>("end", { required: true });
</script>

<template>
    <div>
        <FormStepHeading :number="2" title="Période" />
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6">
            <FormTextField v-model="start" label="Début" type="date" />
            <FormTextField v-model="end" label="Fin" type="date" />
        </div>
    </div>
</template>
