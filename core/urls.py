from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.comparison_view, name="comparison"),
    
    path("inefficient/books/", views.books_list_inefficient, name="books_inefficient"),
    path("inefficient/authors/", views.authors_list_inefficient, name="authors_inefficient"),
    path("inefficient/books-reviews/", views.books_with_reviews_inefficient, name="books_reviews_inefficient"),
    path("inefficient/authors-stats/", views.authors_stats_inefficient, name="authors_stats_inefficient"),
    
    path("optimized/books/", views.books_list_optimized, name="books_optimized"),
    path("optimized/authors/", views.authors_list_optimized, name="authors_optimized"),
    path("optimized/books-reviews/", views.books_with_reviews_optimized, name="books_reviews_optimized"),
    path("optimized/authors-stats/", views.authors_stats_optimized, name="authors_stats_optimized"),
    
    path("inefficient/revenue-report/", views.monthly_revenue_inefficient, name="revenue_report_inefficient"),
    path("optimized/revenue-report/", views.monthly_revenue_optimized, name="revenue_report_optimized"),
    
    path("__debug__/", include("debug_toolbar.urls")),
]
