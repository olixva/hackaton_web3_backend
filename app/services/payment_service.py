from datetime import datetime

from beanie import PydanticObjectId
from app.config.settings import settings
from app.models.payment import Payment
from app.utils.encryption_utils import EncryptionUtils
from app.models.user import User
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput

from app.utils.whatsonchain_utils import WhatsOnChainUtils


class FixedFeeModel:
    def __init__(self, value: int = 100):
        self.value = value

    def compute_fee(self, tx) -> int:
        return self.value


class PaymentService:

    @staticmethod
    async def make_payment(
            user_id: str,
            amount_satoshis: int,
    ) -> Payment:
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        user_wif = EncryptionUtils.decrypt_wif(user.user_wallet.encrypted_wif)

        recipient_address = settings.DESTINATION_BSV_ADDRESS
        sender_key = PrivateKey(user_wif)

        source_tx, source_output_index = await WhatsOnChainUtils.get_source_tx_and_index_for_payment(
            address=sender_key.address(),
            amount_satoshis=amount_satoshis,
        )

        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=source_tx.txid(),
            source_output_index=source_output_index,
            unlocking_script_template=P2PKH().unlock(sender_key),
        )

        payment_output = TransactionOutput(
            locking_script=P2PKH().lock(recipient_address),
            satoshis=amount_satoshis,
        )

        change_output = TransactionOutput(
            locking_script=P2PKH().lock(sender_key.address()),
            change=True,
        )

        tx = Transaction(
            tx_inputs=[tx_input],
            tx_outputs=[payment_output, change_output],
            version=1,
        )

        tx.fee(FixedFeeModel(100))

        tx.sign()

        await tx.broadcast()

        return await Payment(
            user_id=PydanticObjectId(user_id),
            amount_sats=amount_satoshis,
            amount_euro= await WhatsOnChainUtils.convert_satoshis_to_euro(amount_satoshis),
            tx_id=tx.txid(),
            created_at=datetime.now()
        ).insert()