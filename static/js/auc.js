async function sendOTP() {
    let name = document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    // validations
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

    // send OTP
    let response = await fetch('https://pagal-cart.onrender.com/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    });
    let data = await response.json();
    
    if (data.message === 'OTP sent!') {
        alert('OTP sent to your email!');
        document.getElementById('signup-form').style.display = 'none';
        document.getElementById('otp-form').style.display = 'block';
    } else {
        alert('Failed to send OTP');
    }
}

async function verifyAndSignup() {
    let name = document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let otp = document.getElementById('otp').value;

    // verify OTP first
    let otpResponse = await fetch('https://pagal-cart.onrender.com/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, otp: otp })
    });
    let otpData = await otpResponse.json();

    if (!otpData.success) {
        alert('Invalid OTP! Please try again');
        return;
    }

    // create account
    let response = await fetch('https://pagal-cart.onrender.com/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, email: email, password: password })
    });
    let data = await response.json();
    alert(data.message);

    if (data.message === 'user created') {
        window.location.href = '/login';
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
        localStorage.setItem('user_id', data.id);
        localStorage.setItem('role', data.role);
        localStorage.setItem('user_name', data.name);
        alert("Login successful!");
        window.location.href = '/shop';
    } else {
        alert(data.message);
    }
}

function togglePassword(id) {
    let input = document.getElementById(id);
    input.type = input.type === 'password' ? 'text' : 'password';
}