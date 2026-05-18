from functools import cached_property

from web3 import Web3

from app.config import Settings


class ArcClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    @cached_property
    def web3(self) -> Web3:
        if not self.settings.arc_rpc_url:
            raise RuntimeError("ARC_RPC_URL is not configured")
        return Web3(Web3.HTTPProvider(self.settings.arc_rpc_url))

    @cached_property
    def account(self):
        if not self.settings.private_key_agent:
            raise RuntimeError("PRIVATE_KEY_AGENT is not configured")
        return self.web3.eth.account.from_key(self.settings.private_key_agent)

