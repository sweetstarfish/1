<template>
  <el-container>
    <el-header>
      <el-menu mode="horizontal" :default-active="active" @select="onSelect">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/dashboard">会员空间</el-menu-item>
        <el-menu-item index="/admin">管理员后台</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()
const active = ref(route.path)
const onSelect = (index) => {
  router.push(index)
}
</script> 