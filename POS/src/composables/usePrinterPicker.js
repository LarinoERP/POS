import { computed, ref, watch } from "vue"
import { useQzTray } from "@/composables/useQzTray"
import { getSavedPrinterNames, savePrinterNames } from "@/utils/qzTray"

const visible = ref(false)
const title = ref("")
/** @type {import('vue').Ref<string[]>} */
const selected = ref([])
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
 * Promise-based multi-printer picker for silent QZ Tray prints.
 * Resolves to string[] of selected printers, or null if cancelled.
 * Shared singleton — mount PrinterSelectDialog once (e.g. App.vue).
 */
export function usePrinterPicker() {
	const qz = useQzTray()

	const selectedCount = computed(() => selected.value.length)
	const allSelected = computed(
		() =>
			qz.printers.value.length > 0 &&
			selected.value.length === qz.printers.value.length,
	)

	function isSelected(name) {
		return selected.value.includes(name)
	}

	function togglePrinter(name) {
		const idx = selected.value.indexOf(name)
		if (idx === -1) {
			selected.value = [...selected.value, name]
		} else {
			selected.value = selected.value.filter((p) => p !== name)
		}
	}

	function selectAll() {
		selected.value = [...qz.printers.value]
	}

	function clearSelection() {
		selected.value = []
	}

	async function requestPrinter(options = {}) {
		const dialogTitle = options.title || __("Select Printers")

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

		const saved = getSavedPrinterNames().filter((n) =>
			qz.printers.value.includes(n),
		)
		selected.value =
			saved.length > 0 ? [...saved] : [qz.printers.value[0]]
		rememberDefault.value = 0
		title.value = dialogTitle
		visible.value = true

		return new Promise((resolve) => {
			resolvePromise = resolve
		})
	}

	function confirm() {
		if (selected.value.length === 0) return
		if (rememberDefault.value) {
			savePrinterNames(selected.value)
			qz.selectedPrinter.value = selected.value[0]
		}
		const resolver = resolvePromise
		resolvePromise = null
		const names = [...selected.value]
		visible.value = false
		resolver?.(names)
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
		selectedCount,
		allSelected,
		rememberDefault,
		preparing,
		qzConnected: qz.qzConnected,
		qzConnecting: qz.qzConnecting,
		printers: qz.printers,
		loadingPrinters: qz.loadingPrinters,
		handleConnect: qz.handleConnect,
		refreshPrinters: qz.refreshPrinters,
		isSelected,
		togglePrinter,
		selectAll,
		clearSelection,
		requestPrinter,
		confirm,
		cancel,
	}
}
