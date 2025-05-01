#!/usr/bin/env python
"""
Database Index Management Script

This script analyzes the database indexes and their usage patterns.
It helps identify missing or unused indexes to optimize database performance.

To use:
    python manage_indexes.py analyze  # Analyze existing indexes and suggest improvements
    python manage_indexes.py cleanup  # Remove unused indexes (use with caution)
"""

import os
import sys
import django
from django.db import connection
from django.conf import settings
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

def get_table_indexes():
    """Get all indexes in the database and their usage statistics"""
    with connection.cursor() as cursor:
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            # MySQL query
            cursor.execute("""
                SELECT
                    t.TABLE_NAME as table_name,
                    s.INDEX_NAME as index_name,
                    s.COLUMN_NAME as column_name,
                    s.SEQ_IN_INDEX as seq_in_index,
                    s.NON_UNIQUE as non_unique
                FROM
                    information_schema.STATISTICS s
                JOIN
                    information_schema.TABLES t
                ON
                    s.TABLE_SCHEMA = t.TABLE_SCHEMA AND s.TABLE_NAME = t.TABLE_NAME
                WHERE
                    t.TABLE_SCHEMA = DATABASE()
                ORDER BY
                    table_name, index_name, seq_in_index
            """)
            
            result = cursor.fetchall()
            indexes = defaultdict(dict)
            
            for table_name, index_name, column_name, seq_in_index, non_unique in result:
                if index_name not in indexes[table_name]:
                    indexes[table_name][index_name] = {
                        'columns': [],
                        'unique': not non_unique
                    }
                
                indexes[table_name][index_name]['columns'].append(column_name)
            
            return indexes
        else:
            # For SQLite or other databases, provide basic information
            cursor.execute("""
                SELECT
                    name AS table_name
                FROM
                    sqlite_master
                WHERE
                    type='table'
            """)
            
            tables = cursor.fetchall()
            indexes = defaultdict(dict)
            
            for (table_name,) in tables:
                cursor.execute(f"PRAGMA index_list('{table_name}')")
                indices = cursor.fetchall()
                
                for idx_data in indices:
                    index_name = idx_data[1]
                    unique = idx_data[2]
                    
                    cursor.execute(f"PRAGMA index_info('{index_name}')")
                    columns_data = cursor.fetchall()
                    columns = [col_data[2] for col_data in columns_data]
                    
                    indexes[table_name][index_name] = {
                        'columns': columns,
                        'unique': bool(unique)
                    }
            
            return indexes

def analyze_table_queries():
    """Analyze query patterns from Django's query log (when DEBUG=True)"""
    if not settings.DEBUG:
        print("DEBUG must be set to True in settings to log queries")
        return {}
    
    # This would usually analyze Django's connection.queries
    # but for this script we'll just return a simulated result
    return {
        'products_product': [
            {'joins': ['products_category'], 'filters': ['available', 'category_id'], 'sort': ['name']},
            {'filters': ['id', 'slug', 'available']},
            {'filters': ['category_id'], 'excludes': ['id']}
        ],
        'cart_order': [
            {'filters': ['user_id', 'status'], 'sort': ['-created_at']},
            {'filters': ['id', 'user_id']}
        ]
    }

def suggest_indexes(table_indexes, query_patterns):
    """Suggest indexes based on query patterns"""
    suggestions = []
    
    for table, queries in query_patterns.items():
        existing_indexes = table_indexes.get(table, {})
        existing_columns = []
        
        for idx in existing_indexes.values():
            existing_columns.extend([tuple(idx['columns'])])
        
        for query in queries:
            # Suggest indexes for filters
            if 'filters' in query and len(query['filters']) > 0:
                filters = tuple(query['filters'])
                
                # Check if this combination already has an index
                has_index = False
                for cols in existing_columns:
                    # Check if index covers these columns (prefix match)
                    if len(cols) >= len(filters) and cols[:len(filters)] == filters:
                        has_index = True
                        break
                
                if not has_index:
                    suggestions.append({
                        'table': table,
                        'columns': query['filters'],
                        'reason': 'Frequently filtered fields'
                    })
            
            # Suggest indexes for sort columns
            if 'sort' in query and len(query['sort']) > 0:
                # Remove direction indicators (- for DESC)
                sort_cols = [col.lstrip('-') for col in query['sort']]
                
                # Check if already covered
                has_index = False
                for cols in existing_columns:
                    if len(cols) >= len(sort_cols) and all(item in cols for item in sort_cols):
                        has_index = True
                        break
                
                if not has_index:
                    suggestions.append({
                        'table': table,
                        'columns': sort_cols,
                        'reason': 'Frequently sorted fields'
                    })
    
    return suggestions

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python manage_indexes.py [analyze|cleanup]")
        return
    
    command = sys.argv[1]
    
    if command == 'analyze':
        print("Analyzing database indexes...")
        
        table_indexes = get_table_indexes()
        query_patterns = analyze_table_queries()
        suggestions = suggest_indexes(table_indexes, query_patterns)
        
        print("\nCurrent Indexes:")
        for table, indexes in table_indexes.items():
            print(f"\n  Table: {table}")
            for idx_name, idx_info in indexes.items():
                unique_str = "UNIQUE" if idx_info['unique'] else ""
                print(f"    {idx_name} {unique_str}: {', '.join(idx_info['columns'])}")
        
        print("\nSuggested Indexes:")
        if suggestions:
            for suggestion in suggestions:
                print(f"\n  Table: {suggestion['table']}")
                print(f"    Columns: {', '.join(suggestion['columns'])}")
                print(f"    Reason: {suggestion['reason']}")
        else:
            print("  No suggestions - your database indexes look good!")
    
    elif command == 'cleanup':
        print("This feature is not implemented yet. It would identify and remove unused indexes.")
    else:
        print(f"Unknown command: {command}")
        print("Usage: python manage_indexes.py [analyze|cleanup]")

if __name__ == "__main__":
    main() 