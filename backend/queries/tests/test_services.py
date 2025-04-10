import pytest
from databases.models import DatabaseConnectionInfo
from queries.services.validation import validate_sql


@pytest.fixture
def db_info(tmp_path):
    return DatabaseConnectionInfo(
        database_type='sqlite',
        host='',
        port=None,
        name=str(tmp_path / 'northwind_test.sqlite3'),
        user=None,
        password=None,
    )


@pytest.fixture
def setup_test_db(db_info):
    from databases.services.execution import execute_sql

    # Create Categories table
    execute_sql(
        """
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL,
            description TEXT,
            picture BLOB
        )
        """,
        db_info,
    )

    # Create Customers table
    execute_sql(
        """
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_title TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            phone TEXT,
            fax TEXT
        )
        """,
        db_info,
    )

    # Create Employees table
    execute_sql(
        """
        CREATE TABLE employees (
            employee_id INTEGER PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            title TEXT,
            title_of_courtesy TEXT,
            birth_date TEXT,
            hire_date TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            home_phone TEXT,
            extension TEXT,
            photo BLOB,
            notes TEXT,
            reports_to INTEGER,
            FOREIGN KEY (reports_to) REFERENCES employees (employee_id)
        )
        """,
        db_info,
    )

    # Create Suppliers table
    execute_sql(
        """
        CREATE TABLE suppliers (
            supplier_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_title TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            phone TEXT,
            fax TEXT,
            homepage TEXT
        )
        """,
        db_info,
    )

    # Create Products table
    execute_sql(
        """
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            supplier_id INTEGER,
            category_id INTEGER,
            quantity_per_unit TEXT,
            unit_price REAL,
            units_in_stock INTEGER,
            units_on_order INTEGER,
            reorder_level INTEGER,
            discontinued INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (category_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id)
        )
        """,
        db_info,
    )

    # Create Orders table
    execute_sql(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id TEXT,
            employee_id INTEGER,
            order_date TEXT,
            required_date TEXT,
            shipped_date TEXT,
            ship_via INTEGER,
            freight REAL,
            ship_name TEXT,
            ship_address TEXT,
            ship_city TEXT,
            ship_region TEXT,
            ship_postal_code TEXT,
            ship_country TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
        """,
        db_info,
    )

    # Create Order_Details table
    execute_sql(
        """
        CREATE TABLE order_details (
            order_id INTEGER,
            product_id INTEGER,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            discount REAL NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
        """,
        db_info,
    )

    # Insert some sample data
    # Categories
    execute_sql(
        """
        INSERT INTO categories (category_id, category_name, description) VALUES 
        (1, 'Beverages', 'Soft drinks, coffees, teas, beers, and ales'),
        (2, 'Condiments', 'Sweet and savory sauces, relishes, spreads, and seasonings'),
        (3, 'Confections', 'Desserts, candies, and sweet breads'),
        (4, 'Dairy Products', 'Cheeses'),
        (5, 'Grains/Cereals', 'Breads, crackers, pasta, and cereal')
        """,
        db_info,
    )

    # Customers
    execute_sql(
        """
        INSERT INTO customers (customer_id, company_name, contact_name, country, city) VALUES 
        ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Germany', 'Berlin'),
        ('ANATR', 'Ana Trujillo Emparedados', 'Ana Trujillo', 'Mexico', 'México D.F.'),
        ('ANTON', 'Antonio Moreno Taquería', 'Antonio Moreno', 'Mexico', 'México D.F.'),
        ('AROUT', 'Around the Horn', 'Thomas Hardy', 'UK', 'London'),
        ('BERGS', 'Berglunds snabbköp', 'Christina Berglund', 'Sweden', 'Luleå')
        """,
        db_info,
    )

    # Employees
    execute_sql(
        """
        INSERT INTO employees (employee_id, last_name, first_name, title, birth_date, hire_date, city, country) VALUES 
        (1, 'Davolio', 'Nancy', 'Sales Representative', '1968-12-08', '1992-05-01', 'Seattle', 'USA'),
        (2, 'Fuller', 'Andrew', 'Vice President, Sales', '1952-02-19', '1992-08-14', 'Tacoma', 'USA'),
        (3, 'Leverling', 'Janet', 'Sales Representative', '1963-08-30', '1992-04-01', 'Kirkland', 'USA'),
        (4, 'Peacock', 'Margaret', 'Sales Representative', '1958-09-19', '1993-05-03', 'Redmond', 'USA'),
        (5, 'Buchanan', 'Steven', 'Sales Manager', '1955-03-04', '1993-10-17', 'London', 'UK')
        """,
        db_info,
    )

    # Suppliers
    execute_sql(
        """
        INSERT INTO suppliers (supplier_id, company_name, contact_name, city, country) VALUES 
        (1, 'Exotic Liquids', 'Charlotte Cooper', 'London', 'UK'),
        (2, 'New Orleans Cajun Delights', 'Shelley Burke', 'New Orleans', 'USA'),
        (3, 'Grandma Kelly''s Homestead', 'Regina Murphy', 'Ann Arbor', 'USA'),
        (4, 'Tokyo Traders', 'Yoshi Nagase', 'Tokyo', 'Japan'),
        (5, 'Cooperativa de Quesos ''Las Cabras''', 'Antonio del Valle Saavedra', 'Oviedo', 'Spain')
        """,
        db_info,
    )

    # Products
    execute_sql(
        """
        INSERT INTO products (product_id, product_name, supplier_id, category_id, quantity_per_unit, unit_price, units_in_stock, discontinued) VALUES 
        (1, 'Chai', 1, 1, '10 boxes x 20 bags', 18.0, 39, 0),
        (2, 'Chang', 1, 1, '24 - 12 oz bottles', 19.0, 17, 0),
        (3, 'Aniseed Syrup', 1, 2, '12 - 550 ml bottles', 10.0, 13, 0),
        (4, 'Chef Anton''s Cajun Seasoning', 2, 2, '48 - 6 oz jars', 22.0, 53, 0),
        (5, 'Grandma''s Boysenberry Spread', 3, 2, '12 - 8 oz jars', 25.0, 120, 0)
        """,
        db_info,
    )

    # Orders
    execute_sql(
        """
        INSERT INTO orders (order_id, customer_id, employee_id, order_date, required_date, shipped_date) VALUES 
        (10248, 'VINET', 5, '1996-07-04', '1996-08-01', '1996-07-16'),
        (10249, 'TOMSP', 6, '1996-07-05', '1996-08-16', '1996-07-10'),
        (10250, 'HANAR', 4, '1996-07-08', '1996-08-05', '1996-07-12'),
        (10251, 'VICTE', 3, '1996-07-08', '1996-08-05', '1996-07-15'),
        (10252, 'SUPRD', 4, '1996-07-09', '1996-08-06', '1996-07-11')
        """,
        db_info,
    )

    # Order Details
    execute_sql(
        """
        INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount) VALUES 
        (10248, 11, 14.0, 12, 0),
        (10248, 42, 9.8, 10, 0),
        (10249, 14, 18.6, 9, 0),
        (10249, 51, 42.4, 40, 0),
        (10250, 41, 7.7, 10, 0)
        """,
        db_info,
    )

    yield


@pytest.mark.parametrize(
    'query',
    [
        'SELECT * FROM customers',
        'SELECT customer_id, company_name FROM customers WHERE country = "Germany"',
        'SELECT p.product_id, p.product_name, c.category_name FROM products p JOIN categories c ON p.category_id = c.category_id',
        'SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id HAVING COUNT(*) > 0',
        'SELECT * FROM products ORDER BY unit_price DESC LIMIT 10',
        '  SELECT  *  FROM  customers  ',  # Test with extra whitespace
    ],
)
def test_valid_select_queries(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)

    assert result['valid'] is True


@pytest.mark.parametrize(
    'query',
    [
        '',
        '   ',
        '\n\t',
    ],
)
def test_empty_queries(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)
    assert result['valid'] is False
    assert result['errors'] == []


@pytest.mark.parametrize(
    'query',
    [
        'SELECT FROM customers',
        'SELECT * FORM customers',
        'SELECT customer_id, FROM customers',
        'SELECT * FROMM customers',
    ],
)
def test_syntax_errors(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)

    assert result['valid'] is False
    assert len(result['errors']) > 0


@pytest.mark.parametrize(
    'query',
    [
        "INSERT INTO customers (company_name) VALUES ('Test Company')",
        "UPDATE customers SET company_name = 'New Company' WHERE customer_id = 'ALFKI'",
        "DELETE FROM customers WHERE customer_id = 'ALFKI'",
        'CREATE TABLE test_table (id INT, name TEXT)',
        'DROP TABLE customers',
        'ALTER TABLE customers ADD COLUMN email TEXT',
    ],
)
def test_non_select_queries(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)

    assert result['valid'] is False
    assert len(result['errors']) == 1
    # assert result['errors'][0]['message'] == 'Only SELECT queries are allowed.'
    # assert result['errors'][0]['line'] == 1


@pytest.mark.parametrize(
    'query',
    [
        'SELECT * FROM nonexistent_table',
        'SELECT unknown_column FROM customers',
    ],
)
def test_semantic_errors(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)

    assert result['valid'] is False
    assert len(result['errors']) == 1
    assert result['errors'][0]['line'] == 1


@pytest.mark.parametrize(
    'query',
    [
        """
    SELECT 
        c.customer_id, 
        c.company_name, 
        COUNT(o.order_id) as order_count, 
        SUM(od.quantity * od.unit_price) as total_spent
    FROM 
        customers c
    LEFT JOIN 
        orders o ON c.customer_id = o.customer_id
    LEFT JOIN 
        order_details od ON o.order_id = od.order_id
    WHERE 
        c.country IN ('Germany', 'USA', 'UK')
    GROUP BY 
        c.customer_id, c.company_name
    HAVING 
        COUNT(o.order_id) > 0
    ORDER BY 
        total_spent DESC
    LIMIT 10
    """,
        #     """
        # SELECT DISTINCT ON (country)
        #     country,
        #     city,
        #     COUNT(customer_id) as customer_count
        # FROM customers
        # GROUP BY country, city
        # ORDER BY country, customer_count DESC
        # """,
        #     """
        # WITH product_sales AS (
        #     SELECT
        #         p.product_id,
        #         p.product_name,
        #         c.category_name,
        #         SUM(od.quantity * od.unit_price) as total_sales,
        #         RANK() OVER (PARTITION BY p.category_id ORDER BY SUM(od.quantity * od.unit_price) DESC) as rank
        #     FROM products p
        #     JOIN categories c ON p.category_id = c.category_id
        #     JOIN order_details od ON p.product_id = od.product_id
        #     GROUP BY p.product_id, p.product_name, c.category_name
        # )
        # SELECT product_name, category_name, total_sales
        # FROM product_sales
        # WHERE rank = 1
        # """,
    ],
)
def test_complex_valid_queries(query, db_info, setup_test_db):
    result = validate_sql(query, db_info)

    assert result['valid'] is True


def test_sql_injection_attempt(db_info, setup_test_db):
    query = 'SELECT * FROM customers; DROP TABLE customers;'

    result = validate_sql(query, db_info)

    assert result['valid'] is False
