from beanie import Document, PydanticObjectId


class Model(Document):
    """Base model class for all database documents."""

    @staticmethod
    def is_valid_id(id: str) -> bool:
        """Check if the provided string is a valid MongoDB ObjectId."""
        try:
            PydanticObjectId(id)
        except Exception:
            return False
        return True
