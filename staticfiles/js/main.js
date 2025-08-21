// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Quantity increment/decrement buttons for product detail page
    const quantityInput = document.querySelector('.quantity-input');
    if (quantityInput) {
        const incrementBtn = document.querySelector('.increment-btn');
        const decrementBtn = document.querySelector('.decrement-btn');
        
        incrementBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue < 10) { // Set max limit to 10
                quantityInput.value = currentValue + 1;
            }
        });
        
        decrementBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) { // Minimum value is 1
                quantityInput.value = currentValue - 1;
            }
        });
    }

    // Product image gallery for product detail page
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    const mainProductImage = document.querySelector('.main-product-image');
    
    if (productThumbnails.length > 0 && mainProductImage) {
        productThumbnails.forEach(function(thumbnail) {
            thumbnail.addEventListener('click', function() {
                // Update main image src with thumbnail src
                mainProductImage.src = this.src;
                
                // Remove active class from all thumbnails
                productThumbnails.forEach(function(thumb) {
                    thumb.classList.remove('active');
                });
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
            });
        });
    }

    // Sticky navigation on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('navbar-sticky');
            } else {
                navbar.classList.remove('navbar-sticky');
            }
        });
    }
}); 