<template>
	<button
		type="button"
		@click="$emit('open-sheet')"
		:class="[
			'customer-chip group flex items-center gap-2 w-full text-start',
			'rounded-xl border transition-all duration-normal ease-pn-out',
			'focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-1',
			'touch-manipulation active:scale-[0.98]',
			customer
				? 'bg-surface border-hair hover:border-accent-line hover:shadow-sm'
				: 'bg-accent-soft border-accent-line border-dashed hover:bg-accent-soft/80',
		]"
	>
		<!-- Avatar / Tier Icon -->
		<div
			:class="[
				'flex-shrink-0 rounded-lg flex items-center justify-center',
				customer ? 'w-9 h-9' : 'w-9 h-9',
			]"
			:style="customer ? { background: tierHexSoft } : {}"
		>
			<template v-if="customer && loyaltyTier">
				<span class="text-base" :title="tierLabel">{{ tierIcon }}</span>
			</template>
			<template v-else-if="customer">
				<div class="w-9 h-9 bg-gradient-to-br from-accent to-accent-hover rounded-lg flex items-center justify-center">
					<svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
					</svg>
				</div>
			</template>
			<template v-else>
				<svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
				</svg>
			</template>
		</div>

		<!-- Info -->
		<div class="flex-1 min-w-0">
			<template v-if="customer">
				<p class="text-xs font-semibold text-ink truncate leading-tight">
					{{ customer.customer_name || customer.name }}
				</p>
				<div class="flex items-center gap-1.5 mt-0.5">
					<!-- Tier badge -->
					<span
						v-if="loyaltyTier"
						:class="[
							'inline-flex items-center gap-0.5 px-1.5 py-0 rounded text-[9px] font-bold uppercase tracking-wide',
							tierBgSoft, tierText,
						]"
					>
						{{ tierLabel }}
					</span>
					<!-- Points -->
					<span v-if="customer.loyalty_points" class="text-[10px] text-muted truncate">
						{{ formatPoints(customer.loyalty_points) }}
					</span>
					<!-- Phone fallback -->
					<span v-else-if="customer.mobile_no" class="text-[10px] text-muted truncate">
						{{ customer.mobile_no }}
					</span>
				</div>
			</template>
			<template v-else>
				<p class="text-xs font-semibold text-accent leading-tight">
					{{ __("Select Customer") }}
				</p>
				<p class="text-[10px] text-accent/70 mt-0.5">
					{{ __("Tap to choose") }}
				</p>
			</template>
		</div>

		<!-- Chevron -->
		<svg
			class="w-4 h-4 flex-shrink-0 text-faint group-hover:text-accent transition-colors duration-fast"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
		</svg>
	</button>
</template>

<script setup>
import { computed } from "vue"
import { getLoyaltyTier, loyaltyTiers, formatLoyaltyPoints } from "@/utils/colors"

const props = defineProps({
	customer: { type: Object, default: null },
})

defineEmits(["open-sheet"])

const loyaltyTier = computed(() => {
	if (!props.customer) return null
	return getLoyaltyTier(props.customer.loyalty_points || 0)
})

const tierLabel = computed(() => loyaltyTier.value?.label || "")
const tierIcon = computed(() => loyaltyTier.value?.icon || "")
const tierHexSoft = computed(() => loyaltyTier.value?.hexSoft || "#f5f4f9")
const tierBgSoft = computed(() => loyaltyTier.value?.bgSoft || "bg-inset")
const tierText = computed(() => loyaltyTier.value?.text || "text-muted")

function formatPoints(pts) {
	return formatLoyaltyPoints(pts)
}
</script>

<style scoped>
.customer-chip {
	will-change: transform;
}
</style>
