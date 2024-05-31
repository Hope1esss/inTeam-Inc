import CONFIG from "./config.js";


function redirectToVKAuth() {
    const client_id = CONFIG.CLIENT_ID; // Замените на ваш client_id
    const redirect_uri = encodeURIComponent(CONFIG.REDIRECT_URI); // URL, на который будет передан code
    const display = 'page'; // Отображение в отдельном окне
    const scope = 'friends'; // Права доступа, которые вы хотите запросить
    const response_type = 'code'; // Тип ответа - code

    const authUrl = `https://oauth.vk.com/authorize?client_id=${client_id}&display=${display}&redirect_uri=${redirect_uri}&scope=${scope}&response_type=${response_type}`;
    window.location.href = authUrl;
}
