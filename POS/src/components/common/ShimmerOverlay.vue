<template>
	<Transition name="fade">
		<div v-if="loading" class="shimmer-overlay" :class="overlayClass">
			<div class="shimmer-overlay__bar"></div>
		</div>
	</Transition>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	loading: { type: Boolean, default: true },
	absolute: { type: Boolean, default: false },
	class: { type: String, default: "" },
})

const overlayClass = computed(() => [
	props.absolute ? "absolute inset-0 z-10" : "relative",
	props.class,
])
</script>

<style scoped>
.shimmer-overlay {
	pointer-events: none;
	overflow: hidden;
	background: var(--pn-shimmer-base);
	border-radius: inherit;
}

.shimmer-overlay__bar {
	width: 100%;
	height: 100%;
	background: linear-gradient(
		90deg,
		var(--pn-shimmer-base) 25%,
		var(--pn-shimmer-highlight) 50%,
		var(--pn-shimmer-base) 75%
	);
	background-size: 200% 100%;
	animation: shimmer var(--pn-shimmer-speed, 1.8s) ease-in-out infinite;
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity var(--pn-duration-normal, 200ms) var(--pn-ease-out, cubic-bezier(0.16, 1, 0.3, 1));
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
