<template>
    <n-spin :show="isLoading">
        <n-flex vertical align="center" class="container">
            <Poster style="z-index: 100;" ref="posterRef" v-show="false" />
            <n-flex justify="space-between" align="center" style="width: 100%">
                <div class="header-item"></div>
                <h1 class="header">选出你的年度新番 Top3!</h1>
                <a href="https://github.com/AcuLY/Annual-Top3" target="_blank" class="header-item">
                    <img src="/github.png" alt="Github">
                </a>
            </n-flex>

            <n-flex justify="center" class="input-container" size="large">
                <div>
                    <n-input id="user-id" v-model:value="userId" style="border-radius: 8px 0 0 8px; margin-left: 12px;"
                        type="text" placeholder="Bangumi UID (不是昵称)" />
                    <n-button @click="fetchAnimeList" quaternary class="fetch">
                        读取收藏
                    </n-button>
                </div>

                <n-flex>
                    <h3 id="nickname" style="margin: 0 -10px 0 10px; transform: translateY(4px);">昵称</h3>
                    <n-input v-model:value="userNickname" type="text" placeholder="海报上的昵称"
                        style="margin-left: 8px; width: 120px;" />
                </n-flex>

                <n-button @click="exportPoster" secondary type="success" style="width: 100px;">
                    导出海报
                </n-button>
            </n-flex>

            <n-divider style="margin: 20px 0 10px 0;" />

            <n-flex class="rank-container" justify="center" wrap="wrap" size="large">
                <!-- 正向 Top3 -->
                <div class="rank-card">
                    <div class="title-top3">正向 Top3</div>
                    <div class="positive-negative-container">
                        <div v-for="(anime, index) in positiveList" :key="index" :ref="el => positiveRefs[index] = el">
                            <n-flex vertical>
                                <div class="slot-wrapper">
                                    <span v-if="anime.id !== 0" class="slot-remove"
                                        @click.stop="clearSlot(positiveList, index)">
                                        ×
                                    </span>

                                    <n-tooltip trigger="hover" v-if="anime.id !== 0">
                                        <template #trigger>
                                            <img :src="getImageSrc(anime)" class="slot-image"
                                                @dragstart="onDragStartFromSlot(index, positiveList, $event)"
                                                @dragover.prevent @drop="onDrop(index, positiveList, $event)"
                                                @touchstart="onTouchStartFromSlot(positiveList, index, anime, $event)"
                                                @touchmove.prevent @click="onSlotClick(positiveList, index)">

                                        </template>
                                        {{ getPrimaryName(anime) }}
                                    </n-tooltip>

                                    <div v-else class="slot" @dragover.prevent
                                        @drop="onDrop(index, positiveList, $event)"
                                        @click="onSlotClick(positiveList, index)"></div>
                                </div>

                                <h1 class="rank-number" :style="{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    margin: 0,
                                    color: index === 0 ? '#B7B7B7' : index === 1 ? '#FFE562' : '#BF7B2F'
                                }">
                                    {{ index === 0 ? 2 : index === 1 ? 1 : 3 }}
                                </h1>
                            </n-flex>
                        </div>
                    </div>
                </div>

                <!-- 反向 Top3 -->
                <div class="rank-card">
                    <div class="title-top3">反向 Top3</div>
                    <div class="positive-negative-container">
                        <div v-for="(anime, index) in negativeList" :key="index" :ref="el => negativeRefs[index] = el">
                            <n-flex vertical>
                                <div class="slot-wrapper">
                                    <span v-if="anime.id !== 0" class="slot-remove"
                                        @click.stop="clearSlot(negativeList, index)">
                                        ×
                                    </span>

                                    <n-tooltip trigger="hover" v-if="anime.id !== 0">
                                        <template #trigger>
                                            <img :src="getImageSrc(anime)" class="slot-image"
                                                @dragstart="onDragStartFromSlot(index, negativeList, $event)"
                                                @dragover.prevent @drop="onDrop(index, negativeList, $event)"
                                                @touchstart="onTouchStartFromSlot(negativeList, index, anime, $event)"
                                                @touchmove.prevent @click="onSlotClick(negativeList, index)">

                                        </template>
                                        {{ getPrimaryName(anime) }}
                                    </n-tooltip>

                                    <div v-else class="slot" @dragover.prevent
                                        @drop="onDrop(index, negativeList, $event)"
                                        @click="onSlotClick(negativeList, index)"></div>
                                </div>

                                <h1 class="rank-number" :style="{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    margin: 0,
                                    color: index === 0 ? '#B7B7B7' : index === 1 ? '#FFE562' : '#BF7B2F'
                                }">
                                    {{ index === 0 ? 2 : index === 1 ? 1 : 3 }}
                                </h1>
                            </n-flex>
                        </div>
                    </div>
                </div>
            </n-flex>

            <n-divider style="margin: 10px;" />

            <!-- 候选番剧列表 -->
            <section class="anime-list-section">
                <div class="anime-list-toolbar">
                    <div class="anime-list-title">
                        <n-flex style="width: 100%;">
                            <h2>候选番剧列表</h2>
                            <n-switch v-model:value="chooseFromCollectedAnime" :disabled="userList.length === 0"
                                :size="isMobile ? 'small' : 'large'"
                                :style="isMobile ? { fontSize: '12px', marginTop: '4px' } : { marginTop: '4px' }">
                                <template #checked>
                                    从收藏中选择
                                </template>
                                <template #unchecked>
                                    从收藏中选择
                                </template>
                            </n-switch>
                        </n-flex>
                        <p>列表按播出时间排序，拖拽或点击（先点动画再点名次）添加到 Top3</p>
                    </div>
                    <n-input v-model:value="searchQuery" :size="isMobile ? 'small' : 'large'" clearable
                        placeholder="搜索动画名称" />
                </div>

                <n-flex class="anime-list-container" draggable="true" @dragover.prevent @drop="onDropDelete($event)">
                    <template v-if="filteredAnimeList.length">
                        <div v-for="anime in filteredAnimeList" :key="anime.id" class="anime-item">
                            <n-tooltip trigger="hover">
                                <template #trigger>
                                    <img :src="getImageSrc(anime)"
                                        :class="clickSource && clickSource.id === anime.id ? 'selected-anime' : ''"
                                        @dragstart="onDragStartFromList(anime, $event)"
                                        @touchstart="onTouchStartFromList(anime, $event)" @touchmove.prevent
                                        @click="onListClick(anime)" loading="lazy" decoding="async" />
                                </template>
                                {{ getPrimaryName(anime) }}
                            </n-tooltip>
                            <div class="anime-name">{{ getPrimaryName(anime) }}</div>
                        </div>
                    </template>
                    <n-empty v-else class="anime-empty" description="没有找到匹配的动画" />
                </n-flex>
            </section>
        </n-flex>
    </n-spin>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue';
