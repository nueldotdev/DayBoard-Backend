from decouple import config
from supabase import create_client, Client

secret: str = config("SUPABASE_JWT_SECRET")
url: str = config("SUPABASE_URL")
anon_key: str = config("SUPABASE_ANON_KEY")
service_role_key: str = config("SUPABASE_SERVICE_ROLE_KEY")

# For authenticated user requests
supabase_client: Client = create_client(url, anon_key)

# For server-side operations that need to bypass RLS
supabase_admin: Client = create_client(url, service_role_key)