from beanie import Document, PydanticObjectId


class Model(Document):
    @staticmethod
    def is_valid_id(id: str) -> bool:
        try:
            PydanticObjectId(id)
        except Exception:
            return False
        return True