import {
    NFlex,
    NInput,
    NButton,
    NDivider,
    NSwitch,
    NSpin,
    NTooltip,
    NEmpty,
    useNotification
} from 'naive-ui';
import axios from 'axios';
import Poster from './Poster.vue';
import fullList from '../constant/2025.json';

/**
 * 基本状态
 */
const notify = useNotification();
const posterRef = ref(null);

const isMobile = window.innerWidth < 600;
const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

const isLoading = ref(false);

const userId = ref('');
const userNickname = ref('');
const userAvatar = ref('/avatar.jpg');

const chooseFromCollectedAnime = ref(false);
const userList = ref([]);

/**
 * 列表 & 搜索
 */
const animeList = computed(() =>
    chooseFromCollectedAnime.value ? userList.value : fullList
);

const searchQuery = ref('');
const filteredAnimeList = computed(() => {
    const source = animeList.value || [];
    const query = searchQuery.value.trim().toLowerCase();
    if (!query) return source;

    return source.filter(anime => {
        const nameCandidates = (anime.names || [])
            .filter(Boolean)
            .join(' ')
            .toLowerCase();
        return nameCandidates.includes(query);
    });
});

/**
 * Top3 相关
 */
const positiveList = ref([
    { id: 0, names: [] },
    { id: 0, names: [] },
    { id: 0, names: [] }
]);
const negativeList = ref([
    { id: 0, names: [] },
    { id: 0, names: [] },
    { id: 0, names: [] }
]);

const positiveRefs = ref([]);
const negativeRefs = ref([]);

const clickSource = ref(null);

/**
 * 通用工具
 */
const getPrimaryName = anime => {
    if (!anime) return '';
    if (anime.names?.length) {
        const primary = anime.names.find(Boolean);
        if (primary) return primary;
    }
    return anime.name || '';
};

