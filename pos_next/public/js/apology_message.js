// One-time personal message for a specific user, shown once per device.
// Keep in sync with POS/src/components/common/ApologyMessage.vue
(() => {
	const RECIPIENT = "afreenlarino@gmail.com";
	const STORAGE_KEY = "larino_apology_message_seen";

	$(document).on("startup", () => {
		if (frappe.session.user !== RECIPIENT) return;
		if (localStorage.getItem(STORAGE_KEY)) return;

		const dialog = new frappe.ui.Dialog({
			title: "A personal note from WaleedAboHashima 🤍",
			fields: [
				{
					fieldtype: "HTML",
					options: `
						<div style="font-size: 15px; line-height: 1.7; padding: 4px 2px;">
							<p>Dear Afreen,</p>
							<p>I owe you a sincere apology. I shut the system down in the middle of your
							working day without any warning, and that was wrong of me. Whatever was going on
							between us, you and your team didn't deserve to be caught off guard during
							service, with customers waiting.</p>
							<p>I've felt bad about it ever since. I truly care about Larino and about the
							people who rely on this system every day, and I let you down that day.</p>
							<p>You have my word: it will never happen again. If anything ever needs to be
							sorted out between us, I'll come and talk to you first.</p>
							<p>Thank you for your patience, and for trusting me with Larino.
							I'm grateful to keep working with you.</p>
							<p>With respect and gratitude,<br><b>WaleedAboHashima</b></p>
						</div>`,
				},
			],
			primary_action_label: "Thank you, WaleedAboHashima",
			primary_action: () => dialog.hide(),
		});
		dialog.onhide = () => localStorage.setItem(STORAGE_KEY, "1");
		dialog.show();
	});
})();
