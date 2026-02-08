<template>
  <el-container>
    <el-header>
      <h2>某大学某协会</h2>
      <el-button @click="$router.push('/login')">登录</el-button>
      <el-button @click="$router.push('/register')">注册</el-button>
    </el-header>
    <el-main>
      <el-row>
        <el-col :span="12">
          <h3>协会简介</h3>
          <div>{{ about.intro }}</div>
          <h3>协会活动</h3>
          <ul>
            <li v-for="a in activities" :key="a.title">{{ a.title }} - {{ a.date }} - {{ a.desc }}</li>
          </ul>
        </el-col>
        <el-col :span="12">
          <h3>协会资讯</h3>
          <NewsList :news="news" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import NewsList from '../components/NewsList.vue';

const about = ref({});
const activities = ref([]);
const news = ref([]);

onMounted(async () => {
  about.value = (await api.getAbout()).data;
  activities.value = (await api.getActivities()).data.activities;
  news.value = (await api.getNews()).data.news;
});
</script> 