const getImageSrc = (anime) => {
    if (!anime?.id) return ''
    return `/posters/${anime.id}.jpg`
}

/**
 * 点击选择逻辑（PC / Mobile 通用）
 */
const onListClick = anime => {
    clickSource.value =
        clickSource.value && clickSource.value.id === anime.id ? null : anime;
};

const onSlotClick = (slot, index) => {
    if (clickSource.value) {
        slot[index] = clickSource.value;
        clickSource.value = null;
    }
};

const clearSlot = (slot, index) => {
    const current = slot[index];
    if (current.id !== 0 && clickSource.value?.id === current.id) {
        clickSource.value = null;
    }
    slot[index] = { id: 0, names: [] };
};

/**
 * 桌面端拖拽逻辑（保持原有行为）
 */
const dragSource = ref(null);

const onDragStartFromList = (anime, event) => {
    dragSource.value = { type: 'list', data: anime };
    event.dataTransfer?.setData('application/json', JSON.stringify(anime));

    const dragImage = document.createElement('img');
    dragImage.src = getImageSrc(anime);
    dragImage.style.width = '100px';
    dragImage.style.height = '142px';
    dragImage.style.borderRadius = '10px';
    dragImage.style.opacity = '0.8';
    dragImage.style.border = '4px solid #FF1493';
    document.body.appendChild(dragImage);

    event.dataTransfer?.setDragImage(dragImage, 50, 71);
    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
};

const onDragStartFromSlot = (index, slot, event) => {
    dragSource.value = { type: 'slot', index, src: slot };
    event.dataTransfer?.setData('application/json', JSON.stringify(slot[index]));

    const dragImage = document.createElement('img');
    dragImage.src = getImageSrc(slot[index]);
    dragImage.style.width = '100px';
    dragImage.style.height = '142px';
    dragImage.style.borderRadius = '10px';
    dragImage.style.opacity = '0.8';
    dragImage.style.border = '4px solid #FF1493';
    document.body.appendChild(dragImage);

    event.dataTransfer?.setDragImage(dragImage, 50, 71);
    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
};

const onDrop = (index, slot, event) => {
    const data = event.dataTransfer?.getData('application/json');
    if (data) {
        const anime = JSON.parse(data);

        if (dragSource.value?.type === 'slot') {
            const sourceIndex = dragSource.value.index;
            const srcSlot = dragSource.value.src;
            const temp = srcSlot[sourceIndex];
            srcSlot[sourceIndex] = slot[index];
            slot[index] = temp;
        }

        slot[index] = anime;
    }
    dragSource.value = null;
};

const onDropDelete = event => {
    const data = event.dataTransfer?.getData('application/json');

    if (data && dragSource.value?.type === 'slot') {
        const sourceIndex = dragSource.value.index;
        const srcSlot = dragSource.value.src;
        srcSlot[sourceIndex] = { id: 0, names: [] };
    }

    dragSource.value = null;
};

/**
 * 移动端长按拖拽逻辑
 * - 长按触发拖动
 * - 全局 touchmove/touchend 控制 ghost image
 * - 手指松开后必定清理 ghost，不会悬停
 */
const LONG_PRESS_MS = 120;
const touchDragInfo = {
    active: false,
    anime: null,
    srcList: null,
    srcIndex: null,
    mode: null, // 'list' | 'slot'
    ghostEl: null,
    timerId: null
};

let windowTouchHandlersAttached = false;

const resetTouchDragInfo = () => {
    touchDragInfo.active = false;
    touchDragInfo.anime = null;
    touchDragInfo.srcList = null;
    touchDragInfo.srcIndex = null;
    touchDragInfo.mode = null;
    if (touchDragInfo.timerId) {
        clearTimeout(touchDragInfo.timerId);
        touchDragInfo.timerId = null;
    }
};

const cleanupGhost = () => {
    if (touchDragInfo.ghostEl?.parentNode) {
        touchDragInfo.ghostEl.parentNode.removeChild(touchDragInfo.ghostEl);
    }
    touchDragInfo.ghostEl = null;
};

const handleWindowTouchMove = (event) => {
    if (!touchDragInfo.ghostEl) return;

    // 阻止页面滚动 / 背景元素移动
    event.preventDefault();

    const touch = event.touches[0];
    if (!touch) return;

    touchDragInfo.ghostEl.style.left = `${touch.clientX - 40}px`;
    touchDragInfo.ghostEl.style.top = `${touch.clientY - 56}px`;
};

