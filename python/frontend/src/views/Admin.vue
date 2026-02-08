<template>
  <el-container>
    <el-header><h2>管理员后台</h2></el-header>
    <el-main>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="ID" width="50" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-select v-model="scope.row.role" @change="setRole(scope.row)">
              <el-option label="管理员" value="admin" />
              <el-option label="普通管理员" value="manager" />
              <el-option label="会员" value="member" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </el-main>
  </el-container>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
const users = ref([]);
const fetchUsers = async () => { users.value = (await api.getUsers()).data.users; };
const setRole = async (row) => { await api.setRole({ user_id: row.id, role: row.role }); fetchUsers(); };
onMounted(fetchUsers);
</script> 