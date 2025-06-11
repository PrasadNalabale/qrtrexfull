// Retrieve cart from localStorage
function getCartItems() {
    const cart = JSON.parse(localStorage.getItem("cart"));
    return Array.isArray(cart) ? cart : [];
}

// Save cart to localStorage
function saveCartItems(cartItems) {
    localStorage.setItem("cart", JSON.stringify(cartItems));
}

// Update the visibility of the "Go to Cart" button and cart count text
function updateGoToCartButton() {
    const goToCartBtn = document.getElementById("goToCartBtn");
    if (!goToCartBtn) {
        console.warn("Go to Cart button not found");
        return;
    }

    const cart = getCartItems();
    const totalItems = cart.reduce((sum, item) => sum + item.qty, 0); // Sum quantities, not just array length

    const cartCount = document.getElementById("cartCount");
    if (totalItems > 0) {
        goToCartBtn.classList.remove("d-none");
        if (cartCount) {
            cartCount.textContent = `${totalItems} item${totalItems > 1 ? 's' : ''} added`;
        }
    } else {
        goToCartBtn.classList.add("d-none");
        if (cartCount) cartCount.textContent = '';
    }
}

// Change quantity of items
function changeQuantity(button, delta) {
    const row = button.closest(".row");
    if (!row) return;

    const itemId = row.dataset.itemId;
    let cart = getCartItems();

    const item = cart.find(i => i.id == itemId);
    if (item) {
        item.qty += delta;
        if (item.qty <= 0) {
            cart = cart.filter(i => i.id != itemId);
            // Hide quantity control, show "Add" button
            const qtyWrapper = row.querySelector(".quantity-wrapper");
            const addBtn = row.querySelector(".add-btn");
            if (qtyWrapper) qtyWrapper.classList.add("d-none");
            if (addBtn) addBtn.classList.remove("d-none");
        } else {
            // Update visible quantity
            const qtySpan = row.querySelector(".qty");
            if (qtySpan) qtySpan.textContent = item.qty;
        }
        saveCartItems(cart);
        updateGoToCartButton();
    }
}

// Add item to the cart
function addToCart(button) {
    const row = button.closest(".row");
    if (!row) return;

    const itemId = row.dataset.itemId;
    const itemName = row.dataset.itemName;
    const itemPrice = parseFloat(row.dataset.itemPrice);

    let cart = getCartItems();

    // Check if item is already in cart
    const existingItem = cart.find(item => item.id == itemId);
    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push({ id: itemId, name: itemName, price: itemPrice, qty: 1 });
    }

    saveCartItems(cart);

    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.value = "";
        console.log("Input cleared");
        if (typeof window.filterMenuItems === 'function') {
            window.filterMenuItems(); // Call the function that resets menu items
        } else {
            console.warn("filterMenuItems function not found");
        }
    } else {
        console.warn("Search input element not found");
    }

    updateGoToCartButton();

    // Hide the Add button and show quantity controls
    button.classList.add("d-none");
    const qtyWrapper = row.querySelector(".quantity-wrapper");
    if (qtyWrapper) qtyWrapper.classList.remove("d-none");
}

// Initialize the menu UI to reflect cart state
function initializeMenuUI() {
    const cart = getCartItems();
    const allRows = document.querySelectorAll(".menuList");

    allRows.forEach(row => {
        const itemId = row.dataset.itemId;
        const itemInCart = cart.find(item => item.id == itemId);

        const addBtn = row.querySelector(".add-btn");
        const qtyWrapper = row.querySelector(".quantity-wrapper");
        const qtySpan = row.querySelector(".qty");

        if (itemInCart) {
            if (addBtn) addBtn.classList.add("d-none");
            if (qtyWrapper) qtyWrapper.classList.remove("d-none");
            if (qtySpan) qtySpan.textContent = itemInCart.qty;
        } else {
            if (addBtn) addBtn.classList.remove("d-none");
            if (qtyWrapper) qtyWrapper.classList.add("d-none");
            if (qtySpan) qtySpan.textContent = 1;
        }
    });

    updateGoToCartButton();

    // Clear cartCleared flag if set
    if (localStorage.getItem('cartCleared') === 'true') {
        localStorage.removeItem('cartCleared');
    }
}

