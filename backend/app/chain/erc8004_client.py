from app.config import Settings


class ERC8004Client:
    def __init__(self, settings: Settings):
        self.settings = settings

    def record_feedback(self, chain_job_id: str, user_address: str, score: int, comment: str | None) -> str | None:
        return None

