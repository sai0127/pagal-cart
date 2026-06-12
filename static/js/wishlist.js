async function loadWishlist() {
    let user_id = localStorage.getItem('user_id');
    let response = await fetch(`https://pagal-cart.onrender.com/wishlist/${user_id}`);
    let items = await response.json();
    
    let list = document.getElementById('wishlist-items');
    list.innerHTML = '';
    
    if (items.length === 0) {
        list.innerHTML = '<p style="text-align:center; padding:20px;">Your wishlist is empty!</p>';
        return;
    }
    
    items.forEach(item => {
        let div = document.createElement('div');
        div.className = 'wishlist-card';
        div.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <div class="wishlist-info">
                <h3>${item.name}</h3>
                <p>₹${item.price}</p>
                <div class="wishlist-btns">
                    <button class="cart-btn" onclick="addToCartFromWishlist(${item.product_id})">Add to Cart</button>
                    <button class="remove-btn" onclick="removeFromWishlist(${item.id})">Remove ❤️</button>
                </div>
            </div>
        `;
        list.appendChild(div);
    });
}

async function removeFromWishlist(id) {
    await fetch(`https://pagal-cart.onrender.com/wishlist/${id}`, {
        method: 'DELETE'
    });
    loadWishlist();
}

async function addToCartFromWishlist(product_id) {
    let user_id = localStorage.getItem('user_id');
    await fetch('https://pagal-cart.onrender.com/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user_id, product_id: product_id, quantity: 1 })
    });
    alert('Added to cart!');
}

loadWishlist();