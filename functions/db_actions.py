from .supabase_client import supabase_client, supabase_admin

class DBActions:
    """
DBActions class provides methods to interact with a Supabase database.

Attributes:
    supabase: 
        An instance of the Supabase client (for authenticated requests).
    use_admin: 
        Boolean to determine if admin client should be used (bypasses RLS).

## Methods:
    - __init__(use_admin: bool = False):
    - create(table: str, data: dict):
        Creates an entry with the provided data into the given table 
    - update(table: str, data: dict, id: str):
        Updates entries in the given table with passed data with the specified id.
    - delete(table: str, id: str):
        Retrieves an entry from the given table with the specified id.
    - get(table: str, id: str):
        Retrieves an entry from the given table with the specified id.
    - list(table: str):
        Retrieves all entries from the given table.
    """
    supabase = None
    def __init__(self, use_admin: bool = False):
        """
        Initializes the DBActions instance by setting supabase to the appropriate client.
        
        Args:
            use_admin (bool): If True, uses the admin client (bypasses RLS). 
                            Default False uses the authenticated user client.
        
        If the client instance is not available, an exception is caught and the
        supabase attribute is set to None.
        """
        try:
            self.supabase = supabase_admin if use_admin else supabase_client
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
    
    def get_many(self, table: str, field: str, value: str):
        """
        Retrieves all entries from the given table with the specified field and value.
        
        Args:
            table (str): The name of the table to query.
            field (str): The field to filter the entries by.
            value (str): The value to filter the entries by.
        
        Returns:
            dict - or None: The response from the database if the query is successful, otherwise None.
        """
        if self.supabase:
            response = self.supabase.table(table).select().eq(field, value).execute()
            return response
        return None
    
    def get_by_field(self, table: str, field: str, value: str):
        """
        Retrieves an entry from the given table with the specified field and value.
        
        Args:
            table (str): The name of the table to query.
            field (str): The field to filter the entry by.
            value (str): The value to filter the entry by.
        
        Returns:
            dict or None: The response from the database if the query is successful, otherwise None.
        """
        if self.supabase:
            response = self.supabase.table(table).select().eq(field, value).execute()
            return response
        return None
    
    def batch_update(self, table: str, updates: list):
        """
        Updates multiple records in a single call.
        
        Args:
            table (str): The name of the table to update.
            updates (list): List of dicts, each containing 'id' and other fields to update.
                           Example: [{'id': '123', 'position': 3}, {'id': '456', 'position': 4}]
        
        Returns:
            list: List of responses from Supabase for each update.
        """
        if not self.supabase or not updates:
            return None
        
        responses = []
        for update_data in updates:
            record_id = update_data.pop('id')
            response = self.supabase.table(table).update(update_data).eq('id', record_id).execute()
            responses.append(response)
        
        return responses