const handleWindowTouchEnd = event => {
    if (touchDragInfo.timerId) {
        clearTimeout(touchDragInfo.timerId);
        touchDragInfo.timerId = null;
    }

    detachWindowTouchHandlers();

    // 没进入拖拽态：视为普通点击，交给 click 事件处理
    if (!touchDragInfo.active) {
        resetTouchDragInfo();
        return;
    }

    const touch = event.changedTouches[0];
    if (touch) {
        const x = touch.clientX;
        const y = touch.clientY;
        handleTouchDrop(x, y);
    }

    cleanupGhost();
    resetTouchDragInfo();
};

const attachWindowTouchHandlers = () => {
    if (windowTouchHandlersAttached) return;
    window.addEventListener('touchmove', handleWindowTouchMove, { passive: false });
    window.addEventListener('touchend', handleWindowTouchEnd);
    window.addEventListener('touchcancel', handleWindowTouchEnd);
    windowTouchHandlersAttached = true;
};

const detachWindowTouchHandlers = () => {
    if (!windowTouchHandlersAttached) return;
    window.removeEventListener('touchmove', handleWindowTouchMove);
    window.removeEventListener('touchend', handleWindowTouchEnd);
    window.removeEventListener('touchcancel', handleWindowTouchEnd);
    windowTouchHandlersAttached = false;
};

const startLongPressDrag = (anime, srcList, srcIndex, mode, touch) => {
    if (!anime) return;
    resetTouchDragInfo();

    touchDragInfo.anime = anime;
    touchDragInfo.srcList = srcList;
    touchDragInfo.srcIndex = srcIndex;
    touchDragInfo.mode = mode;

    attachWindowTouchHandlers();

    touchDragInfo.timerId = window.setTimeout(() => {
        touchDragInfo.active = true;

        const img = document.createElement('img');
        img.src = getImageSrc(anime);
        img.style.position = 'fixed';
        img.style.width = '80px';
        img.style.height = '112px';
        img.style.left = `${touch.clientX - 40}px`;
        img.style.top = `${touch.clientY - 56}px`;
        img.style.pointerEvents = 'none';
        img.style.zIndex = '9999';
        img.style.borderRadius = '10px';
        img.style.opacity = '0.9';
        img.style.border = '4px solid #FF1493';

        document.body.appendChild(img);
        touchDragInfo.ghostEl = img;
    }, LONG_PRESS_MS);
};

const handleTouchDrop = (x, y) => {
    const anime = touchDragInfo.anime;
    if (!anime) return;

    const inRect = el => {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        return x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;
    };

    let placed = false;

    // 掉到正向 Top3
    positiveRefs.value.forEach((slotEl, index) => {
        if (placed || !slotEl) return;
        if (inRect(slotEl)) {
            if (touchDragInfo.mode === 'slot' && touchDragInfo.srcList) {
                touchDragInfo.srcList[touchDragInfo.srcIndex] = { id: 0, names: [] };
            }
            positiveList.value[index] = anime;
            placed = true;
        }
    });

    // 掉到反向 Top3
    if (!placed) {
        negativeRefs.value.forEach((slotEl, index) => {
            if (placed || !slotEl) return;
            if (inRect(slotEl)) {
                if (touchDragInfo.mode === 'slot' && touchDragInfo.srcList) {
                    touchDragInfo.srcList[touchDragInfo.srcIndex] = { id: 0, names: [] };
                }
                negativeList.value[index] = anime;
                placed = true;
            }
        });
    }

    // 从槽位拖动到列表区域视为删除
    if (!placed && touchDragInfo.mode === 'slot' && touchDragInfo.srcList) {
        const animeListContainer = document.querySelector('.anime-list-container');
        if (animeListContainer && inRect(animeListContainer)) {
            touchDragInfo.srcList[touchDragInfo.srcIndex] = { id: 0, names: [] };
        }
    }
};

// 绑定到列表和槽位的 touchstart
const onTouchStartFromList = (anime, event) => {
    if (!isTouchDevice) return;
    const touch = event.touches?.[0];
    if (!touch) return;
    startLongPressDrag(anime, null, null, 'list', touch);
};

const onTouchStartFromSlot = (slot, index, anime, event) => {
    if (!isTouchDevice) return;
    if (!anime || anime.id === 0) return;
    const touch = event.touches?.[0];
    if (!touch) return;
    startLongPressDrag(anime, slot, index, 'slot', touch);
};

