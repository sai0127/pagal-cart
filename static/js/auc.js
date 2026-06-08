async function signup() {
    let name = document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    // validations first
    if (name === '' || email === '' || password === '') {
        alert('please fill all fields');
        return;
    }
    if (!email.includes('@') || !email.includes('.')) {
        alert('please enter a valid email');
        return;
    }
    if (password.length < 6) {
        alert('password must be at least 6 characters');
        return;
    }

    // then fetch
    let response = await fetch('https://pagal-cart.onrender.com/signup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: name, email: email, password: password})
    });
    let data = await response.json();
    alert(data.message);

    if(data.message == 'user created'){
        window.location.href = '/login'
    }
}


async function login() {
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
        localStorage.setItem('token', data.token);
        localStorage.setItem('user_id', 1);
        localStorage.setItem('role', data.role);
        alert("Login successful!");
        if (data.role === 'admin') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/shop';
        }
    } else {
        alert(data.message);
    }
}
