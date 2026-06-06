async function signup() {
    let name= document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    let response= await fetch('http://127.0.0.1:5000/signup',{
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

    let response = await fetch('http://127.0.0.1:5000/login', {
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
        window.location.href = '/shop';
    } else {
        alert(data.message);
    }
}