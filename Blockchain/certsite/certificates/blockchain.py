import hashlib
import json
from pathlib import Path

from web3 import Web3
from eth_account import Account
from django.conf import settings


# -------------------------------------------------------------------
# 1. Connect to Ganache (LOCAL — NOT INFURA)
# -------------------------------------------------------------------
GANACHE_RPC = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))

if not w3.is_connected():
    raise RuntimeError("Ganache not running or RPC incorrect")


# -------------------------------------------------------------------
# 2. Load ABI
# -------------------------------------------------------------------
ABI_PATH = Path(settings.BASE_DIR) / "certificates"/'certificates'  / "abi.json"

with open(ABI_PATH) as f:
    ABI = json.load(f)


# -------------------------------------------------------------------
# 3. Contract instance
# -------------------------------------------------------------------
CONTRACT_ADDRESS = Web3.to_checksum_address(
    settings.CONTRACT_ADDRESS
)

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)


# -------------------------------------------------------------------
# 4. Hash uploaded file → bytes32 (CORRECT)
# -------------------------------------------------------------------
def hash_file(file) -> bytes:
    sha = hashlib.sha256()
    for chunk in file.chunks():
        sha.update(chunk)
    return sha.digest()  # EXACTLY 32 bytes


# -------------------------------------------------------------------
# 5. Register certificate (WRITE → gas)
# -------------------------------------------------------------------
def register_certificate(file) -> str:
    acct = Account.from_key(settings.PRIVATE_KEY)
    cert_hash = hash_file(file)
    print("Connected:", w3.is_connected())
    print("RPC URL:", w3.provider.endpoint_uri)
    print("Chain ID:", w3.eth.chain_id)
    print("Latest block:", w3.eth.block_number)
    print("Contract address:", CONTRACT_ADDRESS)
    print("Contract code length:", len(w3.eth.get_code(CONTRACT_ADDRESS)))


    # ---- SAFETY CHECKS ----
    if w3.eth.get_balance(acct.address) == 0:
        raise RuntimeError("Account has zero ETH")

    if w3.eth.get_code(CONTRACT_ADDRESS) == b"":
        raise RuntimeError("Contract not deployed on this chain")

    tx = contract.functions.issueCertificate(cert_hash).build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 200_000,
        "gasPrice": w3.to_wei(1, "gwei"),
        "chainId": w3.eth.chain_id,
    })

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction    )

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.transactionHash.hex()


# -------------------------------------------------------------------
# 6. Verify certificate (READ → free)
# -------------------------------------------------------------------
def verify_certificate(file) -> bool:
    cert_hash = hash_file(file)

    if w3.eth.get_code(CONTRACT_ADDRESS) == b"":
        raise RuntimeError("Contract not deployed on this chain")

    return contract.functions.verifyCertificate(cert_hash).call()
