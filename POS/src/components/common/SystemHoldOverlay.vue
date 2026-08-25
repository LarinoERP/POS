<template>
	<div v-if="HOLD_ACTIVE" class="system-hold-overlay">
		<div class="system-hold-card">
			<div class="system-hold-icon">&#9888;</div>
			<h1 class="system-hold-title">System On Hold</h1>
			<p class="system-hold-text">
				Access to this system has been temporarily suspended pending an
				outstanding balance under the service agreement.
			</p>
			<p class="system-hold-text">
				Please contact
				<a class="system-hold-link" :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>
				for more information. Your data is safe and fully retained.
			</p>
		</div>
	</div>
</template>

<script setup>
// Set to false and rebuild once the outstanding balance is settled.
const HOLD_ACTIVE = true;
const CONTACT_EMAIL = "waleedsabry.abohashima@gmail.com";
</script>

<style scoped>
.system-hold-overlay {
	position: fixed;
	inset: 0;
	z-index: 2147483647;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 1.5rem;
	background: rgba(15, 23, 42, 0.96);
	backdrop-filter: blur(6px);
}
.system-hold-card {
	max-width: 32rem;
	width: 100%;
	background: #ffffff;
	border-radius: 1rem;
	padding: 2.5rem 2rem;
	text-align: center;
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}
.system-hold-icon {
	font-size: 3rem;
	line-height: 1;
	margin-bottom: 1rem;
}
.system-hold-title {
	font-size: 1.5rem;
	font-weight: 700;
	margin: 0 0 1rem;
	color: #0f172a;
}
.system-hold-text {
	font-size: 1rem;
	line-height: 1.6;
	color: #334155;
	margin: 0 0 1rem;
}
.system-hold-link {
	color: #2563eb;
	font-weight: 600;
	text-decoration: none;
}
.system-hold-link:hover {
	text-decoration: underline;
}
</style>
