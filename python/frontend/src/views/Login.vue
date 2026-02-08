<template>
  <el-form :model="form" label-width="60px" style="max-width:300px;margin:40px auto;">
    <el-form-item label="用户名">
      <el-input v-model="form.username" />
    </el-form-item>
    <el-form-item label="密码">
      <el-input v-model="form.password" type="password" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="login">登录</el-button>
    </el-form-item>
    <el-alert v-if="msg" :title="msg" type="error" show-icon />
  </el-form>
</template>
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
const router = useRouter();
const form = ref({ username: '', password: '' });
const msg = ref('');
const login = async () => {
  try {
    await api.login(form.value);
    router.push('/dashboard');
  } catch (e) {
    msg.value = e.response?.data?.msg || '登录失败';
  }
};
</script> 