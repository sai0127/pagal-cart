async function signup() {
    let name= document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    let response= await fetch('https://pagal-cart.onrender.com/signup',{
        method: 'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({ name: name, email: email, password: password})
    });
    let data = await response.json();
    alert(data.message);

    if(data.message == 'user created'){
        window.location.href='/login'
    }
}

async function login() {
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

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
    }
}