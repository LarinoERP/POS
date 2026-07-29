<template>
	<div :class="['skeleton-container', containerClass]" :style="containerStyle">
		<!-- Avatar + lines variant (customer, user, etc.) -->
		<template v-if="variant === 'avatar-lines'">
			<div class="flex items-center gap-3">
				<div
					:class="['shimmer rounded-full flex-shrink-0', avatarSizeClass]"
					:style="avatarStyle"
				></div>
				<div class="flex-1 space-y-2">
					<div
						v-for="i in lines"
						:key="i"
						class="shimmer rounded-md"
						:style="{ height: lineHeight, width: lineWeight(i) }"
					></div>
				</div>
			</div>
		</template>

		<!-- Card variant (product card, table card, etc.) -->
		<template v-else-if="variant === 'card'">
			<div class="space-y-3">
				<div class="shimmer rounded-xl" :style="{ height: imageHeight, width: '100%' }"></div>
				<div class="space-y-2 px-1">
					<div
						v-for="i in lines"
						:key="i"
						class="shimmer rounded-md"
						:style="{ height: lineHeight, width: lineWeight(i) }"
					></div>
				</div>
			</div>
		</template>

		<!-- List item variant (invoice row, customer row, etc.) -->
		<template v-else-if="variant === 'list-item'">
			<div class="flex items-center gap-3 p-3">
				<div
					v-if="showAvatar"
					:class="['shimmer rounded-lg flex-shrink-0', avatarSizeClass]"
					:style="avatarStyle"
				></div>
				<div class="flex-1 space-y-2">
					<div
						v-for="i in lines"
						:key="i"
						class="shimmer rounded-md"
						:style="{ height: lineHeight, width: lineWeight(i) }"
					></div>
				</div>
				<div v-if="showTrailing" class="shimmer rounded-md flex-shrink-0" :style="trailingStyle"></div>
			</div>
		</template>

		<!-- Text lines variant (generic) -->
		<template v-else-if="variant === 'text'">
			<div class="space-y-2">
				<div
					v-for="i in lines"
					:key="i"
					class="shimmer rounded-md"
					:style="{ height: lineHeight, width: lineWeight(i) }"
				></div>
			</div>
		</template>

		<!-- Circle variant (icon placeholder) -->
		<template v-else-if="variant === 'circle'">
			<div class="shimmer rounded-full" :style="circleStyle"></div>
		</template>

		<!-- Rect variant (custom rectangle) -->
		<template v-else-if="variant === 'rect'">
			<div class="shimmer rounded-lg" :style="rectStyle"></div>
		</template>

		<!-- Raw slot for fully custom skeletons -->
		<template v-else>
			<slot />
		</template>
	</div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	variant: {
		type: String,
		default: "text",
		validator: (v) =>
			["avatar-lines", "card", "list-item", "text", "circle", "rect", "custom"].includes(v),
	},
	lines: { type: Number, default: 2 },
	lineHeight: { type: String, default: "12px" },
	width: { type: String, default: "100%" },
	height: { type: String, default: null },
	showAvatar: { type: Boolean, default: true },
	showTrailing: { type: Boolean, default: false },
	avatarSize: {
		type: String,
		default: "md",
		validator: (v) => ["sm", "md", "lg"].includes(v),
	},
	imageHeight: { type: String, default: "120px" },
	circleSize: { type: String, default: "40px" },
	rectWidth: { type: String, default: "100%" },
	rectHeight: { type: String, default: "60px" },
	class: { type: String, default: "" },
})

const containerClass = computed(() => props.class)

const containerStyle = computed(() => ({
	width: props.width,
	...(props.height ? { height: props.height } : {}),
}))

const avatarSizeClass = computed(() => {
	const sizes = { sm: "w-8 h-8", md: "w-10 h-10", lg: "w-14 h-14" }
	return sizes[props.avatarSize]
})

const avatarStyle = computed(() => {
	const sizes = { sm: "32px", md: "40px", lg: "56px" }
	return { width: sizes[props.avatarSize], height: sizes[props.avatarSize] }
})

const circleStyle = computed(() => ({
	width: props.circleSize,
	height: props.circleSize,
}))

const rectStyle = computed(() => ({
	width: props.rectWidth,
	height: props.rectHeight,
}))

const trailingStyle = computed(() => ({
	width: "48px",
	height: "14px",
}))

function lineWeight(index) {
	if (index === props.lines && props.lines > 1) return "60%"
	return "100%"
}
</script>

<style scoped>
.skeleton-container {
	--shimmer-base: var(--pn-shimmer-base, #f5f4f9);
	--shimmer-highlight: var(--pn-shimmer-highlight, #ffffff);
}
</style>
