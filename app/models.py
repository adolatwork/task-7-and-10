from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    """Author model with user relationship"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(models.Model):
    """Category model for books"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Publisher(models.Model):
    """Publisher model"""
    name = models.CharField(max_length=100)
    address = models.TextField()
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book model with multiple relationships"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books')
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pages = models.IntegerField()
    published_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']


class Review(models.Model):
    """Review model for books"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.book.title} - {self.rating}"

    class Meta:
        ordering = ['-created_at']



########################################################
########    Order and OrderItem models     #############
########################################################



class Order(models.Model):
    """Order model for customer purchases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - {self.order_date.strftime('%Y-%m-%d')}"
    
    def calculate_total(self):
        """Calculate total from order items"""
        from django.db.models import Sum, F
        return self.items.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
    
    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['customer', 'order_date']),
            models.Index(fields=['order_date']),
        ]


class OrderItem(models.Model):
    """Order item model for individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.order} - {self.book.title} x{self.quantity}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    class Meta:
        ordering = ['order', 'id']
