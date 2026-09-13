<script setup>
defineProps({
  type: { type: String, default: "cards" }, // 'cards', 'rows', 'metrics', 'board'
  count: { type: Number, default: 3 },
});
</script>

<template>
  <!-- Metrics Skeleton -->
  <div v-if="type === 'metrics'" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
    <div
      v-for="i in count"
      :key="i"
      class="surface-card relative overflow-hidden"
    >
      <div class="shimmer-skeleton h-3.5 w-24 rounded-md"></div>
      <div class="shimmer-skeleton mt-3 h-9 w-16 rounded-lg"></div>
      <div class="shimmer-skeleton mt-3 h-2.5 w-32 rounded-md"></div>
    </div>
  </div>

  <!-- Cards Skeleton (e.g. Courses & Projects) -->
  <div v-else-if="type === 'cards'" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <div
      v-for="i in count"
      :key="i"
      class="surface-card relative flex flex-col justify-between overflow-hidden p-5"
    >
      <div>
        <div class="flex items-center justify-between">
          <div class="shimmer-skeleton h-10 w-10 rounded-xl"></div>
          <div class="shimmer-skeleton h-6 w-14 rounded-lg"></div>
        </div>
        <div class="shimmer-skeleton mt-4 h-5 w-3/4 rounded-md"></div>
        <div class="shimmer-skeleton mt-2 h-3 w-full rounded-md"></div>
        <div class="shimmer-skeleton mt-1.5 h-3 w-2/3 rounded-md"></div>
      </div>
      <div class="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
        <div class="flex items-center justify-between">
          <div class="shimmer-skeleton h-4 w-20 rounded-md"></div>
          <div class="shimmer-skeleton h-8 w-24 rounded-xl"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Rows Skeleton (e.g. Ledger Rows & Admin Directory) -->
  <div v-else-if="type === 'rows'" class="space-y-3">
    <div
      v-for="i in count"
      :key="i"
      class="surface-card relative flex items-center justify-between gap-4 overflow-hidden p-4"
    >
      <div class="flex flex-1 items-center gap-3">
        <div class="shimmer-skeleton h-10 w-10 flex-none rounded-xl"></div>
        <div class="flex-1 space-y-2">
          <div class="shimmer-skeleton h-4 w-1/3 rounded-md"></div>
          <div class="shimmer-skeleton h-3 w-1/2 rounded-md"></div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="shimmer-skeleton h-7 w-20 rounded-lg"></div>
        <div class="shimmer-skeleton h-7 w-16 rounded-lg"></div>
      </div>
    </div>
  </div>

  <!-- Board Columns Skeleton -->
  <div v-else-if="type === 'board'" class="grid gap-6 lg:grid-cols-3">
    <div
      v-for="i in 3"
      :key="i"
      class="flex flex-col rounded-2xl border border-slate-200/80 bg-slate-100/40 p-4 dark:border-slate-800 dark:bg-night-surface/50"
    >
      <div class="shimmer-skeleton h-12 w-full rounded-xl"></div>
      <div class="mt-4 space-y-3">
        <div v-for="j in 2" :key="j" class="surface-card overflow-hidden p-4">
          <div class="shimmer-skeleton h-4 w-3/4 rounded-md"></div>
          <div class="shimmer-skeleton mt-2 h-3 w-1/2 rounded-md"></div>
          <div class="shimmer-skeleton mt-4 h-6 w-full rounded-lg"></div>
        </div>
      </div>
    </div>
  </div>
</template>
