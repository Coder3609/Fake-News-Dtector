from supabase import create_client, Client
from backend.core.config import settings

class SupabaseDB:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_ROLE or settings.SUPABASE_KEY
        self.is_mock = "mock" in self.url.lower() or not self.url
        
        self.client = None
        if not self.is_mock:
            try:
                self.client = create_client(self.url, self.key)
                print(f"[TruthLens Supabase] Connected to Supabase client at {self.url}")
            except Exception as e:
                print(f"[TruthLens Supabase] Client connection failed ({str(e)}). Falling back to mock database.")
                self.is_mock = True
        else:
            print("[TruthLens Supabase] Running in development mode with mock database.")

    def save_report(self, report: dict) -> bool:
        """
        Persist a finalized verification report to the 'saved_reports' table.
        """
        if self.is_mock:
            print(f"[TruthLens Supabase] MOCK SAVE: Saved verification {report.get('verification_id')}")
            return True
        try:
            response = self.client.table("saved_reports").insert(report).execute()
            return True
        except Exception as e:
            print(f"[TruthLens Supabase] Database insert error: {e}")
            return False

    def get_user_history(self, user_id: str = None) -> list:
        """
        Retrieve previous verifications for the active session.
        """
        if self.is_mock:
            # Return placeholder reports representing search history
            return [
                {
                    "verification_id": "4d76c3b7-dfde-4fab-8b55-1a3e4f4344b0",
                    "status": "Supported by Evidence",
                    "summary": "NASA satellite confirms temperature anomalies in the atmosphere.",
                    "verification_timestamp": "2026-06-25T13:23:10Z"
                }
            ]
        try:
            query = self.client.table("verification_history").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.order("verification_timestamp", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"[TruthLens Supabase] Database select error: {e}")
            return []

supabase_db = SupabaseDB()
