from typing import Any

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from databases.models import Database
from decouple import config
from projects.models import Project
from queries.models import Query
from users.models import User


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        # Wipe Database
        self.stdout.write('Wiping queries, projects, and databases...')
        Query.objects.all().delete()
        Project.objects.all().delete()
        Database.objects.all().delete()

        self.stdout.write('Deleting non-admin users...')
        User.objects.filter(is_staff=False, is_superuser=False).delete()

        # Create user
        user, created = User.objects.get_or_create(email='pedro@example.com')
        if created:
            user.set_password('123456')
            user.save()

        Database.objects.get_or_create(
            name='Bank Branch',
            defaults={
                'description': 'D.O.C. Bank Branch',
                'host': 'db.doc.ic.ac.uk',
                'port': 5432,
                'user': 'lab',
                'password': 'lab',
                'database_name': 'bank_branch',
                'database_type': Database.DatabaseType.POSTGRESQL,
            },
        )

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

        # Create projects
        sql_valid = Project.objects.create(name='Valid SQL', database=database, user=user)
        sql_syntax = Project.objects.create(name='SQL Syntax Errors', database=database, user=user)
        sql_semantic = Project.objects.create(
            name='SQL Semantic Errors', database=database, user=user
        )
        ra_valid = Project.objects.create(name='Valid RA', database=database, user=user)
        ra_syntax = Project.objects.create(name='RA Syntax Errors', database=database, user=user)
        ra_semantic = Project.objects.create(
            name='RA Semantic Errors', database=database, user=user
        )

        now_time = now()

        # --- SQL Queries ---

        valid_sql_queries = [
            ('Track names and durations', 'SELECT name, milliseconds FROM track'),
            ('Invoices above 20.00', 'SELECT * FROM invoice WHERE total > 20.00'),
            ('Customer contact info', 'SELECT first_name, last_name, email FROM customer'),
            (
                'Tracks and their invoice quantities',
                'SELECT t.name, il.quantity\nFROM track t\nINNER JOIN invoice_line il ON t.track_id = il.track_id',
            ),
            (
                'Average price by media type',
                'SELECT media_type_id, AVG(unit_price) AS avg_price\nFROM track\nGROUP BY media_type_id',
            ),
            (
                'Customers with invoices over 15.00',
                'SELECT first_name, last_name\nFROM customer\nWHERE customer_id IN (\n    SELECT customer_id FROM invoice WHERE total > 15.00\n)',
            ),
            (
                'Customers without invoices',
                'SELECT c.first_name, c.last_name\nFROM customer c\nLEFT JOIN invoice i ON c.customer_id = i.customer_id\nWHERE i.invoice_id IS NULL',
            ),
            (
                'All artist and genre IDs',
                'SELECT artist_id FROM artist\nUNION\nSELECT genre_id FROM genre',
            ),
            (
                'Tracks with invoices',
                'SELECT t.name\nFROM track t\nWHERE EXISTS (\nSELECT 1 FROM invoice_line il WHERE il.track_id = t.track_id\n)',
            ),
            ('Most expensive tracks', 'SELECT * FROM track ORDER BY unit_price DESC LIMIT 5'),
        ]

        sql_syntax_errors = [
            ('Unterminated string literal', "SELECT * FROM track WHERE composer = 'Mozart"),
            (
                'Missing closing parenthesis in subquery',
                'SELECT * FROM track WHERE unit_price > (SELECT AVG(unit_price) FROM track',
            ),
            ('ORDER BY with no column', 'SELECT * FROM track ORDER BY'),
            ('Misspelled SELECT', 'SELEC name FROM track'),
            ('Unbalanced parentheses', 'SELECT * FROM invoice WHERE (total > 20'),
        ]

        sql_semantic_errors = [
            (
                'Column not found',
                'SELECT artist.unknown_field, name\nFROM artist\nWHERE artist_id > 10',
            ),
            ('Type mismatch in comparison', 'SELECT track.name\nFROM track\nWHERE name > 100'),
            (
                'Aggegrate in WHERE clause',
                'SELECT album.title\nFROM album\nWHERE COUNT(album_id) > 5',
            ),
            (
                'Ungrouped column in SELECT',
                'SELECT genre.name, track.composer, COUNT(*)\nFROM track\nJOIN genre ON track.genre_id = genre.genre_id\nGROUP BY genre.name',
            ),
            (
                'Ambiguous column reference',
                'SELECT name\nFROM album\nJOIN artist ON album.artist_id = artist.artist_id',
            ),
            (
                'Missing alias for derived table',
                'SELECT title\nFROM (SELECT album_id, title FROM album WHERE artist_id = 1)',
            ),
            (
                'Non-scalar subquery',
                'SELECT track.name\nFROM track\nWHERE milliseconds = (SELECT milliseconds FROM track)',
            ),
            (
                'Column count mismatch in UNION',
                'SELECT album_id, title FROM album\nUNION\nSELECT artist_id FROM artist',
            ),
            ('Missing JOIN condition', 'SELECT album.title, artist.name\nFROM album\nJOIN artist'),
            ('Out of range ORDER BY', 'SELECT track.name\nFROM track\nORDER BY 3'),
            ('Invalid CAST', 'SELECT CAST(invoice.invoice_date AS INTEGER)\nFROM invoice'),
            (
                'Nested aggregate function',
                'SELECT MAX(AVG(track.milliseconds))\nFROM track\nGROUP BY genre_id',
            ),
            (
                'Duplicate column alias',
                'SELECT album.title AS name, artist.name AS name\nFROM album\nJOIN artist ON album.artist_id = artist.artist_id',
            ),
        ]

        # --- RA Queries ---

        valid_ra_queries = [
            ('Simple projection', '\\pi_{\\text{name}} \\text{genre}'),
            ('Selection', '\\sigma_{\\text{unit_price} > 1.0} \\text{invoice_line}'),
            (
                'Projection after selection',
                '\\pi_{\\text{name}} (\\sigma_{\\text{unit_price} > 1.0} \\text{track})',
            ),
            (
                'Theta-Join',
                '\\text{invoice_line} \\overset{\\text{invoice_line}.\\text{track_id} = \\text{track}.\\text{track_id}}{\\bowtie} \\text{track}',
            ),
            (
                'Join followed by projection',
                '\\pi_{\\text{name}, \\text{unit_price}} (\\text{track} \\Join \\text{invoice_line})',
            ),
            (
                'Grouped aggregation',
                '\\Gamma_{((\\text{media_type_id}), ((\\text{unit_price}, avg, \\text{avg_price})))} \\text{track}',
            ),
            (
                'Top-N',
                '\\operatorname{T}_{(5, \\text{unit_price})} \\text{track}',
            ),
            (
                'Cartesian product followed by selection',
                '\\sigma_{\\text{customer}.\\text{first_name} = \\text{employee}.\\text{first_name}} (\\text{customer} \\times \\text{employee})',
            ),
            (
                'Union',
                '\\text{playlist} \\cup \\pi_{\\text{playlist_id}, \\text{name}} \\text{playlist}',
            ),
        ]

        ra_syntax_errors = [
            ('Missing projection attributes', '\\pi \\text{customer}'),
            (
                'Missing right-hand operand in comparison',
                '\\sigma_{\\text{quantity} >=} \\text{invoice_line}',
            ),
            ('Empty selection condition', '\\sigma_{} Track'),
            ('Division missing divisor operand', '\\text{Artist} \\div'),
            ('Mismatched parentheses', '(\\text{Album} \\Join \\text{Artist}'),
            (
                'Theta-join with empty RHS in overset',
                '\\text{playlist} \\overset{\\text{genre_id} =}{\\bowtie} \\text{track}',
            ),
            (
                'Top-N missing limit',
                '\\operatorname{T}_{(,\\text{unit_price})} \\text{invoice_line}',
            ),
            ('Top-N invalid attribute', '\\operatorname{T}_{(10,5)} \\text{track}'),
        ]

        ra_semantic_errors = [
            ('Non-existent relation', '\\pi_{\\text{artist_id}} \\text{unknown}'),
            (
                'Attribute not found in selection',
                '\\sigma_{\\text{unknown} = 5} \\text{invoice_line}',
            ),
            (
                'Ordering by non-existent attribute in Top-N',
                '\\operatorname{T}_{(10,\\text{price})} \\text{track}',
            ),
            (
                'Ambiguous projection after Cartesian product',
                '\\pi_{\\text{name}} (\\text{playlist} \\times \\text{artist})',
            ),
            (
                'Ambiguous theta-join condition',
                '\\text{invoice} \\overset{\\text{customer_id} = \\text{customer_id}}{\\bowtie} \\text{customer}',
            ),
            ('Type mismatch in comparison', '\\sigma_{\\text{name} > 5} \\text{playlist}'),
            (
                'Type mismatch in logical expression',
                '\\sigma_{\\lnot \\text{fax}} \\text{customer}',
            ),
            ('Union-compatibility', '\\text{invoice_line} \\cup \\text{invoice}'),
            ('Divisor schema not a subset of dividend', '\\text{customer} \\div \\text{employee}'),
            (
                'Invalid aggregation function on VARCHAR',
                '\\Gamma_{((\\text{name}), ((\\text{name}, avg, \\text{avg_name})))} \\text{playlist}',
            ),
        ]

        def seed_queries(
            queries: list[tuple[str, str]], project: Project, language: Query.QueryLanguage
        ) -> None:
            for name, query_text in queries:
                Query.objects.create(
                    name=name,
                    language=language,
                    text=query_text,
                    project=project,
                    created=now_time,
                    modified=now_time,
                )

        seed_queries(valid_sql_queries, sql_valid, language=Query.QueryLanguage.SQL)
        seed_queries(sql_syntax_errors, sql_syntax, language=Query.QueryLanguage.SQL)
        seed_queries(sql_semantic_errors, sql_semantic, language=Query.QueryLanguage.SQL)

        seed_queries(valid_ra_queries, ra_valid, language=Query.QueryLanguage.RA)
        seed_queries(ra_syntax_errors, ra_syntax, language=Query.QueryLanguage.RA)
        seed_queries(ra_semantic_errors, ra_semantic, language=Query.QueryLanguage.RA)

        self.stdout.write(self.style.SUCCESS('Seed completed.'))
