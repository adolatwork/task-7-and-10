# Django N+1 Query Optimization Demo

This project demonstrates the N+1 query problem in Django and how to solve it using `select_related`, `prefetch_related`, and `annotations`.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Populate test data:**
   ```bash
   python manage.py populate_data
   ```
   
   You can customize the amount of data:
   ```bash
   python manage.py populate_data --authors 30 --books 150
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   - Home page: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Features

### Inefficient Views (N+1 Queries)

The following views demonstrate N+1 query problems:

1. **Books List** (`/inefficient/books/`)
   - Problem: Accessing `author`, `publisher`, and `categories` for each book causes multiple queries
   - Query count: 1 + 3N queries (where N is the number of books)

2. **Authors List** (`/inefficient/authors/`)
   - Problem: Accessing `books` and `user` for each author causes multiple queries
   - Query count: 1 + 2N queries

3. **Books with Reviews** (`/inefficient/books-reviews/`)
   - Problem: Accessing nested relationships (books → reviews → reviewer) causes multiple queries
   - Query count: 1 + 3N queries

4. **Authors with Statistics** (`/inefficient/authors-stats/`)
   - Problem: Calculating aggregations in Python instead of the database
   - Query count: 1 + 2N queries

### Optimized Views

The following views demonstrate the optimized versions:

1. **Books List** (`/optimized/books/`)
   - Solution: Uses `select_related('author', 'publisher')` and `prefetch_related('categories')`
   - Query count: 2 queries

2. **Authors List** (`/optimized/authors/`)
   - Solution: Uses `select_related('user')` and `prefetch_related('books')`
   - Query count: 2 queries

3. **Books with Reviews** (`/optimized/books-reviews/`)
   - Solution: Uses `select_related('author')` and `prefetch_related(Prefetch('reviews', queryset=Review.objects.select_related('reviewer')))`
   - Query count: 2 queries

4. **Authors with Statistics** (`/optimized/authors-stats/`)
   - Solution: Uses `annotate()` to calculate stats in the database
   - Query count: 1 query

## Using Django Debug Toolbar

The django-debug-toolbar is configured and will appear on the right side of your browser when viewing pages. It shows:

- **Total number of SQL queries** executed
- **Duplicate queries** (highlighted in red)
- **Time taken** for each query
- **Query details** by clicking on the SQL panel

### Key Metrics to Compare

When comparing inefficient vs optimized views, look for:

1. **Total Query Count**: Should be significantly reduced in optimized views
2. **Duplicate Queries**: Should be eliminated in optimized views
3. **Total Time**: Should be faster in optimized views
4. **Query Types**: Optimized views use JOINs and subqueries instead of multiple separate queries

## Optimization Techniques

### 1. `select_related()`
Use for **ForeignKey** and **OneToOneField** relationships. It performs a SQL JOIN.

```python
# Inefficient
books = Book.objects.all()
for book in books:
    print(book.author.name)  # N+1 queries

# Optimized
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # 1 query
```

### 2. `prefetch_related()`
Use for **ManyToManyField** and reverse **ForeignKey** relationships. It performs a separate optimized query.

```python
# Inefficient
authors = Author.objects.all()
for author in authors:
    print(author.books.count())  # N+1 queries

# Optimized
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    print(author.books.count())  # 2 queries total
```

### 3. `annotations`
Use to calculate aggregations in the database instead of Python.

```python
# Inefficient
authors = Author.objects.all()
for author in authors:
    count = author.books.count()  # N+1 queries
    avg = author.books.aggregate(Avg('price'))  # N+1 queries

# Optimized
authors = Author.objects.annotate(
    book_count=Count('books'),
    avg_price=Avg('books__price')
).all()
for author in authors:
    print(author.book_count)  # 1 query total
    print(author.avg_price)
```

### 4. `Prefetch()` Objects
For more control over prefetch queries, including nested relationships.

```python
# Optimized with nested relationships
books = Book.objects.prefetch_related(
    Prefetch('reviews', queryset=Review.objects.select_related('reviewer'))
).all()
```

## Project Structure

```
task_7/
├── app/
│   ├── models.py              # Author, Book, Category, Publisher, Review models
│   ├── views.py               # Inefficient and optimized views
│   ├── admin.py               # Admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── populate_data.py  # Management command to create test data
│   └── templates/
│       └── app/
│           ├── base.html
│           ├── comparison.html
│           ├── books_list.html
│           ├── authors_list.html
│           ├── books_with_reviews.html
│           ├── authors_stats.html
│           └── authors_stats_optimized.html
├── core/
│   ├── settings.py            # Django settings with debug toolbar config
│   └── urls.py                # URL configuration
└── requirements.txt
```

## Testing the Optimization

1. Start the development server
2. Navigate to the home page to see the comparison view
3. Click on any "Inefficient" link and check the django-debug-toolbar for query count
4. Click on the corresponding "Optimized" link and compare the query count
5. Notice the significant reduction in queries and improved performance

## Example Query Counts

With 50 books in the database:

- **Inefficient Books List**: ~151 queries (1 + 3×50)
- **Optimized Books List**: 2 queries

With 30 authors:

- **Inefficient Authors Stats**: ~61 queries (1 + 2×30)
- **Optimized Authors Stats**: 1 query

## Notes

- The django-debug-toolbar only works when `DEBUG=True` in settings
- Make sure your IP is in `INTERNAL_IPS` (automatically configured for localhost)
- The toolbar appears on the right side of the page in development mode

