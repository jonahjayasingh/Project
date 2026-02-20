from solcx import compile_standard, install_solc, set_solc_version
from web3 import Web3
from pathlib import Path
import json


def deploy_contract():
    BASE_DIR = Path(__file__).resolve().parent
    CONTRACT_PATH = BASE_DIR / "CertificateVerification.sol"
    OUT_DIR = BASE_DIR / "certificates"
    OUT_DIR.mkdir(exist_ok=True)

    ABI_PATH = OUT_DIR / "abi.json"

    # --------------------------------------------------
    # 1. Solidity compiler
    # --------------------------------------------------
    install_solc("0.8.0")
    set_solc_version("0.8.0")

    with open(CONTRACT_PATH, "r") as f:
        source = f.read()

    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            "CertificateVerification.sol": {
                "content": source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    })

    abi = compiled["contracts"]["CertificateVerification.sol"][
        "CertificateVerification"
    ]["abi"]

    bytecode = compiled["contracts"]["CertificateVerification.sol"][
        "CertificateVerification"
    ]["evm"]["bytecode"]["object"]

    # --------------------------------------------------
    # 2. Connect to Ganache
    # --------------------------------------------------
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    if not w3.is_connected():
        raise RuntimeError("Ganache is not running")

    chain_id = w3.eth.chain_id
    account = w3.eth.accounts[0]

    print("Deploying from:", account)
    print("Chain ID:", chain_id)

    # --------------------------------------------------
    # 3. Deploy contract
    # --------------------------------------------------
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx_hash = Contract.constructor().transact({
        "from": account,
        "chainId": chain_id,
        "gas": 2_000_000,
        "gasPrice": w3.to_wei(1, "gwei"),
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress

    # --------------------------------------------------
    # 4. VERIFY deployment (THIS IS THE KEY)
    # --------------------------------------------------
    code = w3.eth.get_code(contract_address)
    if code == b"":
        raise RuntimeError("❌ Contract deployment failed (no bytecode)")

    print("✅ CONTRACT DEPLOYED SUCCESSFULLY")
    print("Contract address:", contract_address)
    print("Code length:", len(code))

    # --------------------------------------------------
    # 5. Save ABI
    # --------------------------------------------------
    with open(ABI_PATH, "w") as f:
        json.dump(abi, f, indent=2)

    return contract_address


if __name__ == "__main__":
    deploy_contract()
