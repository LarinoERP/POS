<template>
	<DialogRoot v-model:open="visible">
		<DialogPortal>
			<DialogOverlay
				class="fixed inset-0 bg-black-overlay-200 dark:bg-black-overlay-700 overflow-y-auto dialog-overlay printer-picker-overlay outline-none"
				:data-dialog="title || __('Select Printer')"
			>
				<div
					class="flex min-h-screen flex-col items-center justify-center px-4 py-4 text-center"
				>
					<DialogContent
						class="my-8 inline-block w-full max-w-sm transform overflow-hidden rounded-xl bg-surface-modal text-start align-middle shadow-xl dialog-content printer-picker-content focus-visible:outline-none"
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
													{{ title || __("Select Printer") }}
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
											<SelectField
												v-model="selected"
												:label="__('Printer')"
												:options="printerOptions"
												:description="
													printers.length === 0
														? __(
																'No printers found. Is QZ Tray running?'
															)
														: __(
																'Choose where to send this print job'
															)
												"
											/>

											<button
												type="button"
												@click="refreshPrinters"
												:disabled="loadingPrinters"
												class="self-start px-3 py-2 text-xs bg-inset hover:bg-inset rounded transition-colors"
											>
												{{ __("Refresh") }}
											</button>

											<CheckboxField
												v-model="rememberDefault"
												:label="__('Remember as default printer')"
												:description="
													__(
														'Save this printer for auto-print and as the pre-selected option next time'
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
										!selected || preparing || printers.length === 0
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
import SelectField from "@/components/settings/SelectField.vue"
import { usePrinterPicker } from "@/composables/usePrinterPicker"

const {
	visible,
	title,
	selected,
	rememberDefault,
	preparing,
	qzConnected,
	qzConnecting,
	printers,
	printerOptions,
	loadingPrinters,
	handleConnect,
	refreshPrinters,
	confirm,
	cancel,
} = usePrinterPicker()

function onPointerDownOutside(event) {
	// Keep the underlying invoice dialog open; only dismiss the printer picker.
	event.preventDefault()
	cancel()
}
</script>
