<template>
<n-spin :show="isLoading">
    <n-flex vertical class="container">
        <Poster ref="posterRef" v-show="false"/>
        <h1 style="display: flex; justify-content: center; margin-bottom: 0px;">选出你的年度新番 Top3！</h1>

        <n-flex justify="center" class="input-container">
            <h3 style="margin: 0 -10px 0 0; transform: translateY(4px);">Bangumi ID :</h3>
            <n-input id="user-id" v-model:value="userId" type="text" placeholder="不是昵称" />

            <n-button id="fetch-button" @click="fetchAnimeList" type="primary" style="color: white;">
                获取 Bangumi 账户信息
            </n-button>

            <n-switch v-model:value="chooseFromCollectedAnime" :disabled="!userList.length > 0" size="large" style="transform: translateY(4px);">
                <template #checked>
                从收藏的新番中选择
                </template>
                <template #unchecked>
                从收藏的新番中选择
                </template>
            </n-switch>

            <h3 id="nickname" style="margin: 0 -10px 0 10px; transform: translateY(4px);">昵称 :</h3>
            <n-input id="user-id" v-model:value="userNickname" type="text" placeholder="昵称" />

            <n-button id="fetch-button" @click="exportPoster" secondary type="success">
                导出海报
            </n-button>
        </n-flex>

        <n-divider style="margin: 10px;" />

        <n-flex class="rank-container" justify="center">
            <n-flex vertical>
                <h2 style="display: flex; justify-content: center; margin: 0px;">正向 Top3</h2>

                <div class="positive-negative-container">
                    <div v-for="(anime, index) in positiveList" :key="index">
                        <n-flex vertical>
                            <img :src="anime.image" :alt="anime.name" :title="anime.name" class="slot-image" v-if="anime.id !== 0" @dragover.prevent
                                @dragstart="onDragStartFromSlot(index, positiveList, $event)" @drop="onDrop(index, positiveList, $event)" @click="onSlotClick(positiveList, index)">
                            <div v-else class="slot" @dragover.prevent @drop="onDrop(index, positiveList, $event)" @click="onSlotClick(positiveList, index)"></div>

                            <h1 :style="{ display: 'flex', justifyContent: 'center', margin: 0, color: index == 0 ? '#B7B7B7' : index == 1 ? '#FFE562' : '#BF7B2F' }">
                                {{ index == 0 ? 2 : index == 1 ? 1 : 3 }}
                            </h1>
                        </n-flex>
                    </div>
                </div>
            </n-flex>
            
            <n-flex vertical>
                <h2 style="display: flex; justify-content: center; margin: 0px;">反向 Top3</h2>

                <div class="positive-negative-container">
                    <div v-for="(anime, index) in negativeList" :key="index">
                        <n-flex vertical>
                            <img :src="anime.image" :alt="anime.name" :title="anime.name" class="slot-image" v-if="anime.id !== 0" @dragover.prevent
                                @dragstart="onDragStartFromSlot(index, negativeList, $event)" @drop="onDrop(index, negativeList, $event)" @click="onSlotClick(negativeList, index)">
                            <div v-else class="slot" @dragover.prevent @drop="onDrop(index, negativeList, $event)" @click="onSlotClick(negativeList, index)"></div>

                            <h1 :style="{ display: 'flex', justifyContent: 'center', margin: 0, color: index == 0 ? '#B7B7B7' : index == 1 ? '#FFE562' : '#BF7B2F' }">
                                {{ index == 0 ? 2 : index == 1 ? 1 : 3 }}
                            </h1>
                        </n-flex>
                    </div>
                </div>
            </n-flex>
            
        </n-flex>

        <n-divider style="margin: 10px;" />

        <n-flex class="anime-list-container">
            <div v-for="anime in animeList" :key="anime.id">
                <img :src="anime.image" :alt="anime.name" :class="clickSource && clickSource.name === anime.name ? 'selected-anime' : ''" :title="anime.name" @dragstart="onDragStartFromList(anime, $event)" @click="onListClick(anime)" loading="lazy">
            </div>
        </n-flex>

    </n-flex>
