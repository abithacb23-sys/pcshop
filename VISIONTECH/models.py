from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class, e.g. bi-cpu")
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    website = models.CharField(max_length=200, blank=True, help_text="Optional brand website URL")
    logo_url = models.CharField(max_length=500, blank=True, help_text="Optional URL or static path to brand logo/image")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=10)
    image_url = models.CharField(max_length=500, help_text="Unsplash or static image URL")
    is_featured = models.BooleanField(default=False)
    
    # Specs & PC Builder Compatibility Fields
    specs = models.JSONField(default=dict, blank=True, help_text="JSON dictionary of specifications")
    wattage = models.IntegerField(default=0, help_text="Wattage requirement or supply (W)")
    socket = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. AM5, LGA1700")
    ram_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. DDR4, DDR5")
    form_factor = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. ATX, Micro-ATX, Mini-ITX")
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.50, help_text="Weight of the component in kg")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Total order shipping weight in kg")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'} for Order #{self.order.id}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    shipping_address = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    avatar = models.CharField(max_length=50, default='bi-person-workspace', help_text="Bootstrap icon class")

    def __str__(self):
        return f"{self.user.username}'s Profile"


class SupportTicket(models.Model):
    TICKET_TYPE_CHOICES = [
        ('Support', 'Support Inquiry'),
        ('RMA', 'RMA Claim'),
        ('Feedback', 'User Feedback'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='Support')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} ({self.ticket_type}) - {self.subject}"
