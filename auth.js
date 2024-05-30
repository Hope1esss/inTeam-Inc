import CONFIG from 'config';


function redirectToVKAuth() {
    const client_id = '51899044'; // Замените на ваш client_id
    const redirect_uri = encodeURIComponent(CONFIG.REDIRECT_URI); // URL, на который будет передан code
    const display = 'page'; // Отображение в отдельном окне
    const scope = 'friends'; // Права доступа, которые вы хотите запросить
    const response_type = 'code'; // Тип ответа - code
    const v = '5.131'; // Версия API

    const authUrl = `https://oauth.vk.com/authorize?client_id=${client_id}&display=${display}&redirect_uri=${redirect_uri}&scope=${scope}&response_type=${response_type}&v=${v}`;
    window.location.href = authUrl;
}
