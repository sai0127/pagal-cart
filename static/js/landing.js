if (localStorage.getItem('token')) {
    window.location.href = '/shop';
}
async function tryDemo() {
    let response = await fetch('https://pagal-cart.onrender.com/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'demo@pagalcart.com', password: 'demo1234' })
    });
    let data = await response.json();
    if (data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user_id', data.id);
        localStorage.setItem('role', data.role);
        localStorage.setItem('user_name', data.name);
        window.location.href = '/shop';
    }
}