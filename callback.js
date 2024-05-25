document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    console.log('Authorization code:', code);

    if (code) {
        const proxyUrl = `http://localhost:8000/api/v1/auth/proxy_vk_access_token?code=${code}`;
        console.log('Requesting access token from proxy:', proxyUrl);

        try {
            const response = await fetch(proxyUrl, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json();
                document.getElementById('message').textContent = errorData.detail || 'Authorization failed';
                console.log('Error received:', errorData.detail);
            } else {
                const data = await response.json();
                console.log('Access token received:', data.access_token);

                // Сохранение access_token в cookies
                document.cookie = `access_token=${data.access_token}; path=/`;

                // Отправка access_token на сервер для создания или обновления пользователя
                await fetch('http://localhost:8000/api/v1/auth/vk', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ access_token: data.access_token }),
                }).then(() => {
                    console.log('Access token sent to server, redirecting to index.html');
                    // Перенаправление на index.html
                    window.location.href = 'index.html';
                }).catch(error => {
                    document.getElementById('message').textContent = 'Fetch error: ' + error.message;
                    console.log('Fetch error:', error.message);
                });
            }
        } catch (error) {
            document.getElementById('message').textContent = 'Fetch error: ' + error.message;
            console.log('Fetch error:', error.message);
        }
    } else {
        document.getElementById('message').textContent = 'No authorization code found';
        console.log('No authorization code found');
    }
});
