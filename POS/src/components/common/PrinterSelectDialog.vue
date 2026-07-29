<template>
	<DialogRoot v-model:open="visible">
		<DialogPortal>
			<DialogOverlay
				class="fixed inset-0 bg-black-overlay-200 dark:bg-black-overlay-700 overflow-y-auto dialog-overlay printer-picker-overlay outline-none"
				:data-dialog="title || __('Select Printers')"
			>
				<div
					class="flex min-h-screen flex-col items-center justify-center px-4 py-4 text-center"
				>
					<DialogContent
						class="my-8 inline-block w-full max-w-md transform overflow-hidden rounded-xl bg-surface-modal text-start align-middle shadow-xl dialog-content printer-picker-content focus-visible:outline-none"
						@escape-key-down="cancel"
						@pointer-down-outside="onPointerDownOutside"
					>
						<div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
							<div class="flex">
								<div class="w-full flex-1">
									<div class="mb-6 flex items-center justify-between">
										<div class="flex items-center space-x-2">
											<DialogTitle as="header">
												<h3
													class="text-2xl font-semibold leading-6 text-ink-gray-9"
												>
													{{ title || __("Select Printers") }}
												</h3>
											</DialogTitle>
										</div>
										<DialogClose as-child>
											<Button variant="ghost" @click="cancel">
												<template #icon>
													<LucideX class="h-4 w-4 text-ink-gray-9" />
												</template>
											</Button>
										</DialogClose>
									</div>

									<div class="flex flex-col gap-4 py-1">
										<div class="flex items-center gap-2">
											<div
												class="w-2.5 h-2.5 rounded-full flex-shrink-0"
												:class="
													qzConnecting
														? 'bg-yellow-500 animate-pulse'
														: qzConnected
															? 'bg-good'
															: 'bg-bad'
												"
											/>
											<span
												class="text-xs font-medium"
												:class="
													qzConnecting
														? 'text-warn'
														: qzConnected
															? 'text-good'
															: 'text-bad'
												"
											>
												{{
													qzConnecting
														? __("Connecting to QZ Tray...")
														: qzConnected
															? __("QZ Tray Connected")
															: __("QZ Tray Not Connected")
												}}
											</span>
											<button
												v-if="!qzConnected && !qzConnecting"
												type="button"
												@click="handleConnect"
												class="ms-auto text-xs px-2 py-1 bg-accent-soft text-accent rounded transition-colors"
											>
												{{ __("Retry") }}
											</button>
										</div>

										<div
											v-if="preparing"
											class="text-sm text-muted text-center py-2"
										>
											{{ __("Loading printers...") }}
										</div>

										<template v-else>
											<div class="flex items-center justify-between gap-2">
												<p class="text-sm font-medium text-ink-gray-9">
													{{ __("Printers") }}
												</p>
												<div class="flex items-center gap-2">
													<button
														type="button"
														@click="
															allSelected ? clearSelection() : selectAll()
														"
														:disabled="printers.length === 0"
														class="text-xs px-2 py-1 text-accent hover:bg-accent-soft rounded transition-colors disabled:opacity-50"
													>
														{{
															allSelected
																? __("Clear all")
																: __("Select all")
														}}
													</button>
													<button
														type="button"
														@click="refreshPrinters"
														:disabled="loadingPrinters"
														class="text-xs px-2 py-1 bg-inset hover:bg-inset rounded transition-colors disabled:opacity-50"
													>
														{{ __("Refresh") }}
													</button>
												</div>
											</div>

											<p
												v-if="printers.length === 0"
												class="text-xs text-muted"
											>
												{{ __("No printers found. Is QZ Tray running?") }}
											</p>

											<div
												v-else
												class="max-h-56 overflow-y-auto rounded-lg border border-outline-gray-2 divide-y divide-outline-gray-1"
											>
												<label
													v-for="printer in printers"
													:key="printer"
													class="flex items-center gap-3 px-3 py-2.5 cursor-pointer hover:bg-surface-gray-1 transition-colors"
												>
													<input
														type="checkbox"
														class="w-4 h-4 text-blue-600 bg-white border-gray-300 rounded focus:ring-blue-500 focus:ring-1 cursor-pointer"
														:checked="isSelected(printer)"
														@change="togglePrinter(printer)"
													/>
													<span
														class="text-sm text-ink-gray-9 truncate"
														:title="printer"
													>
														{{ printer }}
													</span>
												</label>
											</div>

											<p class="text-xs text-muted">
												{{
													selectedCount === 0
														? __("Select one or more printers")
														: selectedCount === 1
															? __("1 printer selected")
															: __("{0} printers selected", [
																	selectedCount,
																])
												}}
											</p>

											<CheckboxField
												v-model="rememberDefault"
												:label="__('Remember as default printers')"
												:description="
													__(
														'Save this selection for auto-print and as the pre-selected options next time'
													)
												"
											/>
										</template>
									</div>
								</div>
							</div>
						</div>

						<div class="px-4 pb-7 pt-4 sm:px-6">
							<div class="flex justify-end gap-2 w-full">
								<Button variant="subtle" @click="cancel">
									{{ __("Cancel") }}
								</Button>
								<Button
									variant="solid"
									theme="blue"
									:disabled="
										selectedCount === 0 ||
										preparing ||
										printers.length === 0
									"
									@click="confirm"
								>
									{{ __("Print") }}
								</Button>
							</div>
						</div>
					</DialogContent>
				</div>
			</DialogOverlay>
		</DialogPortal>
	</DialogRoot>
</template>

<script setup>
import LucideX from "~icons/lucide/x"
import {
	DialogClose,
	DialogContent,
	DialogOverlay,
	DialogPortal,
	DialogRoot,
	DialogTitle,
} from "reka-ui"
import { Button } from "frappe-ui"
import CheckboxField from "@/components/settings/CheckboxField.vue"
import { usePrinterPicker } from "@/composables/usePrinterPicker"

const {
	visible,
	title,
	selectedCount,
	allSelected,
	rememberDefault,
	preparing,
	qzConnected,
	qzConnecting,
	printers,
	loadingPrinters,
	handleConnect,
	refreshPrinters,
	isSelected,
	togglePrinter,
	selectAll,
	clearSelection,
	confirm,
	cancel,
} = usePrinterPicker()

function onPointerDownOutside(event) {
	// Keep the underlying invoice dialog open; only dismiss the printer picker.
	event.preventDefault()
	cancel()
}
</script>
