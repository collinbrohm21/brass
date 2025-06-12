"""Module to automatically create and delete specified tables."""
import argparse
import json
import logging

import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CREATE = 'create'
DELETE = 'delete'
OPERATION = 'operation'
TABLES = 'tables'

class DatabaseConstructor:
    # TODO: Move credentials.
    def __init__(self):
        self._client = psycopg2.connect(
                database = 'score_sync',
                user = 'postgres',
                host = '127.0.0.1',
                password = '',
                port = 5432)
        
    def create_table(self, table_name: str, table_schema: dict[str, str]):
        """Create a table given the table schema.

        Args:
            table_schema: Dictionary of column names to column data types.
        """
        column_definitions = ', '.join(
            [f"{column} {dtype}" for column, dtype in table_schema.items() if column != "constraints"]
        )

        constraints = table_schema.get("constraints")
        if constraints : 
            constraints_definitions = ', '.join(constraints)
            column_definitions += f', {constraints_definitions}'

        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})'
        connection = self._client
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        self._client.close()

    def delete_table(self, table_name: str):
        """Deletes table from database.

        Args:
            table_name: Name of table to delete.
        """
        query = f'DROP TABLE IF EXISTS {table_name}'
        connection = self._client
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        self._client.close()

def main():
    """Main execution function."""
    args = parse_args()
    database = DatabaseConstructor()

    logging.info(f'Starting the script with config file: {args.config_file} and '
         f'tables: {", ".join(args.tables)}')

    # Load the configuration.
    config = load_config(args.config_file)

    # Ensure that the 'operation' keyword is available and valid.
    try:
        operation = config[OPERATION]
    except KeyError:
        raise ValueError('The configuration file is missing the "operation" '
            'key.')

    if operation not in [CREATE, DELETE]:
        raise ValueError('Invalid operation specified. Use "create" or '
            '"delete".')

    # Validate the databases that will be operated on.
    valid_table_names = set(config['tables'])
    if not set(args.tables).issubset(valid_table_names):
        logging.error('Invalid database names specified. Only the following '
            'databases are allowed: %s', ', '.join(valid_table_names))
        return
    
    if operation == 'create':
        for table in args.tables:
            table_schema = config['tables'][table]
            database.create_table(table, table_schema)
    elif operation == 'delete':
        for table in args.tables:
            database.delete_table(table)

def parse_args() -> argparse.Namespace:
    """Command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='Path to config file')
    parser.add_argument('--tables', nargs='+', help='Name of tables to operate on')
    parser.add_argument('--log-level', dest='log_level', default='DEBUG', 
                        help='Log level')

    return parser.parse_args()

def load_config(config_file: str):
    """Loads the configuration from a JSON file.

    Args:
        config_file: The path to the configuration file.

    Returns:
        The loaded configuration.
    """
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config

if __name__ == '__main__':
    main()
