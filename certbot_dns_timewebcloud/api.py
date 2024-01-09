"""
Timeweb Cloud API client for DNS
"""

import logging
import requests


class TWAPIClient():
    """
    Simple Timeweb Cloud API client for working with ACME challenge records
    """
    PUBLIC_API_URL = "https://api.timeweb.cloud"


    def __init__(self, apikey: str, base_url: str=PUBLIC_API_URL):
        self._base_url = base_url
        self.session = requests.session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apikey}"
        })


    def check_token(self) -> dict:
        """
        Verifies the token via requesting account status.
        :return: dict with info
        """
        request_url = f"{self._base_url}/api/v1/account/status"
        with self.session.get(request_url) as response:
            response.raise_for_status()
            return response.json()


    def create_acme_record(self, domain: str, token: str, record_name: str):
        """
        Creates a new DNS record via TW Cloud API.
        :param domain: The base domain
        :param token: Verification string for writing in DNS record
        :param record_name: DNS domain fullname
        :return: Record identifier in API (if everything is ok)
        """
        offset = len(domain.split(".")) * -1
        subdomain = ".".join(record_name.split(".")[:offset])

        request_url = f"{self._base_url}/api/v1/domains/{domain}/dns-records"
        request_body = {
            "subdomain": subdomain,
            "type": "TXT",
            "value": token
        }

        with self.session.post(request_url, json=request_body) as response:
            response.raise_for_status()
            body = response.json()
            record_id = body["dns_record"]["id"]

            logging.info(
                f"Created ACME DNS-01 challenge DNS record {record_id} for domain {domain}"
            )
            return record_id


    def delete_acme_record(self, domain: str, record_id: int):
        """
        Removes a DNS record via TW Cloud API.
        :param domain: The base domain.
        :param record_id: Identifier of created previously record.
        """
        request_url = f"{self._base_url}/api/v1/domains/{domain}/dns-records/{record_id}"
        with self.session.delete(request_url) as response:
            status = response.status_code
            if status == 204:
                logging.info(f"DNS record {record_id} deleted for domain {domain}")
                return

            if status == 404:
                logging.warning(
                    f"Failed to delete DNS record {record_id} for domain {domain} - not exist"
                )
            response.raise_for_status()