</n-spin>
</template>

<script setup>
import { ref, computed } from 'vue';
import {
    NFlex,
    NInput,
    NButton,
    NDivider,
    NSwitch,
    NSpin,
    useNotification
} from 'naive-ui';
import axios from 'axios';
import Poster from './Poster.vue';
import fullList from '../constant/full_list.json';

const posterRef = ref(null);

const notify = useNotification();

const isLoading = ref(false);

const userId = ref('');
const userNickname = ref('');
const userAvater = computed(() => {
    if (userId.value) {
        return `https://api.bgm.tv/v0/users/${userId.value}/avatar?type=large`;
    } else {
        return 'https://lain.bgm.tv/pic/user/m/icon.jpg';
    }
})
const chooseFromCollectedAnime = ref(false);

const fetchAnimeList = () => {
    if (!userId.value.trim()) {
        notify.error({
            title: "请输入用户 ID",
            duration: 3000
        });
        return;
    }

    const url = `https://search.bgmss.fun/statistics`;
    const params = {
        user_id: !userId.value ? '0' : userId.value,
        subject_type: 2,
        position: '',
        collection_types: [2, 3, 4, 5],
        tags: ['2024']
    }

    isLoading.value = true;
    axios.post(url, params)
        .then(response => {
            const data = response.data['all_subjects'];
            userList.value = data.map(subject => ({
                id: subject.id,
                name: subject.name_cn,
                image: subject.image.replace(/\/100\//, '/400/')
            }));

            chooseFromCollectedAnime.value = true;
            fetchNickname();
        })
        .catch(error => {
            const message = error.response?.data?.error;
            if (message === 'invalid userid') {
                notify.error({
                    title: "ID 错误：请输入正确的用户 ID，注意不是用户昵称",
                    duration: 5000
                });
            } else if (message === 'no information') {
                notify.error({
                    title: "找不到条目",
                    duration: 5000
                });
            } else {
                notify.error({
                    title: "查询失败，请检查网络，如果多次秒失败可能是服务器未开启",
                    duration: 8000
                });
            }
        })
        .finally(() => {
            isLoading.value = false;
        });
    
}

const fetchNickname = () => {
    axios.get(`https://api.bgm.tv/v0/users/${userId.value}`)
        .then(response => {
            userNickname.value = response.data['nickname'];
        })
        .catch(error => {
            notify.error({
                title: '获取昵称失败，请手动填充',
                duration: 3000
            })
        })
}

const userList = ref([]);
const animeList = computed(() => {
    return chooseFromCollectedAnime.value ? userList.value : fullList;
})

const positiveList = ref([
    {
        'id': 0,
        'name': '',
        'image': ''
    },
    {
        'id': 0,
        'name': '',
        'image': ''
    },
    {
        'id': 0,
        'name': '',
        'image': ''
    }
]);

const negativeList = ref([
    {
        'id': 0,
        'name': '',
        'image': ''
    },
    {
        'id': 0,
        'name': '',
        'image': ''
    },
    {
        'id': 0,
        'name': '',
        'image': ''
    }
]);

const clickSource = ref(null);
const dragSource = ref(null);

const onListClick = (anime) => {
    if (clickSource.value === anime) {
        clickSource.value = null;
    } else {
        clickSource.value = anime;
    }
}

const onSlotClick = (slot, index) => {
    if (clickSource.value) {
        slot[index] = clickSource.value;
        clickSource.value = null;
    }
}

const onDragStartFromList = (anime, event) => {
    dragSource.value = { type: 'list', data: anime };
    event.dataTransfer.setData('application/json', JSON.stringify(anime));

    const dragImage = document.createElement('img');
    dragImage.src = anime.image;
    dragImage.style.width = '100px';
    dragImage.style.height = '142px';
    dragImage.style.borderRadius = '10px';
    dragImage.style.opacity = '0.8';
    dragImage.style.border = '4px solid #FF1493';
    document.body.appendChild(dragImage);

    event.dataTransfer.setDragImage(dragImage, 50, 71);

    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
};

const onDragStartFromSlot = (index, slot, event) => {
    dragSource.value = { type: 'slot', index, src: slot };
    event.dataTransfer.setData('application/json', JSON.stringify(slot[index]));

    const dragImage = document.createElement('img');
    dragImage.src = slot[index].image;
    dragImage.style.width = '100px';
    dragImage.style.height = '142px';
    dragImage.style.borderRadius = '10px';
    dragImage.style.opacity = '0.8';
    dragImage.style.border = '4px solid #FF1493';
    document.body.appendChild(dragImage);

    event.dataTransfer.setDragImage(dragImage, 50, 71);

    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
};

const onDrop = (index, slot, event) => {
    const data = event.dataTransfer.getData('application/json');
    if (data) {
        const anime = JSON.parse(data);

        if (dragSource.value?.type === 'slot') {
            const sourceIndex = dragSource.value.index;
            const targetIndex = index;
            const srcSlot = dragSource.value.src;

            const temp = srcSlot[sourceIndex];
            srcSlot[sourceIndex] = slot[targetIndex];
            slot[targetIndex] = temp;
        }

        if (slot[index].id !== 0) {
            slot[index] = { id: 0, name: '', image: '' };
        }

        slot[index] = anime;
    }

    dragSource.value = null;
};

const exportPoster = () => {
    if (userNickname.value === '') {
        notify.warning({
            title: '请输入昵称',
            duration: 3000
        });
        return;
    }
    if (positiveList.value.some(anime => anime.id === 0) || negativeList.value.some(anime => anime.id === 0)) {
        notify.warning({
            title: '请填完全部空格',
            duration: 3000
        });
        return;
    }
    if (posterRef.value) {
        posterRef.value.exportPng(userNickname.value, userAvater.value, positiveList.value, negativeList.value);
    }
}

</script>

<style scoped>
#user-id {
    width: 120px;
    height: 35px;
    margin-left: 10px;
    margin-right: 10px;
}

