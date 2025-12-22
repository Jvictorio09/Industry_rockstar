from web3 import Web3
from django.conf import settings
from decimal import Decimal
import logging
from .erc20_abi import USDC_ABI

logger = logging.getLogger(__name__)

class Web3Service:
    def __init__(self):
        rpc_url = getattr(settings, 'BASE_RPC_URL', None)
        if not rpc_url or rpc_url.strip() == "":
            raise ValueError(
                "BASE_RPC_URL must be set in settings. "
                "Please add BASE_RPC_URL to your .env file. "
                "Format: BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
            )
        
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(
                    f"Failed to connect to Base network using RPC URL. "
                    f"Please check your BASE_RPC_URL in .env file. "
                    f"URL starts with: {rpc_url[:30]}..."
                )
        except Exception as e:
            raise ConnectionError(
                f"Error connecting to Base network: {str(e)}. "
                f"Please verify your BASE_RPC_URL is correct."
            )
        
        # Initialize USDC contract
        usdc_address = getattr(settings, 'USDC_CONTRACT_ADDRESS', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
        self.usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=USDC_ABI
        )
    
    def usdc_to_raw(self, usdc_amount):
        """Convert USDC amount to raw units (with 6 decimals)"""
        decimals = getattr(settings, 'USDC_DECIMALS', 6)
        return int(Decimal(str(usdc_amount)) * Decimal(10 ** decimals))
    
    def raw_to_usdc(self, raw_amount):
        """Convert raw units to USDC amount"""
        decimals = getattr(settings, 'USDC_DECIMALS', 6)
        return Decimal(str(raw_amount)) / Decimal(10 ** decimals)
    
    def get_transaction(self, tx_hash):
        """Get transaction details from blockchain"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'transaction': tx,
                'receipt': receipt,
                'status': receipt.status,  # 1 = success, 0 = failed
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'logs': receipt.logs,
            }
        except Exception as e:
            logger.error(f"Error fetching transaction {tx_hash}: {e}")
            return None
    
    def get_current_block(self):
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_confirmations(self, block_number):
        """Get number of confirmations for a block"""
        current_block = self.get_current_block()
        if block_number:
            return max(0, current_block - block_number)
        return 0
    
    def parse_transfer_events(self, receipt_logs):
        """Parse Transfer events from transaction logs"""
        transfer_events = []
        
        for log in receipt_logs:
            try:
                # Try to decode as Transfer event
                event = self.usdc_contract.events.Transfer().process_log(log)
                transfer_events.append({
                    'from': event.args['from'],
                    'to': event.args['to'],
                    'value': event.args['value'],
                    'log_index': log.logIndex,
                })
            except Exception:
                # Not a Transfer event, skip
                continue
        
        return transfer_events
    
    def verify_usdc_transfer(self, tx_hash, expected_to_address, expected_amount_raw=None, expected_from_address=None):
        """
        Verify USDC Transfer event matches expected parameters.
        
        Returns: (is_valid, message, transfer_event)
        """
        tx_data = self.get_transaction(tx_hash)
        if not tx_data:
            return False, "Transaction not found", None
        
        receipt = tx_data['receipt']
        
        # Check transaction status
        if receipt.status != 1:
            return False, "Transaction failed", None
        
        # Parse Transfer events
        transfer_events = self.parse_transfer_events(receipt.logs)
        
        if not transfer_events:
            return False, "No Transfer events found in transaction", None
        
        # Find Transfer event to our receiving wallet
        target_transfer = None
        for event in transfer_events:
            if event['to'].lower() == expected_to_address.lower():
                target_transfer = event
                break
        
        if not target_transfer:
            return False, f"No Transfer event found to receiving wallet {expected_to_address}", None
        
        # Verify recipient
        if target_transfer['to'].lower() != expected_to_address.lower():
            return False, f"Recipient mismatch: {target_transfer['to']} != {expected_to_address}", None
        
        # Verify amount if provided
        if expected_amount_raw is not None:
            # Allow small tolerance for rounding (1 unit = 0.000001 USDC)
            tolerance = 1
            if abs(target_transfer['value'] - expected_amount_raw) > tolerance:
                return False, f"Amount mismatch: {target_transfer['value']} != {expected_amount_raw}", None
        
        # Verify from address if provided
        if expected_from_address is not None:
            if target_transfer['from'].lower() != expected_from_address.lower():
                return False, f"Sender mismatch: {target_transfer['from']} != {expected_from_address}", None
        
        return True, "Transfer verified", target_transfer

