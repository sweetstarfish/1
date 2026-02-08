import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000', // Flask后端地址
  withCredentials: true
});

export default {
  // 用户相关
  register: data => api.post('/user/register', data),
  login: data => api.post('/user/login', data),
  getProfile: () => api.get('/user/profile'),
  updateProfile: data => api.post('/user/profile', data),
  getFriends: () => api.get('/user/friends'),
  addFriend: data => api.post('/user/friends', data),
  deleteFriend: data => api.delete('/user/friends', { data }),
  postLog: data => api.post('/user/log', data),
  getLogs: () => api.get('/user/logs'),
  uploadPhoto: (formData) => api.post('/user/upload_photo', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),

  // 管理员相关
  getUsers: () => api.get('/admin/users'),
  setRole: data => api.post('/admin/set_role', data),
  approve: data => api.post('/admin/approve', data),

  // 公共内容
  getAbout: () => api.get('/public/about'),
  getActivities: () => api.get('/public/activities'),
  getNews: (page = 1, per_page = 10) => api.get('/public/news', { params: { page, per_page } }),
  getNewsDetail: id => api.get(`/public/news/${id}`)
}; 