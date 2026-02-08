// 会员空间页面JavaScript功能

// 用户搜索功能
let allUsers = [];

// 页面加载时获取所有用户
window.addEventListener('load', function() {
    fetch('/user/users')
        .then(response => response.json())
        .then(data => {
            allUsers = data.users;
            displayUsers(allUsers);
        })
        .catch(error => {
            console.error('获取用户列表失败:', error);
        });
});

// 搜索输入框事件
document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const filteredUsers = allUsers.filter(user => 
        user.username.toLowerCase().includes(searchTerm) || 
        user.nickname.toLowerCase().includes(searchTerm)
    );
    displayUsers(filteredUsers);
});

// 显示用户列表
function displayUsers(users) {
    const userList = document.getElementById('userList');
    if (users.length === 0) {
        userList.innerHTML = '<p style="color: #666; text-align: center;">没有找到用户</p>';
        return;
    }
    
    userList.innerHTML = users.map(user => `
        <div class="user-item">
            <div class="user-info">
                <strong>${user.nickname}</strong>
                <br>
                <small>@${user.username}</small>
                ${user.tags ? `<br><small class="user-tags">${user.tags}</small>` : ''}
            </div>
            <div>
                ${user.is_friend ? 
                    '<span class="friend-status">已是好友</span>' : 
                    `<button onclick="addFriend('${user.username}')" class="add-friend-btn">添加好友</button>`
                }
            </div>
        </div>
    `).join('');
}

// 添加好友
function addFriend(username) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/user/friend/add';
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'friend_name';
    input.value = username;
    
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
} 