// get product id from URL
function getProductId() {
    let params = new URLSearchParams(window.location.search);
    return params.get('product_id');
}

async function placeOrder() {
    // get address values
    let fullname = document.getElementById('fullname').value;
    let phone = document.getElementById('phone').value;
    let address = document.getElementById('address').value;
    let city = document.getElementById('city').value;
    let state = document.getElementById('state').value;
    let pincode = document.getElementById('pincode').value;

    // validations
    // validations
    if (!fullname || !phone || !address || !city || !state || !pincode) {
        alert('Please fill all fields');
        return;
    }
    if (phone.length !== 10) {
        alert('Phone number must be 10 digits');
        return;
    }
    if (pincode.length !== 6) {
        alert('Pincode must be 6 digits');
        return;
    }
    if (!/^[a-zA-Z\s]+$/.test(fullname)) {
        alert('Name should only contain letters');
        return;
    }

    let user_id = localStorage.getItem('user_id');
    let product_id = getProductId();

    // get cart items
    let cartResponse = await fetch(`https://pagal-cart.onrender.com/cart/${user_id}`);
    let cartItems = await cartResponse.json();

    // calculate total
    let total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // place order
    let response = await fetch('https://pagal-cart.onrender.com/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: user_id,
            total: total,
            items: cartItems.map(item => ({
                product_id: item.id,
                quantity: item.quantity,
                price: item.price
            })),
            address: {
                fullname: fullname,
                phone: phone,
                address: address,
                city: city,
                state: state,
                pincode: pincode
            }
        })
    });

    let data = await response.json();
    alert('Order placed successfully! 🎉');
    window.location.href = '/dashboard';
}