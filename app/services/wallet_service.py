from app.models.user import UserWallet
from app.utils.encryption_utils import EncryptionUtils
from bsv import PrivateKey


class WalletService:

    @staticmethod
    def create_wallet() -> UserWallet:
        private_key = PrivateKey()
        bsv_address = private_key.public_key().address()
        bsv_public_key = private_key.public_key().hex()
        encrypted_wif = EncryptionUtils().encrypt_wif(private_key.wif())

        return UserWallet(
            bsv_address=str(bsv_address),
            bsv_public_key=str(bsv_public_key),
            encrypted_wif= encrypted_wif
        )