<template>
  <el-container>
    <el-header>
      <h2>会员空间</h2>
      <el-button @click="logout">退出登录</el-button>
    </el-header>
    <el-main>
      <UserProfile :profile="profile" @update="fetchProfile" />
      <FriendList :friends="friends" @refresh="fetchFriends" />
      <LogList :logs="logs" @refresh="fetchLogs" />
      <PhotoUpload @uploaded="fetchPhotos" />
    </el-main>
  </el-container>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import UserProfile from '../components/UserProfile.vue';
import FriendList from '../components/FriendList.vue';
import LogList from '../components/LogList.vue';
import PhotoUpload from '../components/PhotoUpload.vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const profile = ref({});
const friends = ref([]);
const logs = ref([]);
const fetchProfile = async () => { profile.value = (await api.getProfile()).data; };
const fetchFriends = async () => { friends.value = (await api.getFriends()).data.friends; };
const fetchLogs = async () => { logs.value = (await api.getLogs()).data.logs; };
const fetchPhotos = async () => {};
const logout = () => { router.push('/login'); };
onMounted(() => { fetchProfile(); fetchFriends(); fetchLogs(); });
</script> 