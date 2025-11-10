from django.shortcuts import render
from django.db.models import Count, Avg, Prefetch, Sum, F, Q, Case, When, IntegerField, DecimalField
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from collections import defaultdict
from decimal import Decimal
from .models import Book, Author, Review, Order, OrderItem


def books_list_inefficient(request):
    """
    INEFFICIENT: This view causes N+1 queries
    - 1 query to get all books
    - N queries to get author for each book (N+1 problem)
    - N queries to get publisher for each book
    - N queries to get categories for each book
    """
    books = Book.objects.all()[:50]
    
    context = {
        'books': books,
        'view_name': 'Inefficient Books List',
        'description': 'This view causes N+1 queries. Check django-debug-toolbar to see the query count.'
    }
    return render(request, 'app/books_list.html', context)


def authors_list_inefficient(request):
    """
    INEFFICIENT: This view causes N+1 queries
    - 1 query to get all authors
    - N queries to get books for each author
    - N queries to get user for each author
    """
    authors = Author.objects.all()[:50]
    
    context = {
        'authors': authors,
        'view_name': 'Inefficient Authors List',
        'description': 'This view causes N+1 queries. Check django-debug-toolbar to see the query count.'
    }
    return render(request, 'app/authors_list.html', context)


def books_with_reviews_inefficient(request):
    """
    INEFFICIENT: This view causes N+1 queries
    - 1 query to get all books
    - N queries to get reviews for each book
    - N queries to get reviewer (User) for each review
    - N queries to get author for each book
    """
    books = Book.objects.all()[:30]
    
    context = {
        'books': books,
        'view_name': 'Inefficient Books with Reviews',
        'description': 'This view causes N+1 queries. Check django-debug-toolbar to see the query count.'
    }
    return render(request, 'app/books_with_reviews.html', context)


def authors_stats_inefficient(request):
    """
    INEFFICIENT: This view causes N+1 queries
    - 1 query to get all authors
    - N queries to count books for each author
    - N queries to get average rating for each author's books
    """
    authors = Author.objects.all()[:30]

    authors_with_stats = []
    for author in authors:
        book_count = author.books.count()
        avg_rating = author.books.aggregate(Avg('reviews__rating'))['reviews__rating__avg'] or 0
        authors_with_stats.append({
            'author': author,
            'book_count': book_count,
            'avg_rating': avg_rating
        })
    
    context = {
        'authors_with_stats': authors_with_stats,
        'view_name': 'Inefficient Authors with Stats',
        'description': 'This view causes N+1 queries. Check django-debug-toolbar to see the query count.'
    }
    return render(request, 'app/authors_stats.html', context)



def books_list_optimized(request):
    """
    OPTIMIZED: Using select_related and prefetch_related
    - 1 query to get all books with authors and publishers (select_related)
    - 1 query to get all categories for all books (prefetch_related)
    Total: 2 queries instead of 1 + 3N queries
    """
    books = Book.objects.select_related('author', 'publisher').prefetch_related('categories').all()[:50]
    
    context = {
        'books': books,
        'view_name': 'Optimized Books List',
        'description': 'This view uses select_related and prefetch_related. Check django-debug-toolbar to see the reduced query count.'
    }
    return render(request, 'app/books_list.html', context)


def authors_list_optimized(request):
    """
    OPTIMIZED: Using select_related and prefetch_related
    - 1 query to get all authors with users (select_related)
    - 1 query to get all books for all authors (prefetch_related)
    Total: 2 queries instead of 1 + 2N queries
    """
    authors = Author.objects.select_related('user').prefetch_related('books').annotate(
        book_count=Count('books')
    ).all()[:50]
    
    context = {
        'authors': authors,
        'view_name': 'Optimized Authors List',
        'description': 'This view uses select_related, prefetch_related, and annotations. Check django-debug-toolbar to see the reduced query count.'
    }
    return render(request, 'app/authors_list.html', context)


def books_with_reviews_optimized(request):
    """
    OPTIMIZED: Using select_related and prefetch_related with Prefetch
    - 1 query to get all books with authors (select_related)
    - 1 query to get all reviews with reviewers for all books (prefetch_related with Prefetch)
    Total: 2 queries instead of 1 + 3N queries
    """
    books = Book.objects.select_related('author').prefetch_related(
        Prefetch('reviews', queryset=Review.objects.select_related('reviewer'))
    ).all()[:30]
    
    context = {
        'books': books,
        'view_name': 'Optimized Books with Reviews',
        'description': 'This view uses select_related and prefetch_related with Prefetch. Check django-debug-toolbar to see the reduced query count.'
    }
    return render(request, 'app/books_with_reviews.html', context)


def authors_stats_optimized(request):
    """
    OPTIMIZED: Using annotations to calculate stats in the database
    - 1 query to get all authors with book counts and average ratings (annotations)
    Total: 1 query instead of 1 + 2N queries
    """
    authors = Author.objects.annotate(
        book_count=Count('books'),
        avg_rating=Avg('books__reviews__rating')
    ).all()[:30]
    
    context = {
        'authors': authors,
        'view_name': 'Optimized Authors with Stats',
        'description': 'This view uses annotations to calculate stats in the database. Check django-debug-toolbar to see the reduced query count.'
    }
    return render(request, 'app/authors_stats_optimized.html', context)


