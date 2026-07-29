<template>
	<Teleport to="body">
		<Transition name="sheet-overlay">
			<div
				v-if="show"
				class="fixed inset-0 z-[var(--z-dialog-overlay)] bg-black/45 backdrop-blur-sm"
				@click.self="close"
			></div>
		</Transition>

		<Transition name="sheet">
			<div
				v-if="show"
				class="fixed inset-x-0 bottom-0 z-[var(--z-dialog-content)] max-h-[85vh] flex flex-col"
			>
				<!-- Sheet Handle (drag indicator) -->
				<div class="flex justify-center pt-2 pb-1 bg-surface rounded-t-[var(--pn-radius)]">
					<div class="w-10 h-1 rounded-full bg-hair-strong"></div>
				</div>

				<!-- Sheet Content -->
				<div class="flex-1 flex flex-col bg-surface overflow-hidden rounded-t-[var(--pn-radius)] shadow-pn-lg">
					<!-- Header -->
					<div class="flex items-center justify-between px-4 pt-3 pb-2 border-b border-hair">
						<h3 class="text-sm font-bold text-ink">{{ __("Select Customer") }}</h3>
						<button
							@click="close"
							class="w-8 h-8 flex items-center justify-center rounded-lg text-faint hover:text-ink hover:bg-inset transition-colors touch-manipulation"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>

					<!-- Search -->
					<div class="px-4 py-3 border-b border-hair">
						<div class="relative">
							<div class="absolute inset-y-0 start-0 ps-3 flex items-center pointer-events-none">
								<svg v-if="!loading" class="w-4 h-4 text-faint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
								<div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-accent"></div>
							</div>
							<input
								ref="searchInputRef"
								:value="searchTerm"
								@input="handleSearchInput"
								type="text"
								:placeholder="__('Search by name, phone, or email...')"
								class="w-full h-10 ps-9 pe-9 text-sm border border-hair-strong rounded-xl bg-canvas focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-shadow"
								@keydown="handleKeydown"
								autocomplete="off"
								:aria-label="__('Search customers')"
							/>
							<button
								v-if="searchTerm"
								@click="clearSearch"
								class="absolute inset-y-0 end-0 pe-3 flex items-center text-faint hover:text-muted"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Customer List -->
					<div class="flex-1 overflow-y-auto overscroll-contain" style="will-change: scroll-position">
						<!-- Loading skeleton -->
						<div v-if="loading && customers.length === 0" class="p-4 space-y-3">
							<div v-for="i in 5" :key="i" class="flex items-center gap-3 p-3">
								<div class="w-10 h-10 rounded-xl shimmer flex-shrink-0"></div>
								<div class="flex-1 space-y-2">
									<div class="h-3 rounded-md shimmer" :style="{ width: i % 2 === 0 ? '70%' : '85%' }"></div>
									<div class="h-2.5 rounded-md shimmer" style="width: 50%"></div>
								</div>
								<div v-if="i % 3 === 0" class="w-12 h-4 rounded shimmer flex-shrink-0"></div>
							</div>
						</div>

						<!-- Recommendations -->
						<div v-else-if="recommendations.length > 0 && !searchTerm" class="px-4 pt-3 pb-1">
							<div class="flex flex-wrap gap-2">
								<div
									v-for="rec in recommendations"
									:key="rec.type"
									class="inline-flex items-center gap-1 px-2 py-1 bg-accent-soft text-accent rounded-lg text-xs font-medium"
								>
									<span>{{ rec.icon }}</span>
									<span>{{ rec.text }}</span>
								</div>
							</div>
						</div>

						<!-- Recent/Frequent label -->
						<div v-if="!loading && !searchTerm && customers.length > 0" class="px-4 pt-3 pb-1">
							<p class="text-[11px] font-semibold text-faint uppercase tracking-wider">
								{{ __("Recent & Frequent") }}
							</p>
						</div>

						<!-- Search results count -->
						<div v-if="!loading && searchTerm && customers.length > 0" class="px-4 pt-3 pb-1">
							<p class="text-[11px] font-semibold text-faint uppercase tracking-wider">
								{{ __("{0} results", [customers.length]) }}
							</p>
						</div>

						<!-- Customer list -->
						<div v-if="customers.length > 0" class="px-2 pb-2">
							<button
								v-for="(customer, index) in customers"
								:key="customer.name"
								v-memo="[customer.name, index === selectedIndex]"
								@click="selectCustomer(customer)"
								@mouseenter="selectedIndex = index"
								:class="[
									'w-full text-start p-3 rounded-xl transition-all duration-fast ease-pn-out',
									'border border-transparent',
									index === selectedIndex
										? 'bg-accent-soft border-accent-line'
										: 'hover:bg-inset',
								]"
							>
								<div class="flex items-center gap-3">
									<!-- Avatar with tier indicator -->
									<div
										class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
										:style="{ background: getTierHexSoft(customer) }"
									>
										<span v-if="getTier(customer)" class="text-base" :title="getTierLabel(customer)">
											{{ getTierIcon(customer) }}
										</span>
										<svg v-else class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
										</svg>
									</div>

									<!-- Info -->
									<div class="flex-1 min-w-0">
										<p class="text-sm font-semibold text-ink truncate">
											{{ customer.customer_name || customer.name }}
										</p>
										<div class="flex items-center gap-2 mt-0.5">
											<span v-if="customer.mobile_no" class="text-xs text-muted truncate">
												{{ customer.mobile_no }}
											</span>
											<span v-if="customer.email_id" class="text-xs text-muted truncate hidden sm:inline">
												{{ customer.email_id }}
											</span>
										</div>
										<div v-if="customer.customer_group" class="text-[11px] text-faint mt-0.5 truncate">
											{{ customer.customer_group }}
										</div>
									</div>

									<!-- Tier + Points -->
									<div class="flex flex-col items-end gap-0.5 flex-shrink-0">
										<span
											v-if="getTier(customer)"
											:class="[
												'inline-flex items-center gap-0.5 px-1.5 py-0 rounded text-[9px] font-bold uppercase tracking-wide',
												getTierBgSoft(customer), getTierText(customer),
											]"
										>
											{{ getTierLabel(customer) }}
										</span>
										<span v-if="customer.loyalty_points" class="text-[10px] text-muted">
											{{ formatPoints(customer.loyalty_points) }}
										</span>
									</div>

									<!-- Selected check -->
									<div v-if="index === selectedIndex" class="flex-shrink-0">
										<svg class="w-5 h-5 text-accent" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
										</svg>
									</div>
								</div>
							</button>
						</div>

						<!-- Empty state -->
						<div
							v-if="!loading && customers.length === 0 && allCustomers.length === 0"
							class="flex flex-col items-center justify-center py-12 px-4"
						>
							<div class="w-14 h-14 bg-inset rounded-2xl flex items-center justify-center mb-3">
								<svg class="w-7 h-7 text-faint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
							</div>
							<p class="text-sm font-medium text-ink">{{ __("No customers yet") }}</p>
							<p class="text-xs text-muted mt-1">{{ __("Create your first customer to get started") }}</p>
						</div>

						<!-- No search results -->
						<div
							v-if="!loading && customers.length === 0 && searchTerm && allCustomers.length > 0"
							class="flex flex-col items-center justify-center py-12 px-4"
						>
							<div class="w-14 h-14 bg-inset rounded-2xl flex items-center justify-center mb-3">
								<svg class="w-7 h-7 text-faint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
							</div>
							<p class="text-sm font-medium text-ink">{{ __('No results for "{0}"', [searchTerm]) }}</p>
							<p class="text-xs text-muted mt-1">{{ __("Try a different search term") }}</p>
						</div>
					</div>

					<!-- Footer -->
					<div class="flex-shrink-0 border-t border-hair px-4 py-3 bg-surface">
						<button
							@click="createNewCustomer"
							class="w-full flex items-center justify-center gap-2 py-2.5 px-4 text-sm font-semibold text-accent bg-accent-soft hover:bg-accent-line rounded-xl transition-colors touch-manipulation"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
							</svg>
							{{ __("Create New Customer") }}
						</button>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { useCustomerSearchStore } from "@/stores/customerSearch"
