async function loadOrders() {
    let name = localStorage.getItem('user_name');
    document.getElementById('user-name').innerText = name;

    let user_id = localStorage.getItem('user_id');
    let response = await fetch(`https://pagal-cart.onrender.com/orders/${user_id}`);
    let orders = await response.json();
    
    let list = document.getElementById('orders-list');
    list.innerHTML = '';
    
    orders.forEach(order => {
        let div = document.createElement('div');
        div.innerHTML = `
            <p>Order #${order.id}</p>
            <p>Total: ₹${order.total}</p>
        `;
        list.appendChild(div);
    });
}

loadOrders();