def comparison_view(request):
    """View to show side-by-side comparison"""
    return render(request, 'app/comparison.html', {
        'view_name': 'Query Optimization Comparison'
    })



########################################################
########    Order and OrderItem models     #############
########################################################



def monthly_revenue_inefficient(request):
    """
    INEFFICIENT: Monthly revenue breakdown per customer calculated in Python
    - Multiple queries to get orders per customer per month
    - Python loops to calculate totals, averages, and ratios
    - Very inefficient for large datasets
    """
    orders = Order.objects.filter(status='completed').select_related('customer').all()
    
    customer_monthly_data = defaultdict(lambda: defaultdict(lambda: {
        'revenue': Decimal('0'),
        'orders': [],
        'order_count': 0
    }))
    
    for order in orders:
        month_key = order.order_date.strftime('%Y-%m')
        customer_id = order.customer.id
        
        order_total = sum(item.quantity * item.price for item in order.items.all())
        
        customer_monthly_data[customer_id][month_key]['revenue'] += order_total
        customer_monthly_data[customer_id][month_key]['orders'].append(order_total)
        customer_monthly_data[customer_id][month_key]['order_count'] += 1
    
    report_data = []
    for customer_id, monthly_data in customer_monthly_data.items():
        customer = User.objects.get(id=customer_id)
        for month, data in monthly_data.items():
            total_orders = data['order_count']
            total_revenue = data['revenue']
            avg_check = total_revenue / total_orders if total_orders > 0 else Decimal('0')
            is_returning = total_orders > 1
            
            report_data.append({
                'customer': customer,
                'month': month,
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'avg_check': avg_check,
                'is_returning': is_returning,
            })
    
    monthly_ratios = defaultdict(lambda: {'returning': 0, 'total': 0})
    for item in report_data:
        monthly_ratios[item['month']]['total'] += 1
        if item['is_returning']:
            monthly_ratios[item['month']]['returning'] += 1
    
    for item in report_data:
        month = item['month']
        ratio = (monthly_ratios[month]['returning'] / monthly_ratios[month]['total'] * 100) if monthly_ratios[month]['total'] > 0 else 0
        item['returning_ratio'] = ratio
    
    report_data.sort(key=lambda x: (x['month'], x['customer'].username))
    
    context = {
        'report_data': report_data,
        'view_name': 'Inefficient Monthly Revenue Report',
        'description': 'This view calculates everything in Python with multiple queries. Check django-debug-toolbar to see the high query count.'
    }
    return render(request, 'app/monthly_revenue_report.html', context)


def monthly_revenue_optimized(request):
    """
    OPTIMIZED: Monthly revenue breakdown per customer using ORM annotations and aggregates
    - Uses TruncMonth to group by month
    - Uses annotate with Sum, Count, Avg for calculations
    - Uses Case/When for conditional expressions (returning customer flag)
    - Uses aggregate for returning customer ratio
    - All calculations done in the database
    """
    from django.db.models import Subquery, OuterRef
    
    order_totals_qs = OrderItem.objects.filter(
        order=OuterRef('pk')
    ).values('order').annotate(
        order_total=Sum(F('quantity') * F('price'))
    ).values('order_total')
    
    
    orders_annotated = Order.objects.filter(
        status='completed'
    ).annotate(
        month=TruncMonth('order_date'),
        order_total=Subquery(order_totals_qs[:1], output_field=DecimalField())
    )
    
    monthly_revenue = orders_annotated.values('customer', 'month').annotate(
        total_revenue=Sum('order_total'),
        total_orders=Count('id', distinct=True),
        avg_check=Avg('order_total')
    ).order_by('month', 'customer')
    
    monthly_revenue = monthly_revenue.annotate(
        is_returning=Case(
            When(total_orders__gt=1, then=1),
            default=0,
            output_field=IntegerField()
        )
    )
    
    customer_ids = [item['customer'] for item in monthly_revenue]
    customers = {c.id: c for c in User.objects.filter(id__in=customer_ids)}
    
    unique_months = set(item['month'] for item in monthly_revenue)
    monthly_ratios = {}
    
    for month_date in unique_months:
        month_orders = Order.objects.filter(
            status='completed',
            order_date__year=month_date.year,
            order_date__month=month_date.month
        ).values('customer').annotate(
            order_count=Count('id', distinct=True)
        )
        
        total_customers = month_orders.count()
        returning_customers = month_orders.filter(order_count__gt=1).count()
        ratio = (returning_customers / total_customers * 100) if total_customers > 0 else 0
        monthly_ratios[month_date.strftime('%Y-%m')] = ratio
    
    report_data = []
    for item in monthly_revenue:
        customer = customers.get(item['customer'])
        if customer:
            month = item['month'].strftime('%Y-%m')
            report_data.append({
                'customer': customer,
                'month': month,
                'total_revenue': item['total_revenue'] or Decimal('0'),
                'total_orders': item['total_orders'],
                'avg_check': item['avg_check'] or Decimal('0'),
                'is_returning': bool(item['is_returning']),
                'returning_ratio': monthly_ratios.get(month, 0),
            })
    
    context = {
        'report_data': report_data,
        'view_name': 'Optimized Monthly Revenue Report',
        'description': 'This view uses annotate, aggregate, and Case/When expressions. All calculations are done in the database. Check django-debug-toolbar to see the reduced query count.'
    }
    return render(request, 'app/monthly_revenue_report.html', context)