import { storeToRefs } from "pinia"
import { computed, nextTick, onMounted, ref, watch } from "vue"
import { getLoyaltyTier, formatLoyaltyPoints } from "@/utils/colors"

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
})

const emit = defineEmits(["update:modelValue", "customer-selected", "create-customer"])

// Store
const customerStore = useCustomerSearchStore()
const {
	filteredCustomers,
	loading,
	selectedIndex,
	searchTerm,
	allCustomers,
	recommendations,
} = storeToRefs(customerStore)

// Refs
const searchInputRef = ref(null)

// Computed
const show = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

const customers = computed(() => filteredCustomers.value)

// Watch for open → focus search, load customers
watch(show, (val) => {
	if (val) {
		customerStore.clearSearch()
		customerStore.loadAllCustomers(props.posProfile)
		nextTick(() => searchInputRef.value?.focus())
	}
})

// Methods
function close() {
	show.value = false
}

function handleSearchInput(e) {
	customerStore.setSearchTerm(e.target.value)
}

function clearSearch() {
	customerStore.clearSearch()
	nextTick(() => searchInputRef.value?.focus())
}

function handleKeydown(e) {
	if (customers.value.length === 0) return

	if (e.key === "ArrowDown") {
		e.preventDefault()
		customerStore.setSelectedIndex(
			Math.min(selectedIndex.value + 1, customers.value.length - 1),
		)
	} else if (e.key === "ArrowUp") {
		e.preventDefault()
		customerStore.setSelectedIndex(Math.max(selectedIndex.value - 1, -1))
	} else if (e.key === "Enter") {
		e.preventDefault()
		if (selectedIndex.value >= 0 && selectedIndex.value < customers.value.length) {
			selectCustomer(customers.value[selectedIndex.value])
		} else if (customers.value.length === 1) {
			selectCustomer(customers.value[0])
		}
	} else if (e.key === "Escape") {
		close()
	}
}

