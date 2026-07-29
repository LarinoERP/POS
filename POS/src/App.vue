<template>
	<div>
		<router-view :key="translationVersion" />
		<Toast />
		<PrinterSelectDialog />
	</div>
</template>

<script setup>
import Toast from "@/components/common/Toast.vue";
import PrinterSelectDialog from "@/components/common/PrinterSelectDialog.vue";
import { translationVersion } from "@/utils/translation";
</script>
