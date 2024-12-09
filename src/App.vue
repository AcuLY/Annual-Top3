<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="pinkTheme" :locale="zhCN">
    <n-global-style />
    <n-notification-provider>

      <a href="https://github.com/AcuLY/BangumiStaffStats" target="_blank" class="header-item">
        <img src="/github.png" alt="Github">
      </a>

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

.header-item {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}

.header-item img {
  width: 50px;
}

@media (max-width: 600px) {
  .header-item {
    top: 18px;
    right: 14px;
  }
  .header-item img {
    width: 32px;
  }
}
</style>
