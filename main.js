import {redirectToVKAuth} from './auth.js';
import CONFIG from "./config.js";
document.addEventListener('DOMContentLoaded', function () {
    const username = localStorage.getItem('username');
    const avatarUrl = localStorage.getItem('avatar_url');
    const tokenExpiry = localStorage.getItem('token_expiry');

    // Проверка срока действия токена
    if (tokenExpiry && new Date().getTime() > parseInt(tokenExpiry)) {
        // Токен истек, очищаем данные пользователя и перенаправляем на страницу входа
        localStorage.removeItem('username');
        localStorage.removeItem('avatar_url');
        localStorage.removeItem('token_expiry');
        alert('Your session has expired. Please log in again.');
        window.location.href = 'login.html';
        return;
    }

    if (username && avatarUrl) {
        const userInfoDiv = document.getElementById('user-info');
        userInfoDiv.innerHTML = `
            <img src="${avatarUrl}" alt="User Avatar" class="user-avatar">
            <span class="user-name">${username}</span>
        `;
        document.getElementById('sign-up-button').style.display = 'none';
        document.getElementById('log-in-button').style.display = 'none';
    }

    document.getElementById('startButton').addEventListener('click', async function () {
        const userId = document.getElementById('linkInput').value;
        const accessToken = localStorage.getItem('vk_token');
        if (!userId || !accessToken) {
            alert('User ID and access token are required');
            redirectToVKAuth();
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/api/v1/user/user_info/${userId}?user_id=${userId}&access_token=${accessToken}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const result = await response.json();
            console.log(result);
            if (response.ok) {
                localStorage.setItem("user_id", userId);
                localStorage.setItem('vk_user_data', JSON.stringify(result));
                window.location.href = 'user_info.html';
            } else {
                throw new Error(result.detail || 'Unknown error');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    });
});
