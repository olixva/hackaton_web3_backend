# Import BSV library for private key generation
from bsv import PrivateKey

# Import UserWallet model and encryption utilities
from app.models.user import UserWallet
from app.utils.encryption_utils import EncryptionUtils

# WalletService class handles BSV wallet creation
class WalletService:

    # Generate a new BSV wallet with encrypted private key
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