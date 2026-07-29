<template>
	<div ref="dropdownRef" class="relative">
		<button
			@click="toggleDropdown"
			:disabled="isChanging || isOffline"
			:title="isOffline ? __('Unavailable while offline') : __('Select Price List')"
			class="flex items-center gap-1.5 px-2 py-1.5 text-sm font-medium transition-colors rounded-lg border"
			:class="isOffline ? 'text-muted bg-faint/20 border-hair cursor-not-allowed' : 'text-ink bg-surface border-hair-strong hover:bg-canvas focus:outline-none'"
		>
			<svg class="w-4 h-4 flex-shrink-0" :class="isOffline ? 'text-faint' : 'text-muted'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span class="hidden sm:inline text-xs max-w-[100px] truncate">{{ activeLabel }}</span>
			<svg
				class="w-3 h-3 transition-transform flex-shrink-0"
				:class="[isOpen ? 'rotate-180' : '', isOffline ? 'text-faint' : 'text-muted']"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		<Transition
			enter-active-class="transition ease-out duration-150"
			enter-from-class="opacity-0 scale-95"
			enter-to-class="opacity-100 scale-100"
			leave-active-class="transition ease-in duration-100"
			leave-from-class="opacity-100 scale-100"
			leave-to-class="opacity-0 scale-95"
		>
			<div
				v-if="isOpen"
				class="absolute z-50 mt-2 w-44 rounded-lg bg-surface shadow-lg ring-1 ring-black/5 end-0"
				role="menu"
			>
				<div class="py-1 max-h-60 overflow-y-auto">
					<button
						v-for="pl in priceLists"
						:key="pl"
						@click="selectPriceList(pl)"
						class="flex items-center w-full px-4 py-2 text-sm transition-colors"
						:class="
							activePriceList === pl
								? 'bg-accent-soft text-accent'
								: 'text-ink hover:bg-inset'
						"
						role="menuitem"
					>
						<span class="flex-1 text-start truncate">{{ pl }}</span>
						<svg
							v-if="activePriceList === pl"
							class="w-4 h-4 text-accent flex-shrink-0 ms-2"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					</button>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useItemSearchStore } from "@/stores/itemSearch"

const itemStore = useItemSearchStore()

const isOpen = ref(false)
const isChanging = ref(false)
const dropdownRef = ref(null)
const isOffline = ref(!navigator.onLine)

const priceLists = computed(() => itemStore.availablePriceLists || [])
const activePriceList = computed(() => itemStore.selectedPriceList)
const activeLabel = computed(() => activePriceList.value || itemStore.availablePriceLists?.[0] || "")

const toggleDropdown = () => {
	if (isChanging.value || isOffline.value) return
	isOpen.value = !isOpen.value
}

const selectPriceList = async (pl) => {
	isOpen.value = false
	if (pl === activePriceList.value || isChanging.value) return

	isChanging.value = true
	try {
		await itemStore.updatePricesForPriceList(pl)
	} finally {
		isChanging.value = false
	}
}

const handleClickOutside = (e) =>
	dropdownRef.value?.contains(e.target) || (isOpen.value = false)

const handleOnline = () => { isOffline.value = false }
const handleOffline = () => { isOffline.value = true; isOpen.value = false }

onMounted(() => {
	document.addEventListener("click", handleClickOutside)
	window.addEventListener("online", handleOnline)
	window.addEventListener("offline", handleOffline)
})
onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside)
	window.removeEventListener("online", handleOnline)
	window.removeEventListener("offline", handleOffline)
})
</script>
