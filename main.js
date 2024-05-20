async function checkToken() {
    const cookies = document.cookie.split('; ').reduce((prev, current) => {
        const [name, ...value] = current.split('=');
        prev[name] = value.join('=');
        return prev;
    }, {});

    if (cookies.access_token) {
        try {
            const response = await fetch('http://localhost:8000/api/v1/auth/check-token', {
                method: 'GET',
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user info');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error during token check:', error);
            return null;
        }
    } else {
        return null;
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    const userInfo = document.getElementById('user-info');
    const userAvatar = document.getElementById('user-avatar');
    const userName = document.getElementById('user-name');
    const authButtons = document.getElementById('auth-buttons');

    const userData = await checkToken();

    if (userData) {
        userName.textContent = userData.username;
        userAvatar.textContent = userData.username[0].toUpperCase();

        userInfo.style.display = 'flex';
        authButtons.style.display = 'none';
    }

    if (userData && (window.location.pathname === '/sign.html' || window.location.pathname === '/login.html')) {
        window.location.href = 'index.html';
    }
});
