async function loadcart() {
    let user_id = localStorage.getItem('user_id');
    let response = await fetch(`https://pagal-cart.onrender.com/cart/${user_id}`);
    let items = await response.json();
    let list = document.getElementById('cart-items');
    list.innerHTML = '';
    
    items.forEach(item => {
        let div = document.createElement('div');
        div.className = 'cart-card';
        div.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <div>
                <h3>${item.name}</h3>
                <p>₹${item.price}</p>
                <div class="qty-controls">
                    <button onclick="decreaseQty(${item.id}, ${item.quantity})">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="increaseQty(${item.id})">+</button>
                </div>
                <p>Total: ₹${item.price * item.quantity}</p>
                <button class="remove-btn" onclick="removeItem(${item.id})">Remove</button>
            </div>
        `;
        list.appendChild(div);
    });
}
loadcart(); 
async function removeItem(id) {
    await fetch(`https://pagal-cart.onrender.com/cart/delete/${id}`, {
        method: 'DELETE'
    });
    loadcart();
}
async function checkout() {
    let user_id = localStorage.getItem('user_id');
    let response = await fetch('https://pagal-cart.onrender.com/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user_id, total: 0 })
    });
    let data = await response.json();
    alert("Order placed!");
    window.location.href = '/shop';
   
}

async function increaseQty(id) {
    await fetch(`https://pagal-cart.onrender.com/cart/update/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'increase' })
    });
    loadcart();
} 

async function decreaseQty(id, quantity) {
    if (quantity === 1) {
        removeItem(id);
    } else {
        await fetch(`https://pagal-cart.onrender.com/cart/update/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'decrease' })
        });
        loadcart();
    }
}

