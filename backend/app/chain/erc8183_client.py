import json
from pathlib import Path

from web3 import Web3

from app.chain.arc_client import ArcClient
from app.config import Settings


class ERC8183Client:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.arc = ArcClient(settings)

    def _load_abi(self) -> list[dict]:
        abi_path = Path(__file__).resolve().parents[3] / "contracts" / "abis" / "ERC8183.json"
        payload = json.loads(abi_path.read_text(encoding="utf-8"))
        return payload["abi"] if isinstance(payload, dict) and "abi" in payload else payload

    def _contract(self):
        if not self.settings.erc8183_contract_address:
            raise RuntimeError("ERC8183_CONTRACT_ADDRESS is not configured")
        return self.arc.web3.eth.contract(
            address=Web3.to_checksum_address(self.settings.erc8183_contract_address),
            abi=self._load_abi(),
        )

    def submit_deliverable(self, chain_job_id: str, report_hash: str) -> str:
        if not self.settings.submit_to_chain:
            return f"mock-submit-{chain_job_id}-{report_hash[:10]}"

        contract = self._contract()
        account = self.arc.account
        job_id = int(chain_job_id)
        digest = bytes.fromhex(report_hash.removeprefix("0x"))
        function = contract.functions.submit(job_id, digest)
        tx = function.build_transaction(
            {
                "from": account.address,
                "nonce": self.arc.web3.eth.get_transaction_count(account.address),
                "chainId": self.settings.arc_chain_id,
            }
        )
        signed = account.sign_transaction(tx)
        tx_hash = self.arc.web3.eth.send_raw_transaction(signed.rawTransaction)
        return self.arc.web3.to_hex(tx_hash)

    def get_job(self, chain_job_id: str):
        contract = self._contract()
        return contract.functions.getJob(int(chain_job_id)).call()

