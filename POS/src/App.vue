<template>
	<div>
		<router-view :key="translationVersion" />
		<Toast />
		<PrinterSelectDialog />
		<ApologyMessage />
	</div>
</template>

<script setup>
import Toast from "@/components/common/Toast.vue";
import PrinterSelectDialog from "@/components/common/PrinterSelectDialog.vue";
import ApologyMessage from "@/components/common/ApologyMessage.vue";
import { translationVersion } from "@/utils/translation";
</script>