/**
 * 远端数据获取
 */
const fetchAnimeList = () => {
    if (!userId.value.trim()) {
        notify.error({
            title: '请输入用户 ID',
            duration: 3000
        });
        return;
    }

    const url = `https://top3.bgmss.fun/2025?userid=${userId.value}`;

    isLoading.value = true;
    axios
        .get(url)
        .then(response => {
            const data = response.data['subjectIDs'];
            if (data.length === 0) {
                notify.warning({
                    title: '找不到 2025 年的收藏',
                    duration: 5000
                })
                return
            }

            let idSet = new Set(data)
            userList.value = []
            for (const subject of fullList) {
                if (idSet.has(subject.id)) {
                    userList.value.push(subject)
                }
            }

            chooseFromCollectedAnime.value = true;
            fetchNickname();

            notify.success({
                title: '读取成功',
                duration: 3000
            })
        })
        .catch(error => {
            const message = error.response?.data?.error;
            if (message === 'invalid userid') {
                notify.error({
                    title: 'ID 错误：请输入正确的用户 ID，注意不是用户昵称',
                    duration: 5000
                });
            } else {
                notify.error({
                    title: `未知错误：${error}`,
                    duration: 8000
                });
            }
        })
        .finally(() => {
            isLoading.value = false;
        });
};

const fetchNickname = () => {
    axios
        .get(`https://api.bgm.tv/v0/users/${userId.value}`)
        .then(response => {
            userNickname.value = response.data['nickname'];
            userAvatar.value = response.data['avatar']['large'];
        })
        .catch(() => {
            notify.error({
                title: '获取昵称失败，请手动填充',
                duration: 3000
            });
        });
};

/**
 * 导出海报
 */
const exportPoster = async () => {
    if (userNickname.value === '') {
        notify.warning({
            title: '请输入昵称',
            duration: 3000
        });
        return;
    }

    if (!posterRef.value) {
        notify.error({
            title: '导出失败，未知错误',
            duration: 5000
        });
        return;
    }

    isLoading.value = true;
    try {
        await posterRef.value.exportPng(
            userNickname.value,
            userAvatar.value,
            positiveList.value,
            negativeList.value
        );
        // 给浏览器保存时间
        setTimeout(() => {
            isLoading.value = false;
        }, 5000);
    } catch (error) {
        console.error('Error during export:', error);
        notify.warning({
            title: '导出失败，可能是网络问题或者服务器未开启',
            duration: 5000
        });
        isLoading.value = false;
    }
};

/**
 * 组件卸载时清理全局事件 & 悬浮元素
 */
onBeforeUnmount(() => {
    detachWindowTouchHandlers();
    cleanupGhost();
});
</script>

<style scoped>
.header {
    display: flex;
    justify-content: center;
    color: #fff;
    margin-top: 10px;
}

.header-item {
    width: 48px;
}

.header-item img {
    width: 36px;
}

@media (max-width: 600px) {
    .header {
        font-size: 22px;
    }

    .header-item {
        width: 28px;
    }

    .header-item img {
        width: 32px;
    }
}

#user-id {
    width: 190px;
    height: 35px;
}

.fetch {
    border-radius: 0 8px 8px 0;
    background-color: rgba(255, 97, 171, 0.48);
    color: #eee;
    transition: background-color 0.2s ease;
}

.fetch:hover {
    background-color: rgba(254, 109, 181, 0.618);
}

.container {
    display: flex;
    overflow-y: scroll;
    height: 100vh;
    gap: 24px;
    padding: 16px 24px 72px;
    background:
        radial-gradient(circle at top, rgba(205, 81, 147, 0.235), transparent 40%),
        linear-gradient(180deg, #0f0f1a 0%, #131324 35%, #0c0c12 100%);
    user-select: none;
}

.container::-webkit-scrollbar {
    width: 8px;
    background-color: rgba(16, 16, 24, 0.8);
}

.container::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff1491c4, #0c0c1200);
    border-radius: 6px;
}

.input-container {
    width: 80vw;
    padding: 0 12px;
    border-radius: 16px;
}

.rank-container {
    width: 100%;
    gap: 24px;
}

.rank-card {
    width: 380px;
    background: #c86ac00f;
    border-radius: 12px;
    max-width: 90vw;
    padding: 12px 6px;
}

.title-top3 {
    width: 100%;
    display: flex;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 12px;
}

