
async function adminlogin() {
    // get values first
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    // then validations
    if (email === '' || password === '') {
        alert('please fill all fields');
        return;
    }
    if (!email.includes('@') || !email.includes('.')) {
        alert('please enter a valid email');
        return;
    }

    // then fetch
    let response = await fetch('https://pagal-cart.onrender.com/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: password })
    });
    
    let data = await response.json();
    
    if (data.token) {
        if (data.role !== 'admin') {
            alert('Access denied! This is admin only.');
            return;
        }
        localStorage.setItem('token', data.token);
        localStorage.setItem('user_id', data.id);
        localStorage.setItem('role', data.role);
        localStorage.setItem('user_name', data.name);
        window.location.href = '/admin';
    } else {
        alert(data.message);
    }
}
