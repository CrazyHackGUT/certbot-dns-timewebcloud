"""
DNS authenticator for Timeweb Cloud DNS
"""

import logging
from typing import Callable

from certbot import errors
from certbot.plugins import dns_common

from .api import TWAPIClient


logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """
    DNS Authenticator for Timeweb Cloud

    This Authenticator uses the Timeweb Cloud API to fulfill a DNS-01 challenge.
    """

    description = (
        "Obtain certificates using a DNS TXT record (if you are using Timeweb Cloud "
        + "infrastructure for DNS)."
    )
    ttl = 300


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials = None
        self._for_cleanup = {}


    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None],  # pylint: disable=arguments-differ
                             default_propagation_seconds: int = 10) -> None:
        super().add_parser_arguments(
            add, default_propagation_seconds=10
        )
        add("credentials", help="Timeweb Cloud credentials INI file.")


    def more_info(self) -> str:
        return (
            "This plugin configures a DNS TXT record to respond to a DNS-01 challenge using "
            + "the Timeweb Cloud API."
        )


    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Timeweb Cloud credentials INI file",
            {
                "api_key": "Timeweb Cloud API key"
            }
        )
        # TODO: add API URL for testing purposes


    def _perform(self, domain: str, validation_name: str,
                 validation: str) -> None:
        client = self._get_twcloud_api_client()
        response = client.check_token()
        if 'status' not in response:
            raise errors.PluginError(
                "Invalid Timeweb Cloud API response when checking token: "
                + "not found 'status' in response body"
            )

        if response['status']['is_blocked']:
            raise errors.PluginError("User is blocked")

        key = f"{validation_name}{domain}"
        if key not in self._for_cleanup:
            self._for_cleanup[key] = []
        record_id = client.create_acme_record(domain, validation, validation_name.rstrip('.'))
        self._for_cleanup[key].append(record_id)


    def _cleanup(self, domain: str, validation_name: str,
                 validation: str) -> None:
        key = f"{validation_name}{domain}"
        if key in self._for_cleanup:
            for record_id in self._for_cleanup.pop(key):
                self._get_twcloud_api_client().delete_acme_record(domain, record_id)


    def _get_twcloud_api_client(self) -> TWAPIClient:
        return TWAPIClient(apikey=self.credentials.conf('api_key'))