function selectCustomer(customer) {
	customerStore.trackCustomerSelection(customer.name)
	emit("customer-selected", customer)
	close()
}

function createNewCustomer() {
	close()
	emit("create-customer", searchTerm.value)
}

function getTier(customer) {
	return getLoyaltyTier(customer?.loyalty_points || 0)
}

function getTierLabel(customer) {
	return getTier(customer)?.label || ""
}

function getTierIcon(customer) {
	return getTier(customer)?.icon || ""
}

function getTierHexSoft(customer) {
	return getTier(customer)?.hexSoft || "#f5f4f9"
}

function getTierBgSoft(customer) {
	return getTier(customer)?.bgSoft || "bg-inset"
}

function getTierText(customer) {
	return getTier(customer)?.text || "text-muted"
}

function formatPoints(pts) {
	return formatLoyaltyPoints(pts)
}
</script>

<style scoped>
/* Sheet overlay transition */
.sheet-overlay-enter-active {
	transition: opacity var(--pn-duration-normal) var(--pn-ease-out);
}
.sheet-overlay-leave-active {
	transition: opacity var(--pn-duration-fast) var(--pn-ease-in);
}
.sheet-overlay-enter-from,
.sheet-overlay-leave-to {
	opacity: 0;
}

/* Sheet slide transition */
.sheet-enter-active {
	animation: sheet-slide-up var(--pn-duration-sheet) var(--pn-ease-out);
}
.sheet-leave-active {
	animation: sheet-slide-down var(--pn-duration-normal) var(--pn-ease-in);
}
</style>
