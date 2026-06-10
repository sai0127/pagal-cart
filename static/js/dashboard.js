async function loadOrders() {
    let name = localStorage.getItem('user_name');
    document.getElementById('user-name').innerText = name;

    let user_id = localStorage.getItem('user_id');
    let response = await fetch(`https://pagal-cart.onrender.com/orders/${user_id}`);
    let orders = await response.json();
    
    let list = document.getElementById('orders-list');
    list.innerHTML = '';
    
    if (orders.length === 0) {
        list.innerHTML = '<p>No orders yet!</p>';
        return;
    }
    
    for (let order of orders) {
        // get order items for each order
        let itemsResponse = await fetch(`https://pagal-cart.onrender.com/order-items/${order.id}`);
        let items = await itemsResponse.json();
        
        let itemsHTML = items.map(item => `
            <div class="order-item">
                <img src="${item.image}" alt="${item.name}">
                <div>
                    <p>${item.name}</p>
                    <p>Qty: ${item.quantity}</p>
                    <p>₹${item.price}</p>
                </div>
            </div>
        `).join('');
        
        let div = document.createElement('div');
        div.className = 'order-card';
        div.innerHTML = `
            <h3>Order #${order.id}</h3>
            <p>Total: ₹${order.total}</p>
            <div class="order-items">${itemsHTML}</div>
        `;
        list.appendChild(div);
    }
}

loadOrders();