.container {
    height: 100vh;
    padding: 0;
    display: flex;
    flex-direction: column;
    user-select: none;
}

.input-container {
    margin: 0;
}

.rank-container {
    overflow-y: auto;
}

.rank-container::-webkit-scrollbar {
    background-color: rgb(16, 16, 20);
    width: 8px;
}

.rank-container::-webkit-scrollbar-thumb {
    background-color: rgb(50, 50, 50);
    border-radius: 5px;
}

.slot {
    border: 2px dashed #ccc;
    width: 100px;
    height: 142px;
    box-sizing: border-box;
    border-radius: 10px;
    margin: 0px 10px 0px 10px;
}

.slot:hover {
    border: 2px dashed #FF1493;
}

.slot-image {
    width: 100px;
    height: 142px;
    border-radius: 10px;
    margin: 0px 10px 0px 10px;
    transition: all 0.1s;
}

.slot-image:hover {
    box-shadow: 0px 0px 15px #FF1493;
    cursor: pointer;
}

.positive-negative-container {
    display: flex;
    justify-content: center;
}


.anime-list-container {
    width: 100vw;
    flex: 1;
    min-height: 30vh;
    box-sizing: border-box;
    padding: 10px 0 10px 10px;
    overflow-y: auto;
}

.anime-list-container img {
    width: 75px;
    height: 106.5px;
    border-radius: 10px;
    transition: all 0.1s;
}

.anime-list-container img:hover {
    box-shadow: 0px 0px 10px #FF1493;
    cursor: pointer;
}

.selected-anime {
    box-shadow: 0px 0px 10px #FF1493;
    border: 2px solid #FF1493;
    box-sizing: border-box;
}

.anime-list-container::-webkit-scrollbar {
    background-color: rgb(16, 16, 20);
    width: 8px;
}

.anime-list-container::-webkit-scrollbar-thumb {
    background-color: rgb(50, 50, 50);
    border-radius: 5px;
    ;
}
</style>