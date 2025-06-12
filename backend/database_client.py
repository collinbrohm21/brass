"""Module to connect, insert, and retrieve information from the database."""

import psycopg2

from models import User


class DatabaseClient:
    def __init__(self):
        self._client = psycopg2.connect(
            database = 'brass',
                user = 'postgres',
                host = '127.0.0.1',
                password = '',
                port = 5432)
        
    
    def is_valid_account(self, email: str, password: str) -> bool:
        connection = self._client   
        cursor = connection.cursor()
        try:
            query = f'''select 1 from users where email= %s AND password = %s
            '''
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            if result is not None:
                return True
        finally:
            cursor.close()
        return False
    
    def persist_users(self, data: User):
        """Function to persist user data into the database.
        
        Args:
            data: A User object that contains needed user information.
            
        """
        connection = self._client
        cursor = connection.cursor()
        query = '''
        INSERT INTO users (
            first_name, last_name, email,
            username, password, teams
        ) VALUES (%s, %s, %s, %s, %s, %s)
        '''
        teams = ','.join(data.teams) if data.teams else None
        cursor.execute(query, (
            data.first_name,
            data.last_name,
            data.email,
            data.username,
            data.password,
            teams,
        ))
        connection.commit()
        return data

    def transform_users(self, data: dict) -> User:
        """Returns a user object.
        
        Args:
            data: A dict containing user data.
        """
        return User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            email=data['email'],
            password=data.get('password'),
            teams=data.get('teams')  
        )

    