
let allProducts = [];


async function loadProducts() {
    let response = await fetch('https://pagal-cart.onrender.com/products');
    allProducts = await response.json();
    
    let list = document.getElementById('products-grid');
    list.innerHTML = '';
    
    allProducts.forEach(product => {
        let div = document.createElement('div');
        div.className = 'product-card'; 
        div.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>₹${product.price}</p>
            <button onclick="addToCart(${product.id})">Add to Cart</button>
            <button onclick="buyNow(${product.id})">Buy Now</button>
        `;
        list.appendChild(div);
    });
}
loadProducts();

async function addToCart(id) {
    let user_id = localStorage.getItem('user_id');
    
    try {
        let response = await fetch('https://pagal-cart.onrender.com/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: user_id,
                product_id: id,
                quantity: 1
            })
        });

        if (response.ok) {
            alert("Added to cart!");
        } else {
            alert("Failed to add item to cart.");
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
        alert("An error occurred. Please try again.");
    }
}
async function buyNow(id) {
    let user_id = localStorage.getItem('user_id');
    await fetch('https://pagal-cart.onrender.com/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user_id, product_id: id, quantity: 1 })
    });
    window.location.href = '/cart';
}
async function searchProducts() {
    let query = document.getElementById('search-input').value.toLowerCase();
    
    let filtered = allProducts.filter(product => 
        product.name.toLowerCase().includes(query)
    );
    
    let list = document.getElementById('products-grid');
    list.innerHTML = '';
    
    filtered.forEach(product => {
        let div = document.createElement('div');
        div.className = 'product-card';
        div.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>₹${product.price}</p>
            <button onclick="addToCart(${product.id})">Add to Cart</button>
            <button onclick="buyNow(${product.id})">Buy Now</button>
        `;
        list.appendChild(div);
    });
}