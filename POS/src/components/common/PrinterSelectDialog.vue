<template>
	<Dialog
		v-model="visible"
		:options="{ title: title || __('Select Printer'), size: 'sm' }"
	>
		<template #body-content>
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

				<div v-if="preparing" class="text-sm text-muted text-center py-2">
					{{ __("Loading printers...") }}
				</div>

				<template v-else>
					<SelectField
						v-model="selected"
						:label="__('Printer')"
						:options="printerOptions"
						:description="
							printers.length === 0
								? __('No printers found. Is QZ Tray running?')
								: __('Choose where to send this print job')
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
		</template>

		<template #actions>
			<div class="flex justify-end gap-2 w-full">
				<Button variant="subtle" @click="cancel">
					{{ __("Cancel") }}
				</Button>
				<Button
					variant="solid"
					theme="blue"
					:disabled="!selected || preparing || printers.length === 0"
					@click="confirm"
				>
					{{ __("Print") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
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
</script>
