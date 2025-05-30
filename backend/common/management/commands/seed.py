import textwrap
from typing import Any

from django.core.management.base import BaseCommand
from django.utils.timezone import now

import queries.services.ra.ast as ra
from databases.models import Database
from exercises.models import Exercise
from projects.models import Project, Query
from queries.models import Language
from queries.services.ra.ast import attribute
from queries.services.ra.ast.factory import query
from queries.services.ra.ast.query import Aggregation, RAQuery
from users.models import User


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        # Wipe Database
        self.stdout.write('Wiping queries, projects, databases, and users...')
        Query.objects.all().delete()
        Project.objects.all().delete()
        Database.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write('Creating users...')
        User.objects.create_superuser(
            email='admin@querycod.com',
            password='querycod',  # noqa: S106
        )

        # Create users
        test_user_1 = User.objects.create(email='test@querycod.com')
        test_user_1.set_password('querycod')
        test_user_1.save()

        test_user_2 = User.objects.create(email='p.mcbrien@imperial.ac.uk')
        test_user_2.set_password('querycod')
        test_user_2.save()

        users = [test_user_1, test_user_2]

        doc_databases = [
            ('Bank Branch', 'bank_branch'),
            ('Bank Customer', 'bank_customer'),
            ('Family History', 'family_history'),
            ('Mondial', 'mondial'),
            ('1990 United States census', 'uscensus1990'),
        ]

        # Create databases
        for name, db_name in doc_databases:
            Database.objects.get_or_create(
                name=name,
                description='D.O.C. educational database',
                host='db.doc.ic.ac.uk',
                port=5432,
                user='lab',
                password='lab',  # noqa: S106
                database_name=db_name,
                database_type=Database.DatabaseType.POSTGRESQL,
            )

        database = Database.objects.create(
            name='Chinook',
            description='Digital media store, including tables for artists, albums, media tracks, invoices, and customers.',
            host='aws-0-eu-west-2.pooler.supabase.com',
            port=6543,
            user='postgres.szwxnnaqhqairmwulojt',
            password='5LvprM3QNB9h5VZd',  # noqa: S106
            database_name='postgres',
            database_type=Database.DatabaseType.POSTGRESQL,
        )

        # Create projects and queries
        now_time = now()

        def seed_queries(
            queries: list[tuple[str, str]], project: Project, language: Language
        ) -> None:
            for name, query_text in queries:
                Query.objects.create(
                    name=name,
                    _language=language,
                    text=query_text,
                    project=project,
                    created=now_time,
                    modified=now_time,
                )

        def seed_ra_queries(queries: list[tuple[str, RAQuery | str]], project: Project) -> None:
            seed_queries(
                [
                    (name, query.latex() if isinstance(query, RAQuery) else query)
                    for name, query in queries
                ],
                project,
                language=Language.RA,
            )

        def seed_sql_queries(queries: list[tuple[str, str]], project: Project) -> None:
            seed_queries(
                [(name, textwrap.dedent(query_text).strip()) for name, query_text in queries],
                project,
                language=Language.SQL,
            )

        for user in users:
            sql_lecture = Project.objects.create(
                name='SQL Lecture',
                database=Database.objects.get(name='Bank Branch'),
                user=user,
            )

            sql_lecture_queries = [
                (
                    'Current accounts with branch names',
                    """
                    SELECT branch.bname, no
                    FROM account
                        JOIN branch
                        ON account.sortcode = branch.sortcode
                    WHERE account.type='current'
                    """,
                ),
                (
                    'Except - Accounts with no movements',
                    """
                    SELECT no
                    FROM account
                    EXCEPT
                    SELECT no
                    FROM movement
                    """,
                ),
                (
                    'Natural Join',
                    """
                    SELECT *
                    FROM branch NATURAL JOIN
                        account
                    """,
                ),
                (
                    'Join Using',
                    """
                    SELECT branch.*, no, type, cname, rate
                    FROM branch JOIN account
                        USING (sortcode)
                    """,
                ),
                (
                    'Table and Column Aliases',
                    """
                    SELECT current_account.cname,
                        current_account.no AS current_no,
                        deposit_account.no AS deposit_no
                    FROM   account AS current_account
                        JOIN account AS deposit_account
                        ON current_account.cname = deposit_account.cname
                        AND current_account.type = 'current'
                        AND deposit_account.type = 'deposit'
                    """,
                ),
                (
                    'Set Operations: IN',
                    """
                    SELECT no
                    FROM   account
                    WHERE  type = 'current'
                    AND    no IN (SELECT no
                                FROM movement
                                WHERE amount > 500)
                    """,
                ),
                (
                    'Set Operations: EXISTS',
                    """
                    SELECT DISTINCT cname
                    FROM   account
                    WHERE NOT EXISTS
                        (SELECT cname
                        FROM   account AS deposit_account
                        WHERE  type = 'deposit'
                        AND    account.cname = deposit_account.cname)
                    """,
                ),
                (
                    'Unqualified Correlated Subquery',
                    """
                    SELECT DISTINCT cname
                    FROM   account
                    WHERE NOT EXISTS
                        (SELECT *
                        FROM   account AS deposit_account
                        WHERE  type = 'deposit'
                        AND    account.cname = cname)
                    """,
                ),
                (
                    'Set Operations: SOME',
                    """
                    SELECT bname
                    FROM branch
                    WHERE 'deposit' = SOME (SELECT type
                                            FROM account
                                            WHERE branch.sortcode = account.sortcode)
                    """,
                ),
                (
                    'Set Operations: ALL',
                    """
                    SELECT bname
                    FROM branch
                    WHERE 'deposit' = ALL (SELECT type
                                        FROM account
                                        WHERE branch.sortcode = account.sortcode)
                    """,
                ),
            ]

            seed_sql_queries(sql_lecture_queries, sql_lecture)

            ra_lecture = Project.objects.create(
                name='Relational Algebra Lecture',
                database=Database.objects.get(name='Bank Branch'),
                user=user,
            )

            ra_lecture_queries: list[tuple[str, RAQuery | str]] = [
                ('Project', query('account').project('no', 'type')),
                ('Select', query('account').select(ra.GT(attribute('rate'), 0))),
                (
                    'Product',
                    query('branch').cartesian(query('account').select(ra.GT(attribute('rate'), 0))),
                ),
                (
                    'SPJ',
                    query('branch')
                    .cartesian('account')
                    .select(
                        ra.And(
                            ra.EQ(attribute('branch.sortcode'), attribute('account.sortcode')),
                            ra.EQ(attribute('account.type'), 'current'),
                        )
                    )
                    .project('bname', 'no'),
                ),
                (
                    'Union',
                    query('account').project('sortcode').union(query('account').project('no')),
                ),
                (
                    'Difference',
                    query('account').project('no').difference(query('movement').project('no')),
                ),
                ('Natural Join', query('branch').natural_join('account')),
                ('Quiz 3.1', query('account').natural_join('movement').project('no')),
                ('Semi Join', query('account').semi_join(query('movement'))),
                (
                    'Intersection',
                    query('account').project('no').intersect(query('movement').project('no')),
                ),
                (
                    'Division',
                    query('account')
                    .project('cname', 'type')
                    .divide(query('account').project('type')),
                ),
            ]

            seed_ra_queries(ra_lecture_queries, ra_lecture)

            sql_valid = Project.objects.create(name='Valid SQL', database=database, user=user)

            valid_sql_queries = [
                ('Track names and durations', 'SELECT name, milliseconds FROM track'),
                ('Invoices above 20.00', 'SELECT * FROM invoice WHERE total > 20.00'),
                ('Customer contact info', 'SELECT first_name, last_name, email FROM customer'),
                (
                    'Tracks and their invoice quantities',
                    """
                    SELECT t.name, il.quantity
                    FROM track t
                        INNER JOIN invoice_line il
                        ON t.track_id = il.track_id
                    """,
                ),
                (
                    'Average price by media type',
                    """
                    SELECT media_type_id, AVG(unit_price) AS avg_price
                    FROM track
                    GROUP BY media_type_id
                    """,
                ),
                (
                    'Customers with invoices over 15.00',
                    """
                    SELECT first_name, last_name
                    FROM customer
                    WHERE customer_id IN (SELECT customer_id
                                        FROM invoice
                                        WHERE total > 15.00)
                    """,
                ),
                (
                    'Customers without invoices',
                    """
                    SELECT c.first_name, c.last_name
                    FROM customer c
                        LEFT JOIN invoice i
                        ON c.customer_id = i.customer_id
                    WHERE i.invoice_id IS NULL
                    """,
                ),
                (
                    'All artist and genre IDs',
                    """
                    SELECT artist_id FROM artist
                    UNION
                    SELECT genre_id FROM genre
                    """,
                ),
                (
                    'Tracks with invoices',
                    """
                    SELECT t.name
                    FROM track t
                    WHERE EXISTS (SELECT 1
                                FROM invoice_line il
                                WHERE il.track_id = t.track_id)
                    """,
                ),
                ('Most expensive tracks', 'SELECT * FROM track ORDER BY unit_price DESC LIMIT 5'),
            ]

            seed_sql_queries(valid_sql_queries, sql_valid)

            # sql_syntax = Project.objects.create(name='SQL Syntax Errors', database=database, user=user)

            # sql_syntax_errors = [
            #     ('Unterminated string literal', "SELECT * FROM track WHERE composer = 'Mozart"),
            #     (
            #         'Missing closing parenthesis in subquery',
            #         'SELECT * FROM track WHERE unit_price > (SELECT AVG(unit_price) FROM track',
            #     ),
            #     ('ORDER BY with no column', 'SELECT * FROM track ORDER BY'),
            #     ('Misspelled SELECT', 'SELEC name FROM track'),
            #     ('Unbalanced parentheses', 'SELECT * FROM invoice WHERE (total > 20'),
            # ]

            # seed_sql_queries(sql_syntax_errors, sql_syntax)

            sql_semantic = Project.objects.create(
                name='SQL Semantic Errors', database=database, user=user
            )

            sql_semantic_errors = [
                (
                    'Column not found',
                    """
                    SELECT artist.unknown_field, name
                    FROM artist
                    WHERE artist_id > 10
                    """,
                ),
                (
                    'Type mismatch in comparison',
                    """
                    SELECT track.name
                    FROM track
                    WHERE name > 100
                    """,
                ),
                (
                    'Aggegrate in WHERE clause',
                    """
                    SELECT album.title
                    FROM album
                    WHERE COUNT(album_id) > 5
                    """,
                ),
                (
                    'Ungrouped column in SELECT',
                    """
                    SELECT genre.name, track.composer, COUNT(*)
                    FROM track
                        JOIN genre
                        ON track.genre_id = genre.genre_id
                    GROUP BY genre.name
                    """,
                ),
                (
                    'Ambiguous column reference',
                    """
                    SELECT name, composer
                    FROM playlist
                    NATURAL JOIN playlist_track
                    JOIN track USING (track_id)
                    """,
                ),
                (
                    'Missing alias for derived table',
                    """
                    SELECT title
                    FROM (SELECT album_id, title
                        FROM album
                        WHERE artist_id = 1)
                    """,
                ),
                (
                    'Non-scalar subquery',
                    """
                    SELECT track.name
                    FROM track
                    WHERE milliseconds = (SELECT milliseconds FROM track)
                    """,
                ),
                (
                    'Column count mismatch in UNION',
                    """
                    SELECT album_id, title FROM album
                    UNION
                    SELECT artist_id FROM artist
                    """,
                ),
                (
                    'Missing JOIN condition',
                    """
                    SELECT album.title, artist.name
                    FROM album
                    JOIN artist
                    """,
                ),
                (
                    'Out of range ORDER BY',
                    """
                    SELECT name, composer
                    FROM track
                    ORDER BY 3
                    """,
                ),
                (
                    'Invalid CAST',
                    """
                    SELECT CAST(invoice.invoice_date AS INTEGER)
                    FROM invoice
                    """,
                ),
                (
                    'Nested aggregate function',
                    """
                    SELECT MAX(AVG(track.milliseconds))
                    FROM track
                    GROUP BY genre_id
                    """,
                ),
                (
                    'Duplicate column alias',
                    """
                    SELECT album.title AS name, artist.name AS name
                        FROM album
                        JOIN artist
                        ON album.artist_id = artist.artist_id
                    """,
                ),
            ]

            seed_sql_queries(sql_semantic_errors, sql_semantic)

            ra_valid = Project.objects.create(name='Valid RA', database=database, user=user)

            valid_ra_queries: list[tuple[str, RAQuery | str]] = [
                (
                    'Theta-Join',
                    query('invoice_line').theta_join(
                        'track',
                        ra.EQ(attribute('invoice_line.track_id'), attribute('track.track_id')),
                    ),
                ),
                (
                    'Grouped aggregation',
                    query('track').grouped_aggregation(
                        ['media_type_id'],
                        [
                            Aggregation(
                                attribute('unit_price'), ra.AggregationFunction.AVG, 'avg_price'
                            )
                        ],
                    ),
                ),
                ('Top-N', query('track').top_n(5, 'unit_price')),
            ]

            seed_ra_queries(valid_ra_queries, ra_valid)

            ra_syntax = Project.objects.create(
                name='RA Syntax Errors', database=database, user=user
            )

            ra_syntax_errors: list[tuple[str, RAQuery | str]] = [
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

            seed_ra_queries(ra_syntax_errors, ra_syntax)

            ra_semantic = Project.objects.create(
                name='RA Semantic Errors', database=database, user=user
            )

            ra_semantic_errors: list[tuple[str, RAQuery | str]] = [
                ('Non-existent relation', query('unknown').project('artist_id')),
                (
                    'Attribute not found in selection',
                    query('invoice_line').select(ra.EQ(attribute('unknown'), 5)),
                ),
                (
                    'Ordering by non-existent attribute in Top-N',
                    query('track').top_n(10, 'price'),
                ),
                (
                    'Ambiguous projection after Cartesian product',
                    query('playlist').cartesian('artist').project('name'),
                ),
                (
                    'Ambiguous theta-join condition',
                    query('invoice').theta_join(
                        'customer', ra.EQ(attribute('customer_id'), attribute('customer_id'))
                    ),
                ),
                (
                    'Type mismatch in comparison',
                    query('playlist').select(ra.GT(attribute('name'), 5)),
                ),
                (
                    'Type mismatch in logical expression',
                    query('customer').select(ra.Not(attribute('fax'))),
                ),
                ('Union-compatibility', query('invoice_line').union('invoice')),
                ('Divisor schema not a subset of dividend', query('customer').divide('employee')),
                (
                    'Invalid aggregation function on VARCHAR',
                    query('playlist').grouped_aggregation(
                        ['name'],
                        [Aggregation(attribute('name'), ra.AggregationFunction.AVG, 'avg_name')],
                    ),
                ),
            ]

            seed_ra_queries(ra_semantic_errors, ra_semantic)

        self.stdout.write('Creating exercises...')

        Exercise.objects.create(
            title='People born in the same place as their mother',
            description='Write a query that returns the scheme ```(name, born_in)``` containing the name and place of birth of all people known to have been born in the same place as their mother.',
            solution=query('person')
            .cartesian(query('person').rename('mother'))
            .select(
                ra.And(
                    ra.EQ(attribute('person.mother'), attribute('mother.name')),
                    ra.EQ(attribute('person.born_in'), attribute('mother.born_in')),
                )
            )
            .project('person.name', 'person.born_in')
            .latex(pretty=True),
            language=Language.RA,
            difficulty=Exercise.Difficulty.MEDIUM,
            database=Database.objects.get(name='Family History'),
        )

        Exercise.objects.create(
            title='Parents',
            description='Write a query that returns the scheme ```(name)``` containing names of all people known to be parents.',
            solution=textwrap.dedent(
                """
                SELECT name
                FROM person AS child
                WHERE EXISTS (SELECT *
                              FROM person
                              WHERE child.name IN (mother,father))
            """
            ).strip(),
            language=Language.SQL,
            difficulty=Exercise.Difficulty.EASY,
            database=Database.objects.get(name='Family History'),
        )

        self.stdout.write(self.style.SUCCESS('Seed completed.'))
