from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from databases.models import Database
from decouple import config
from queries.models import Project, Query


User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with queries for testing'

    def handle(self, *args, **options):
        # Create user
        user, created = User.objects.get_or_create(email='pedro@example.com')
        if created:
            user.set_password('123456')
            user.save()

        # Create database
        database, _ = Database.objects.get_or_create(
            name='Chinook',
            defaults={
                'description': 'Test DB for validation',
                'host': config('SEED_DB_HOST'),
                'port': config('SEED_DB_PORT', cast=int),
                'user': config('SEED_DB_USER'),
                'password': config('SEED_DB_PASSWORD'),
                'database_name': config('SEED_DB_NAME'),
                'database_type': Database.DatabaseType.POSTGRESQL,
            },
        )

        # Create project
        project = Project.objects.create(
            name='Validation Project',
            database=database,
            user=user,
        )

        # Seed queries

        valid_queries = [
            'SELECT * FROM customer',
            "SELECT customer_id, first_name FROM customer WHERE country = 'Germany'",
            'SELECT t.track_id, t.name, a.title FROM track t JOIN album a ON t.album_id = a.album_id',
            'SELECT customer_id, COUNT(*) FROM invoice GROUP BY customer_id HAVING COUNT(*) > 0',
            'SELECT * FROM track ORDER BY unit_price DESC LIMIT 10',
            '  SELECT  *  FROM  customer  ',
        ]

        empty_queries = ['', '   ', '\n\t']

        syntax_errors = [
            'SELECT FROM customer',
            'SELECT * FORM customer',
            'SELECT customer_id, FROM customer',
            'SELECT * FROMM customer',
        ]

        non_select_queries = [
            "INSERT INTO customer (first_name) VALUES ('Test')",
            "UPDATE customer SET first_name = 'New' WHERE customer_id = 1",
            'DELETE FROM customer WHERE customer_id = 1',
            'CREATE TABLE test_table (id INT, name TEXT)',
            'DROP TABLE customer',
            'ALTER TABLE customer ADD COLUMN email TEXT',
        ]

        semantic_errors = [
            'SELECT * FROM nonexistent_table',
            'SELECT unknown_column FROM customer',
        ]

        complex_query = """
            SELECT 
                c.customer_id, 
                c.first_name, 
                COUNT(i.invoice_id) as invoice_count, 
                SUM(il.quantity * il.unit_price) as total_spent
            FROM 
                customer c
            LEFT JOIN 
                invoice i ON c.customer_id = i.customer_id
            LEFT JOIN 
                invoice_line il ON i.invoice_id = il.invoice_id
            WHERE 
                c.country IN ('Germany', 'USA', 'UK')
            GROUP BY 
                c.customer_id, c.first_name
            HAVING 
                COUNT(i.invoice_id) > 0
            ORDER BY 
                total_spent DESC
            LIMIT 10
        """

        sql_injection_attempt = 'SELECT * FROM customer; DROP TABLE customer;'

        all_queries = (
            [(q, 'valid') for q in valid_queries]
            + [(q, 'empty') for q in empty_queries]
            + [(q, 'syntax error') for q in syntax_errors]
            + [(q, 'non-select') for q in non_select_queries]
            + [(q, 'semantic error') for q in semantic_errors]
            + [(complex_query, 'complex')]
            + [(sql_injection_attempt, 'injection')]
        )

        for i, (text, category) in enumerate(all_queries, 1):
            Query.objects.create(
                name=f'{category.title()} Query {i}',
                text=text.strip(),
                project=project,
                created=now(),
                modified=now(),
            )

        self.stdout.write(self.style.SUCCESS('Seed completed.'))
