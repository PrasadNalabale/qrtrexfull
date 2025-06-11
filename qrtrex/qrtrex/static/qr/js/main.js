
document.addEventListener("DOMContentLoaded", function() {  

    // Notification
    function showNotification(message) {
        const notification = document.getElementById('notification');
        const notificationMessage = document.getElementById('notification-message');

        // message
        notificationMessage.textContent = message;
        notification.classList.add('show');

        // Hide notification after 5 seconds
        setTimeout(closeNotification, 5000);
    }

    // Close the notification
    function closeNotification() {
        const notification = document.getElementById('notification');
        notification.classList.remove('show');
    }

});


