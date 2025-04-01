from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Query

class QueryModelTests(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
            cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob');")

    def test_execute_select_query(self):
        query = Query.objects.create(text="SELECT * FROM test_table")
        result = query.execute()

        self.assertEqual(result['columns'], ['id', 'name'])
        self.assertEqual(len(result['rows']), 2)
        self.assertIn(('Alice',), [row[1:] for row in result['rows']])
    
    def test_execute_invalid_query_raises(self):
        query = Query.objects.create(text="SELEC invalid SQL")
        with self.assertRaises(Exception):
            query.execute()

class QueryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
            cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob');")

    def test_create_query(self):
        response = self.client.post("/api/queries/", {
            "text": "SELECT * FROM test_table"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["text"], "SELECT * FROM test_table")

    def test_execute_query(self):
        query = Query.objects.create(text="SELECT * FROM test_table")
        
        response = self.client.post(f"/api/queries/{query.id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(results["columns"], ["id", "name"])
        self.assertEqual(len(results["rows"]), 2)
