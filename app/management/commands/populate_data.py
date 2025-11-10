from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Author, Book, Category, Publisher, Review, Order, OrderItem
from decimal import Decimal
from datetime import date, timedelta, datetime
import random


class Command(BaseCommand):
    help = 'Populates the database with test data for N+1 query demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--authors',
            type=int,
            default=20,
            help='Number of authors to create (default: 20)',
        )
        parser.add_argument(
            '--books',
            type=int,
            default=100,
            help='Number of books to create (default: 100)',
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=200,
            help='Number of orders to create (default: 200)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()
        Publisher.objects.all().delete()
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories_data = [
            ('Fiction', 'Fictional stories and novels'),
            ('Non-Fiction', 'Factual and informative books'),
            ('Science Fiction', 'Speculative fiction with scientific elements'),
            ('Mystery', 'Mystery and detective stories'),
            ('Romance', 'Romantic fiction'),
            ('Thriller', 'Suspenseful and exciting stories'),
            ('Biography', 'Biographical works'),
            ('History', 'Historical accounts and analysis'),
            ('Science', 'Scientific and technical books'),
            ('Philosophy', 'Philosophical works'),
        ]
        categories = []
        for name, desc in categories_data:
            category, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories.append(category)
        
        # Create publishers
        self.stdout.write('Creating publishers...')
        publishers_data = [
            ('Penguin Random House', '1745 Broadway, New York, NY 10019', 'https://www.penguinrandomhouse.com'),
            ('HarperCollins', '195 Broadway, New York, NY 10007', 'https://www.harpercollins.com'),
            ('Simon & Schuster', '1230 Avenue of the Americas, New York, NY 10020', 'https://www.simonandschuster.com'),
            ('Macmillan Publishers', '120 Broadway, New York, NY 10271', 'https://www.macmillan.com'),
            ('Hachette Book Group', '1290 Avenue of the Americas, New York, NY 10104', 'https://www.hachettebookgroup.com'),
        ]
        publishers = []
        for name, address, website in publishers_data:
            publisher, created = Publisher.objects.get_or_create(
                name=name,
                defaults={'address': address, 'website': website}
            )
            publishers.append(publisher)
        
        # Create users
        self.stdout.write('Creating users...')
        users = []
        for i in range(options['authors']):
            username = f'user_{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
        
        # Create authors
        self.stdout.write(f'Creating {options["authors"]} authors...')
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica', 'William', 'Amanda']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        authors = []
        for i in range(options['authors']):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f'{first_name} {last_name}'
            if i < len(users):
                user = users[i]
            else:
                user = random.choice(users)
            
            author = Author.objects.create(
                name=name,
                email=f'{first_name.lower()}.{last_name.lower()}@example.com',
                bio=f'Biography of {name}, a talented author with many published works.',
                user=user
            )
            authors.append(author)
        
        # Create books
        self.stdout.write(f'Creating {options["books"]} books...')
        book_titles = [
            'The Great Adventure', 'Mystery of the Night', 'Love in Paris', 'Science and Discovery',
            'The Hidden Truth', 'Journey to the Stars', 'Secrets of the Past', 'Future Worlds',
            'The Last Stand', 'Echoes of Time', 'Beyond the Horizon', 'The Final Chapter',
            'Shadows and Light', 'The Quest Begins', 'Endless Possibilities', 'The Turning Point',
            'Lost and Found', 'The Perfect Storm', 'Breaking Barriers', 'The New Dawn',
        ]
        
        books = []
        for i in range(options['books']):
            author = random.choice(authors)
            publisher = random.choice(publishers) if random.random() > 0.1 else None
            title = f'{random.choice(book_titles)} {i+1}'
            
            # Generate ISBN
            isbn = ''.join([str(random.randint(0, 9)) for _ in range(13)])
            
            book = Book.objects.create(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                price=Decimal(str(round(random.uniform(9.99, 49.99), 2))),
                pages=random.randint(100, 800),
                published_date=date.today() - timedelta(days=random.randint(0, 3650))
            )
            
            # Add random categories
            num_categories = random.randint(1, 3)
            book.categories.set(random.sample(categories, num_categories))
            books.append(book)
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        review_comments = [
            'Great book! Highly recommended.',
            'A wonderful read from start to finish.',
            'Interesting plot and well-developed characters.',
            'Could not put it down!',
            'A bit slow in the beginning but picks up.',
            'Not my favorite, but still enjoyable.',
            'Excellent writing style and engaging story.',
            'The ending was a bit disappointing.',
            'One of the best books I have read this year.',
            'Well worth the time to read.',
        ]
        
        for book in books:
            # Create 0-5 reviews per book
            num_reviews = random.randint(0, 5)
            for _ in range(num_reviews):
                reviewer = random.choice(users)
                Review.objects.create(
                    book=book,
                    reviewer=reviewer,
                    rating=random.randint(1, 5),
                    comment=random.choice(review_comments)
                )
        
        # Create orders
        self.stdout.write(f'Creating {options["orders"]} orders...')
        orders = []
        # Create orders spread across the last 6 months
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(options['orders']):
            customer = random.choice(users)
            # Random date within last 6 months
            days_ago = random.randint(0, 180)
            order_date = datetime.now() - timedelta(days=days_ago)
            
            order = Order.objects.create(
                customer=customer,
                order_date=order_date,
                status='completed',
                shipping_address=f'{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}'
            )
            orders.append(order)
            
            # Create 1-5 items per order
            num_items = random.randint(1, 5)
            order_books = random.sample(books, min(num_items, len(books)))
            order_total = Decimal('0')
            
            for book in order_books:
                quantity = random.randint(1, 3)
                # Price might be slightly different from book price (discounts, etc.)
                item_price = book.price * Decimal(str(random.uniform(0.8, 1.0)))
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=quantity,
                    price=item_price
                )
                order_total += item_price * quantity
            
            order.total_amount = order_total
            order.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully populated database with:\n'
            f'  - {len(categories)} categories\n'
            f'  - {len(publishers)} publishers\n'
            f'  - {len(users)} users\n'
            f'  - {len(authors)} authors\n'
            f'  - {len(books)} books\n'
            f'  - {Review.objects.count()} reviews\n'
            f'  - {len(orders)} orders\n'
            f'  - {OrderItem.objects.count()} order items\n'
        ))

