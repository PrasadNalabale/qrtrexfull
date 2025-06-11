
// Get cart items from localStorage

function getCartItems() {
    try {
        const cart = JSON.parse(localStorage.getItem('cart'));
        return Array.isArray(cart) ? cart : [];
    } catch {
        return [];
    }
}

// Save cart items to localStorage
function saveCartItems(cartItems) {
    localStorage.setItem('cart', JSON.stringify(cartItems));
}



// Update the cart UI
function updateCartUI() {
    const cartList = document.getElementById('cart-list');
    if (!cartList) return;
    cartList.innerHTML = '';
    let total = 0;
    
    const cart = getCartItems();
    cart.forEach(item => { 
        total += item.price * item.qty;

        const li = document.createElement('li');
        li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
        li.innerHTML = `
            
                <div class="item-info">
                    <div class="item-name"><p class="text-capitalize" style="margin-bottom : 0rem;">${item.name}</p></div>
                    <div class="item-price">&#8377; ${(item.price * item.qty).toFixed(0) }</div>
                </div>
                <div class="quantity-wrapper">
                    <button type="button" class="qty-btn" onclick="changeQuantity('${item.id}', -1)">-</button>
                    <span class="qty-display">${item.qty}</span>
                    <button type="button" class="qty-btn" onclick="changeQuantity('${item.id}', 1)">+</button>
                </div> 
               
        `;
        
        cartList.appendChild(li);
    });
    

    // Initialize or refresh popover

    const popoverTrigger = document.getElementById('cart-popover');

    // Destroy any existing popover
    if (bootstrap.Popover.getInstance(popoverTrigger)) {
        bootstrap.Popover.getInstance(popoverTrigger).dispose();
    }

    const cartPopover = new bootstrap.Popover(popoverTrigger, {
        html: true,
        trigger: 'focus',
        title: `<div class="popover-header">Cart Summary</div>`,
        content: generatePopoverContent()
    });
    window.cartPopover= cartPopover;
    // newly added for translation

    if (typeof window.collectTextNodes === 'function') {
        window.collectTextNodes();  // Re-scan new nodes
    }

    const currentLang = localStorage.getItem('lang');
    if (currentLang && currentLang !== 'en' && typeof window.applyLanguage === 'function') {
        window.applyLanguage(currentLang);
    }
    //endof newly added 
    

    
}







// Function to call your translation API
async function translateItems(items, lang) {
    // Create a new FormData object
    const formData = new FormData();
    
    // Add each item text to the FormData object
    items.forEach(item => formData.append('texts[]', item));
    formData.append('language', lang);

    // Send the request with the FormData
    const response = await fetch('/api/translate/', {
        method: 'POST',
        body: formData // Send the form data instead of JSON
    });

    if (response.ok) {
        const data = await response.json();
        return data.translated || items;  // Use the translated items or fall back to the original ones
    } else {
        console.error("Translation API failed with status:", response.status);
        return items;  // If the request fails, just return the original items
    }
}

// Function to initialize or refresh the popover for the cart
function initializePopover() {
    const popoverTrigger = document.getElementById('cart-popover');

    // Destroy any existing popover
    if (bootstrap.Popover.getInstance(popoverTrigger)) {
        bootstrap.Popover.getInstance(popoverTrigger).dispose();
    }

    const cartPopover = new bootstrap.Popover(popoverTrigger, {
        html: true,
        trigger: 'focus',
        title: `<div class="popover-header">Cart Summary</div>`,
        content: generatePopoverContent()
    });
    window.cartPopover = cartPopover;
}







// Helper function for content
function generatePopoverContent() {
    const cart = getCartItems();

    if (cart.length === 0) {
        document.getElementById('cart-total').innerHTML = "0.00";
        return '<p>Your cart is empty.</p>';
    }

    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    const cgst = total * 0.05;
    const sgst = total * 0.05;
    const grandTotal = total + cgst + sgst;
    const roundedGrandTotal = Math.round(grandTotal);
    document.getElementById('cart-total').innerHTML = `Total : &#8377; ${roundedGrandTotal.toFixed(2)}`;
    return `
        <div class="popover-body-custom">
            <div class="row mb-1"><div class="col-auto">Subtotal:</div><div class="col text-end fw-bold">&#8377; ${total.toFixed(2)}</div></div>
            <div class="row mb-1"><div class="col-auto">CGST @5%:</div><div class="col text-end">&#8377; ${cgst.toFixed(2)}</div></div>
            <div class="row mb-1"><div class="col-auto">SGST @5%:</div><div class="col text-end">&#8377; ${sgst.toFixed(2)}</div></div>
            <hr class="my-2">
            <div class="row"><div class="col-auto">Total:</div><div class="col text-center text-success fw-bold">&#8377; ${grandTotal.toFixed(2)}</div></div>
        </div>
    `;
}



// Change quantity of items
function changeQuantity(itemId, delta) {
    let cart = getCartItems();
    const item = cart.find(i => i.id === itemId);

    if (item) {
        item.qty += delta;
        if (item.qty <= 0) {
            cart = cart.filter(i => i.id !== itemId);
        }
        saveCartItems(cart);
        updateCartUI();
    }
}

// Clear cart
function clearCart() {
    localStorage.removeItem('cart');
    updateCartUI();
    
    // Dispose of any existing popover instance
    if (window.cartPopover) {
        window.cartPopover.dispose();  // Dispose of the current popover instance
    }

    // Hide popover button (if necessary)
    const popoverTrigger = document.getElementById('cart-popover');
    popoverTrigger.classList.add('d-none');

    
    const toastEl = document.getElementById('cart-toast');
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Checkout (dummy function for now)
function proceedToCheckout() {
    alert('Proceeding to checkout!');
}

function downloadReceipt() {
    const { jsPDF } = window.jspdf; // Access jsPDF from the global window object
    const doc = new jsPDF();
    
    // Cart Data
    const cart = getCartItems();
    const totalAmount = cart.reduce((total, item) => total + (item.price * item.qty), 0).toFixed(2);
    
    // Add Title to PDF
    doc.setFontSize(18);
    doc.text('Receipt', 20, 20);
    
    // Add Cart Items to PDF
    doc.setFontSize(12);
    let yOffset = 30;
    
    cart.forEach(item => {
        doc.text(`${item.name} - $${(item.price * item.qty).toFixed(2)}`, 20, yOffset);
        doc.text(`Quantity: ${item.qty}`, 120, yOffset);
        yOffset += 10;
    });
    
    // Add Total Price
    doc.setFontSize(14);
    doc.text(`Total: $${totalAmount}`, 20, yOffset + 10);

    // Save the PDF
    doc.save('receipt.pdf');
}

// Run on page load
document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();
    
    
});