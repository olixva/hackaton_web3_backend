from datetime import datetime
from beanie import PydanticObjectId
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput

from app.config.settings import settings
from app.models.payment import Payment
from app.utils.encryption_utils import EncryptionUtils
from app.models.user import User

# Import WhatsOnChain utilities for BSV operations
from app.utils.whatsonchain_utils import WhatsOnChainUtils

# Fee model for transaction fees - fixed fee of 100 satoshis
# This is because python sdk does not support dynamic fee calculation yet
# And the default fee model is very low (1 satoshi per byte)
class FixedFeeModel:
    def __init__(self, value: int = 100):
        self.value = value

    def compute_fee(self, tx) -> int:
        return self.value

# PaymentService class handles BSV payment processing
class PaymentService:

    # Create and broadcast a BSV payment transaction
    @staticmethod
    async def make_payment(
        user_id: str,
        amount_satoshis: int,
    ) -> Payment:
        # Get user
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        
        # Decrypt user's private key
        user_wif = EncryptionUtils.decrypt_wif(user.user_wallet.encrypted_wif)

        # Get recipient electricity provider address
        recipient_address = settings.DESTINATION_BSV_ADDRESS
        
        # Create user private key
        sender_key = PrivateKey(user_wif)

        # Get source transaction (utxo) and output index for payment
        source_tx, source_output_index = await WhatsOnChainUtils.get_source_tx_and_index_for_payment(
            address=sender_key.address(),
            amount_satoshis=amount_satoshis,
        )

        # Create transaction input
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=source_tx.txid(),
            source_output_index=source_output_index,
            unlocking_script_template=P2PKH().unlock(sender_key),
        )

        # Create transaction outputs
        payment_output = TransactionOutput(
            locking_script=P2PKH().lock(recipient_address),
            satoshis=amount_satoshis,
        )

        # Create change output (to send remaining balance back to sender)
        change_output = TransactionOutput(
            locking_script=P2PKH().lock(sender_key.address()),
            change=True,
        )

        # Create transaction
        tx = Transaction(
            tx_inputs=[tx_input],
            tx_outputs=[payment_output, change_output],
            version=1,
        )

        # Set fixed fee of 100 (MVP)
        tx.fee(FixedFeeModel(100))

        # Sign transaction
        tx.sign()

        # Broadcast transaction to BSV network
        await tx.broadcast()

        # Save payment in database
        return await Payment(
            user_id=PydanticObjectId(user_id),
            amount_sats=amount_satoshis,
            amount_euro= await WhatsOnChainUtils.convert_satoshis_to_euro(amount_satoshis),
            tx_id=tx.txid(),
            created_at=datetime.now()
        ).insert()