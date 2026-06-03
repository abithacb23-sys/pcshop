
console.log("Nova Tech Website Loaded Successfully");

document.querySelectorAll('.add-cart-btn').forEach(button => {
    button.addEventListener('click', () => {
        alert("Product Added to Cart");
    });
});
