<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="pinkTheme" :locale="zhCN">
    <n-global-style />
    <n-notification-provider>

      <Rank class="rank"/>

    </n-notification-provider>
  </n-config-provider>
</template>

<script setup>
import {
  darkTheme,
  zhCN,
  NConfigProvider,
  NGlobalStyle,
  NNotificationProvider,
} from 'naive-ui';
import Rank from './components/Rank.vue';
import Poster from './components/Poster.vue';

const pinkTheme = {
  common: {
    primaryColor: '#ff2075',
    primaryColorHover: '#FF69B4',
    primaryColorPressed: '#C71585',
    primaryColorSuppl: '#ff2075',
    borderRadius: '8px',
  }
};

</script>

<style>
.rank {
  height: 100vh;
  overflow: hidden;
}
</style>
