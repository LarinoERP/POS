<template>
	<div>
		<router-view :key="translationVersion" />
		<Toast />
		<PrinterSelectDialog />
		<SystemHoldOverlay />
	</div>
</template>

<script setup>
import Toast from "@/components/common/Toast.vue";
import PrinterSelectDialog from "@/components/common/PrinterSelectDialog.vue";
import SystemHoldOverlay from "@/components/common/SystemHoldOverlay.vue";
import { translationVersion } from "@/utils/translation";
</script>