// Run on initial page load
document.addEventListener("DOMContentLoaded", initializeMenuUI);

// Handle browser back/forward restore from cache
window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        initializeMenuUI();
    }
});


























// // Retrieve cart from localStorage
// function getCartItems() {
//     const cart = JSON.parse(localStorage.getItem("cart"));
//     return Array.isArray(cart) ? cart : [];
// }

// // Save cart to localStorage
// function saveCartItems(cartItems) {
//     localStorage.setItem("cart", JSON.stringify(cartItems));
// }

// // Update the visibility of the "Go to Cart" button
// function updateGoToCartButton() {
//     const goToCartBtn = document.getElementById("goToCartBtn");
//     if (!goToCartBtn) return console.log("Go to Cart button not found");

//     const cart = getCartItems();
//     const totalItems = cart.length;
    
//     cartCount = document.getElementById("cartCount");
//     if (totalItems > 0) {
//         goToCartBtn.classList.remove("d-none");
//         cartCount.textContent = `${totalItems} item${totalItems > 1 ? 's' : ''} added`;    
//     } else {
//         goToCartBtn.classList.add("d-none");
//     }
// }

// // Change quantity of items
// function changeQuantity(button, delta) {
//     const row = button.closest(".row");
//     const itemId = row.dataset.itemId;
//     let cart = getCartItems();

//     const item = cart.find(i => i.id == itemId);
//     if (item) {
//         item.qty += delta;
//         if (item.qty <= 0) {
//             cart = cart.filter(i => i.id != itemId);
//             // Hide quantity control, show "Add" button
//             row.querySelector(".quantity-wrapper").classList.add("d-none");
//             row.querySelector(".add-btn").classList.remove("d-none");
//         } else {
//             // Update visible quantity
//             const qtySpan = row.querySelector(".qty");
//             qtySpan.textContent = item.qty;
//         }
//         saveCartItems(cart);
//         updateGoToCartButton();
//     }
// }

// // Add item to the cart

// function addToCart(button) {
    
//     const row = button.closest(".row");
//     const itemId = row.dataset.itemId;
//     const itemName = row.dataset.itemName;
//     const itemPrice = parseFloat(row.dataset.itemPrice);

//     let cart = getCartItems();

//     // Check if item is already in cart
//     const existingItem = cart.find(item => item.id == itemId);
//     if (existingItem) {
//         existingItem.qty += 1;
//     } else {
//         cart.push({ id: itemId, name: itemName, price: itemPrice, qty: 1 });
//     }

//     saveCartItems(cart);
//     searchInput = document.getElementById("searchInput");
//     if (searchInput) {
//         searchInput.value = "";
//         console.log("input cleared");
//         // ✅ Re-run filter to show all items
//         window.filterMenuItems(); // Call the function that resets menu items
//     }else {
//         console.log("some error");
//     }

//     updateGoToCartButton();

//     // Optionally hide the Add button and show quantity controls
//     button.classList.add("d-none");
//     row.querySelector(".quantity-wrapper").classList.remove("d-none");
    
// }





// function initializeMenuUI() {

//     const cart = getCartItems();
//     const allRows = document.querySelectorAll(".menuList");

//     allRows.forEach(row => {
//         const itemId = row.dataset.itemId;
//         const itemInCart = cart.find(item => item.id == itemId);

//         const addBtn = row.querySelector(".add-btn");
//         const qtyWrapper = row.querySelector(".quantity-wrapper");
//         const qtySpan = row.querySelector(".qty");

//         if (itemInCart) {
//             addBtn.classList.add("d-none");
//             qtyWrapper.classList.remove("d-none");
//             qtySpan.textContent = itemInCart.qty;
//         } else {
//             addBtn.classList.remove("d-none");
//             qtyWrapper.classList.add("d-none");
//             qtySpan.textContent = 1;
//         }
//     });

//     updateGoToCartButton();

//     // Clear cartCleared flag if set
//     if (localStorage.getItem('cartCleared') === 'true') {
//         localStorage.removeItem('cartCleared');
//     }
// }

// // Handle initial load
// document.addEventListener("DOMContentLoaded", initializeMenuUI);

// // Handle browser back/forward restore from cache
// window.addEventListener("pageshow", (event) => {
//     if (event.persisted) {
//         initializeMenuUI();
//     }
// });








