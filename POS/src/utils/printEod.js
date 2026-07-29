import { silentPrintDoc } from "./printInvoice";

const EOD_PRINT_FORMAT = "POS Next EOD Report";

export async function printEODReport(closingShiftName, printerName = null) {
	await silentPrintDoc(
		"POS Closing Shift",
		closingShiftName,
		EOD_PRINT_FORMAT,
		printerName,
	);
}
