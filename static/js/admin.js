// check if admin
if (localStorage.getItem('role') !== 'admin') {
    alert('Access denied!');
    window.location.href = '/shop';
}
let allProducts = []
async function loadProducts() {
    let response = await fetch('https://pagal-cart.onrender.com/products');
    allProducts = await response.json();

    
    let list = document.getElementById('products-list');
    list.innerHTML = '';
    
    allProducts.forEach(product => {
        let div = document.createElement('div');
        div.className = 'product-item';
        div.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <p>₹${product.price}</p>
            <button onclick="editProduct(${product.id})">Edit</button>
            <button onclick="deleteproduct(${product.id})">Delete</button>`;
        list.appendChild(div);
    });

}

async function addproduct() {
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;
    let price = document.getElementById('price').value;
    let image = document.getElementById('image').value;
    
    if (name === '') {
        alert('please enter a product name');
        return;
    }
    
    await fetch('https://pagal-cart.onrender.com/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, description: description, price: price, image: image })
    });
    alert('product added successfully!');
    closeModal(); // also close modal after adding
    document.getElementById('name').value = '';
    document.getElementById('description').value = '';
    document.getElementById('price').value = '';
    document.getElementById('image').value = '';
    
    loadProducts();
}

async function deleteproduct(id) {
    await fetch(`https://pagal-cart.onrender.com/products/${id}`, {
        method: 'DELETE'
    });
    loadProducts();

}
function openModal() {
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

async function editProduct(id) {
    let product = allProducts.find(p => p.id === id);
    
    document.getElementById('name').value = product.name;
    document.getElementById('description').value = product.description;
    document.getElementById('price').value = product.price;
    document.getElementById('image').value = product.image;
    
    openModal();
    document.getElementById('modal-btn').innerText = 'Save Changes';
    document.getElementById('modal-btn').onclick = () => saveProduct(id);
}
async function saveProduct(id) {
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;
    let price = document.getElementById('price').value;
    let image = document.getElementById('image').value;
    
    if (name === '') {
        alert('please enter a product name');
        return;
    }
    
    await fetch(`https://pagal-cart.onrender.com/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, description: description, price: price, image: image })
    });
    alert('product updated successfully!');
    closeModal(); // also close modal after adding
    document.getElementById('name').value = '';
    document.getElementById('description').value = '';
    document.getElementById('price').value = '';
    document.getElementById('image').value = '';
    document.getElementById('modal-btn').innerText = 'Add Product'
    document.getElementById('modal-btn').onclick = addproduct
    loadProducts();
}
loadProducts()
async function loadStats() {
    let response = await fetch('https://pagal-cart.onrender.com/stats');
    let stats = await response.json();
    
    document.getElementById('total-products').innerText = stats.products;
    document.getElementById('total-users').innerText = stats.users;
    document.getElementById('total-orders').innerText = stats.orders;
}
function showTab(tab) {
    document.getElementById('products-section').style.display = tab === 'products' ? 'block' : 'none';
    document.getElementById('database-section').style.display = tab === 'database' ? 'block' : 'none';
    document.getElementById('tab-products').classList.toggle('active', tab === 'products');
    document.getElementById('tab-database').classList.toggle('active', tab === 'database');
    
    if (tab === 'database') {
        loadUsers();
        loadOrders();
    }
}

async function loadUsers() {
    let response = await fetch('https://pagal-cart.onrender.com/users');
    let users = await response.json();
    
    let list = document.getElementById('users-list');
    list.innerHTML = '';
    
    users.forEach(user => {
        let div = document.createElement('div');
        div.className = 'db-row';
        div.innerHTML = `
            <span>${user.id}</span>
            <span>${user.name}</span>
            <span>${user.email}</span>
            <span class="role-badge">${user.role}</span>
            <button class="delete-btn" onclick="deleteUser(${user.id})">Delete</button>
        `;
        list.appendChild(div);
    });
}

async function loadOrders() {
    let response = await fetch('https://pagal-cart.onrender.com/all-orders');
    let orders = await response.json();
    
    let list = document.getElementById('orders-list');
    list.innerHTML = '';
    
    orders.forEach(order => {
        let div = document.createElement('div');
        div.className = 'db-row';
        div.innerHTML = `
            <span>Order #${order.id}</span>
            <span>User ID: ${order.user_id}</span>
            <span>₹${order.total}</span>
        `;
        list.appendChild(div);
    });
}
async function deleteUser(id) {
    if (confirm('Are you sure you want to delete this user?')) {
        await fetch(`https://pagal-cart.onrender.com/users/${id}`, {
            method: 'DELETE'
        });
        loadUsers();
        loadStats();
    }
}

loadStats();