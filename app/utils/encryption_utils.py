from cryptography.fernet import Fernet

from app.config.settings import settings


class EncryptionUtils:

    # Get Fernet instance for encryption/decryption
    @staticmethod
    def _get_fernet() -> Fernet:
        encryption_secret = settings.ENCRYPTION_SECRET.encode("utf-8")
        return Fernet(encryption_secret)

    # Encrypt a WIF (Wallet Import Format) string
    @staticmethod
    def encrypt_wif(wif: str) -> str:
        fernet = EncryptionUtils._get_fernet()
        token = fernet.encrypt(wif.encode("utf-8"))
        return token.decode("utf-8")

    # Decrypt an encrypted WIF string
    @staticmethod
    def decrypt_wif(encrypted_wif: str) -> str:
        fernet = EncryptionUtils._get_fernet()
        wif_bytes = fernet.decrypt(encrypted_wif.encode("utf-8"))
        return wif_bytes.decode("utf-8")
