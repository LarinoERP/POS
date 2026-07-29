import { ref, watch } from "vue"
import { useQzTray } from "@/composables/useQzTray"
import { getSavedPrinterName } from "@/utils/qzTray"

const visible = ref(false)
const title = ref("")
const selected = ref("")
const rememberDefault = ref(0)
const preparing = ref(false)

let resolvePromise = null

watch(visible, (open) => {
	if (!open && resolvePromise) {
		resolvePromise(null)
		resolvePromise = null
	}
})

/**
 * Promise-based printer picker for silent QZ Tray prints.
 * Shared singleton — mount PrinterSelectDialog once (e.g. App.vue).
 */
export function usePrinterPicker() {
	const qz = useQzTray()

	async function requestPrinter(options = {}) {
		const dialogTitle = options.title || __("Select Printer")

		preparing.value = true
		try {
			if (!qz.qzConnected.value) {
				await qz.handleConnect()
			}
			await qz.refreshPrinters()
		} finally {
			preparing.value = false
		}

		if (qz.printers.value.length === 0) {
			throw new Error(__("No printers found. Is QZ Tray running?"))
		}

		const saved = getSavedPrinterName()
		selected.value =
			saved && qz.printers.value.includes(saved)
				? saved
				: qz.printers.value[0]
		rememberDefault.value = 0
		title.value = dialogTitle
		visible.value = true

		return new Promise((resolve) => {
			resolvePromise = resolve
		})
	}

	function confirm() {
		if (!selected.value) return
		if (rememberDefault.value) {
			qz.selectedPrinter.value = selected.value
		}
		const resolver = resolvePromise
		resolvePromise = null
		visible.value = false
		resolver?.(selected.value)
	}

	function cancel() {
		const resolver = resolvePromise
		resolvePromise = null
		visible.value = false
		resolver?.(null)
	}

	return {
		visible,
		title,
		selected,
		rememberDefault,
		preparing,
		qzConnected: qz.qzConnected,
		qzConnecting: qz.qzConnecting,
		printers: qz.printers,
		printerOptions: qz.printerOptions,
		loadingPrinters: qz.loadingPrinters,
		handleConnect: qz.handleConnect,
		refreshPrinters: qz.refreshPrinters,
		requestPrinter,
		confirm,
		cancel,
	}
}
