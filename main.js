document.addEventListener('DOMContentLoaded', async () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');

    const userInfo = document.getElementById('user-info');
    const userAvatar = document.getElementById('user-avatar');
    const userName = document.getElementById('user-name');
    const authButtons = document.getElementById('auth-buttons');


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
            userName.textContent = data.username;
            userAvatar.textContent = data.username.slice(0, 2).toUpperCase();

            userInfo.style.display = 'flex';
            authButtons.style.display = 'none';
        } catch (error) {
            console.error('Error during token check:', error);
            document.getElementById('message').textContent = error.message;
        }
    }


    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Проверка наличия токена при загрузке стран

            try {
                const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({username, password}),
                    credentials: 'include'
                });

                const data = await response.json();
                if (!response.ok) {
                    if (response.status === 422) {
                        const errors = data.detail.map(e => `${e.loc[1]}: ${e.msg}`).join('\n');
                        throw new Error(errors);
                    } else if (response.status === 400 && data.detail === "Username already exists") {
                        throw new Error("Username already exists. Please choose another one.");
                    } else {
                        throw new Error(data.detail || 'Registration failed');
                    }
                }
                document.getElementById('message').textContent = data.message;

                window.location.href = 'index.html';
            } catch (error) {
                document.getElementById('message').textContent = error.message;
            }
        });
    }


    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({username, password}),
                    credentials: 'include'
                });

                const data = await response.json();
                if (!response.ok) {
                    if (response.status === 422) {
                        const errors = data.detail.map(e => `${e.loc[1]}: ${e.msg}`).join('\n');
                        throw new Error(errors);
                    } else if (response.status === 400 && data.detail === "Invalid username or password") {
                        throw new Error("Invalid username or password. Please try again.");
                    } else {
                        throw new Error(data.detail || 'Login failed');
                    }
                }
                document.getElementById('message').textContent = data.message;

                window.location.href = 'index.html';
            } catch (error) {
                document.getElementById('message').textContent = error.message;
            }
        });
    }
});
