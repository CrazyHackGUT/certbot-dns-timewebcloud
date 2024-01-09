# certbot-dns-timewebcloud
Certbot plugin for Timeweb Cloud DNS.

## Installation
```commandline
pip install certbot-dns-timewebcloud
```

## Getting started
Get Timeweb Cloud [access token](https://timeweb.cloud/my/api-keys) and fill credentials configuration.
Example below.

Then issue a certificate with command like:
```commandline
certbot certonly --authenticator dns-timewebcloud \
    --dns-timewebcloud-credentials /etc/letsencrypt/twcloud-creds.ini \
    -d example.org -d *.example.org
```

## Plugin arguments
- `--dns-timewebcloud-credentials` - path to Credentials configuration.
- `--dns-timewebcloud-propagation-seconds` - seconds when DNS record is propagated (default: 10)

## Configuration example
```ini
# /etc/letsencrypt/twcloud-creds.ini is a suggested path for
# configuration file. You may place him in any place.
dns_timewebcloud_api_key = XXXXXXXXXXXXXXXXXXX
```
