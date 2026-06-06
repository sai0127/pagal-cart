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
