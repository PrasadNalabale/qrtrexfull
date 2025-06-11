document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');

    if (!searchInput) return console.warn('searchInput element not found');

    searchInput.addEventListener('input', debounce(filterMenuItems, 300));

    window.addEventListener('pageshow', function () {
        searchInput.value = '';
        setTimeout(() => {
            filterMenuItems();
        }, 100); // small delay allows content to fully load
    });
});

// Debounce helper to limit how often filterMenuItems is called
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}


function filterMenuItems() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    const filter = searchInput.value.trim().toLowerCase();
    const menuItems = document.querySelectorAll('.menuList');

    menuItems.forEach(item => {
        const itemName = item.dataset.itemName.toLowerCase();
        const container = item.closest('.menu-item-wrapper') || item.parentElement.parentElement;

        if (itemName.includes(filter)) {
            container.classList.remove('d-none');
        } else {
            container.classList.add('d-none');
        }
    });

    // Hide accordion sections if all their menu items are hidden
    document.querySelectorAll('.accordion-item').forEach(section => {
        const visibleItems = section.querySelectorAll('.menu-item-wrapper:not(.d-none)');
        if (visibleItems.length === 0) {
            section.classList.add('d-none');
        } else {
            section.classList.remove('d-none');
        }
    });
}







// // function filterMenuItems() {
// //     const searchInput = document.getElementById('searchInput');
// //     if (!searchInput) return;

// //     const filter = searchInput.value.trim().toLowerCase();
// //     const menuItems = document.querySelectorAll('.menuList');

// //     menuItems.forEach(item => {
// //         const itemName = item.dataset.itemName.toLowerCase();
// //         const container = item.closest('.menu-item-wrapper') || item.parentElement.parentElement;

// //         // Remove any previous highlight
// //         container.classList.remove('highlight');

// //         if (filter && itemName.includes(filter)) {
// //             container.classList.add('highlight');
// //         }
// //     });

// //     // Optionally show all accordion sections (no need to hide anything now)
// //     document.querySelectorAll('.accordion-item').forEach(section => {
// //         section.classList.remove('d-none');
// //     });
// // }


// document.addEventListener('DOMContentLoaded', function () {
//     const searchInput = document.getElementById('searchInput');

//     if (!searchInput) return console.warn('searchInput element not found');

//     searchInput.addEventListener('input', debounce(filterMenuItems, 300));

//     window.addEventListener('pageshow', function () {
//         searchInput.value = '';
//         setTimeout(() => filterMenuItems(), 100); // ensure content is rendered
//     });
// });

// // Debounce helper to avoid excessive function calls
// function debounce(fn, delay) {
//     let timer;
//     return function (...args) {
//         clearTimeout(timer);
//         timer = setTimeout(() => fn.apply(this, args), delay);
//     };
// }

// function filterMenuItems() {
//     const searchInput = document.getElementById('searchInput');
//     if (!searchInput) return;

//     const filter = searchInput.value.trim().toLowerCase();
//     const menuItems = document.querySelectorAll('.menuList');

//     menuItems.forEach(item => {
//         const nameElement = item.querySelector('.menusearch strong');
//         const originalName = nameElement.textContent;
//         const container = item.closest('.menu-item-wrapper') || item;

//         // Reset text and remove highlights
//         nameElement.innerHTML = originalName;

//         if (filter && originalName.toLowerCase().includes(filter)) {
//             const regex = new RegExp(`(${filter})`, 'gi');
//             const highlighted = originalName.replace(regex, '<span class="highlight">$1</span>');
//             nameElement.innerHTML = highlighted;
//         }
//     });
// }