.positive-negative-container {
    display: flex;
    justify-content: center;
    padding-top: 8px;
}

@media (max-width: 600px) {
    .rank-card {
        width: 300px;
        padding: 6px 6px;
    }

    .title-top3 {
        font-size: 18px;
        margin-bottom: 6px;
    }

    .rank-number {
        font-size: 16px;
    }
}

.slot-wrapper {
    position: relative;
    display: inline-flex;
    transition: transform 0.15s ease;
}

.slot-wrapper:hover {
    transform: translateY(-6px);
}

.slot-remove {
    position: absolute;
    top: -12px;
    right: 0px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #ff3881;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    cursor: pointer;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    transition:
        transform 0.12s ease,
        box-shadow 0.12s ease,
        background 0.12s ease;
    z-index: 100;
}

.slot-remove:hover {
    transform: scale(1.05);
    background: #ff5c9d;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45);
}

.slot {
    border: 2px dashed rgba(255, 255, 255, 0.2);
    width: 100px;
    height: 142px;
    box-sizing: border-box;
    border-radius: 12px;
    margin: 0px 10px 0px 10px;
    transition:
        border-color 0.2s,
        transform 0.2s;
    background: rgba(255, 255, 255, 0.02);
}

.slot:hover {
    border: 2px dashed #ff1493;
    transform: translateY(-1px);
}

.slot-image {
    width: 100px;
    height: 142px;
    border-radius: 12px;
    margin: 0px 10px 0px 10px;
    transition: box-shadow 0.15s ease;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
}

@media (max-width: 600px) {
    .slot {
        width: 75px;
        height: 106.5px;
        border-radius: 8px;
    }

    .slot-image {
        width: 75px;
        height: 106.5px;
        border-radius: 8px;
        margin: 0px 10px 0px 10px;
    }
}

.slot-wrapper:hover .slot-image {
    box-shadow: 0px 0px 15px #ff1493;
    cursor: pointer;
}

.anime-list-section {
    width: 95%;
    padding: 0 24px 24px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.anime-list-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.anime-list-title {
    width: 100%;
}

.anime-list-title h2 {
    margin: 0;
    color: #fff;
}

.anime-list-title p {
    margin: 4px 0 0;
    color: rgba(255, 255, 255, 0.65);
    font-size: 14px;
}

.search-input :deep(.n-input__input) {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
}

.anime-list-container {
    width: 100%;
    flex: 1;
    min-height: 40vh;
    max-height: 80vh;
    padding: 12px 0;
    box-sizing: border-box;
    overflow-y: auto;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
}

.anime-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 75px;
    gap: 8px;
    margin-right: 1px;
}

.anime-list-container img {
    width: 75px;
    height: 106.5px;
    border-radius: 12px;
    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.5);
}

.anime-list-container::-webkit-scrollbar {
    background-color: rgba(16, 16, 24, 0.8);
}

.anime-list-container::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff14917a, rgb(16, 16, 24));
}

@media (max-width: 600px) {
    .anime-list-title h2 {
        font-size: 16px;
    }

    .anime-list-title p {
        font-size: 12px;
    }

    .anime-list-container img {
        width: 55px;
        height: 78px;
        border-radius: 10px;
        transition: all 0.1s;
    }

    .anime-item {
        width: 55px;
        gap: 4px;
        margin-right: -4px;
    }
}

.anime-list-container img:hover {
    box-shadow: 0px 0px 15px #ff1493;
    cursor: pointer;
    transform: translateY(-6px);
}

.anime-name {
    width: 100%;
    color: rgba(255, 255, 255, 0.838);
    font-size: 12px;
    text-align: center;
    line-height: 1.3;
    letter-spacing: 0.5px;
    font-weight: 500;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    min-height: 2.6em;
    margin-bottom: 4px;
}

@media (max-width: 600px) {
    .anime-name {
        font-size: 11px;
    }
}

.selected-anime {
    box-shadow: 0px 0px 15px #ff1493;
    border: 2px solid #ff1493;
    box-sizing: border-box;
}

.anime-list-container::-webkit-scrollbar {
    background-color: rgb(16, 16, 20);
    width: 8px;
}

.anime-list-container::-webkit-scrollbar-thumb {
    background-color: rgb(50, 50, 50);
    border-radius: 5px;
}

.anime-empty {
    width: 100%;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.65);
}
</style>
