<template>
	<Dialog v-model="visible" :options="{ size: 'lg' }">
		<template #body>
			<div class="p-6 text-[15px] leading-7 text-gray-800">
				<h3 class="text-xl font-semibold text-gray-900 mb-4">A personal note from Waleed 🤍</h3>
				<p class="mb-3">Dear Afreen,</p>
				<p class="mb-3">
					I owe you a sincere apology. I shut the system down in the middle of your working day
					without any warning, and that was wrong of me. Whatever was going on between us, you
					and your team didn't deserve to be caught off guard during service, with customers
					waiting.
				</p>
				<p class="mb-3">
					I've felt bad about it ever since. I truly care about Larino and about the people who
					rely on this system every day, and I let you down that day.
				</p>
				<p class="mb-3">
					You have my word: it will never happen again. If anything ever needs to be sorted out
					between us, I'll come and talk to you first.
				</p>
				<p class="mb-3">
					Thank you for your patience, and for trusting me with Larino. I'm grateful to keep
					working with you.
				</p>
				<p class="mb-5">With respect and gratitude,<br /><b>Waleed</b></p>
				<div class="flex justify-end">
					<Button variant="solid" @click="visible = false">Thank you, Waleed</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
// One-time personal message for a specific user, shown once per device.
// Keep in sync with pos_next/public/js/apology_message.js
import { session } from "@/data/session";
import { Button, Dialog } from "frappe-ui";
import { ref, watch } from "vue";

const RECIPIENT = "afreenlarino@gmail.com";
const STORAGE_KEY = "larino_apology_message_seen";

const visible = ref(false);

watch(
	() => session.user,
	(user) => {
		if (user === RECIPIENT && !localStorage.getItem(STORAGE_KEY)) {
			visible.value = true;
		}
	},
	{ immediate: true }
);

watch(visible, (open) => {
	if (!open) markSeen();
});

function markSeen() {
	localStorage.setItem(STORAGE_KEY, "1");
}
</script>
