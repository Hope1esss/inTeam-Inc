import CONFIG from "./config.js";


document.addEventListener('DOMContentLoaded', async () => {
    const vkLoginButton = document.getElementById('vk-login-btn');
    vkLoginButton.addEventListener('click', redirectToVKAuth);
    console.log('VK Login button event listener added');
});

function redirectToVKAuth() {
    const client_id = CONFIG.CLIENT_ID; // Замените на ваш client_id
    const redirect_uri = CONFIG.REDIRECT_URI; // URL, на который будет передан code
    const display = 'page'; // Отображение в отдельном окне
    const scope = 'friends'; // Права доступа, которые вы хотите запросить
    const response_type = 'code'; // Тип ответа - code
    const v = '5.131'; // Версия API

    const authUrl = `https://oauth.vk.com/authorize?client_id=${client_id}&display=${display}&redirect_uri=${encodeURIComponent(redirect_uri)}&scope=${scope}&response_type=${response_type}&v=${v}`;
    console.log('Redirecting to VK Auth URL:', authUrl);
    window.location.href = authUrl;
}
