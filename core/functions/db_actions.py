from ..supabase_client import supabase

class DBActions:
    """
DBActions class provides methods to interact with a Supabase database.

Attributes:
    supabase: An instance of the Supabase client.

Methods:
    __init__():
    create(table: str, data: dict):
    update(table: str, data: dict, id: str):
    delete(table: str, id: str):
    get(table: str, id: str):
        Retrieves an entry from the given table with the specified id.
    list(table: str):
        Retrieves all entries from the given table.
    """
    supabase = None
    def __init__(self):
        """
        Initializes the DBActions instance by setting supabase to the client instance.
        
        If the client instance is not available, an exception is caught and the
        supabase attribute is set to None.
        """
        try:
            self.supabase = supabase
        except Exception as e:
            print(f"Failed to initialize supabase client: {e}")
            self.supabase = None
        
    def create(self, table: str, data: dict):
        """
        Creates a new entry in the given table with the provided data.
        
        Args:
            table (str): The name of the table to create the entry in.
            data (dict): A dictionary of key-value pairs to be inserted into the table.
        
        Returns:
            The response from the Supabase server, or None if the server is not available.
        """
        if self.supabase:
            response = self.supabase.table(table).insert(data).execute()
            return response
        return None
    
    def update(self, table: str, data: dict, id: str):
        """
        Updates an existing entry in the given table with the provided data.
        
        Args:
            table (str): The name of the table to update the entry in.
            data (dict): A dictionary of key-value pairs to be updated in the table.
            id (str): The id of the entry to be updated.
        
        Returns:
            The response from the Supabase server, or None if the server is not available.
        """
        if self.supabase:
            response = self.supabase.table(table).update(data).eq('id', id).execute()
            return response
        return None
    
    def delete(self, table: str, id: str):
        
        """
        Deletes an entry from the given table with the specified id.
        
        Args:
            table (str): The name of the table from which the entry will be deleted.
            id (str): The id of the entry to be deleted.
        
        Returns:
            The response from the Supabase server, or None if the server is not available.
        """

        if self.supabase:
            response = self.supabase.table(table).delete().eq('id', id).execute()
            return response
        return None
    
    def get(self, table: str, id: str):
        """
        Retrieve a record from the specified table by its ID.
        Args:
            table (str): The name of the table to query.
            id (str): The ID of the record to retrieve.
        Returns:
            dict or None: The response from the database if the query is successful, otherwise None.
        """
        
        if self.supabase:
            response = self.supabase.table(table).select().eq('id', id).execute()
            return response
        return None
    
    def list(self, table: str):
        if self.supabase:
            response = self.supabase.table(table).select().execute()
            return response
        return None