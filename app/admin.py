from django.contrib import admin
from .models import Author, Book, Category, Publisher, Review, Order, OrderItem


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email')
    raw_id_fields = ('user',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'price', 'published_date')
    list_filter = ('published_date', 'categories')
    search_fields = ('title', 'isbn', 'author__name')
    filter_horizontal = ('categories',)
    raw_id_fields = ('author', 'publisher')
    date_hierarchy = 'published_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'reviewer__username')
    raw_id_fields = ('book', 'reviewer')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('book',)
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__username', 'id')
    raw_id_fields = ('customer',)
    readonly_fields = ('total_amount',)
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'price', 'subtotal')
    list_filter = ('order__order_date',)
    search_fields = ('order__id', 'book__title')
    raw_id_fields = ('order', 'book')
    readonly_fields = ('subtotal',)
