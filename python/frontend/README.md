# 前端项目结构（Vue3 + Element Plus）

## 目录结构

frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/                # 所有后端接口请求
│   │   └── index.js
│   ├── assets/
│   ├── components/
│   │   ├── NewsList.vue
│   │   ├── ActivityList.vue
│   │   ├── UserProfile.vue
│   │   ├── FriendList.vue
│   │   ├── LogList.vue
│   │   └── PhotoUpload.vue
│   ├── views/
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Dashboard.vue
│   │   ├── Admin.vue
│   │   └── ...
│   ├── router/
│   │   └── index.js
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js / vue.config.js

## 依赖安装

```bash
npm install vue@next vue-router@4 element-plus axios
```

## 启动方式

```bash
npm run dev
# 或
npm run serve
``` 