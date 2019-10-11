#!/usr/bin/python3

import requests
##customize
ZONE_ID=
API_KEY=
AUTH_EMAIL=
DOMAIN_NAME=
##
CF_API_URL="https://api.cloudflare.com/client/v4/"
AUTH_HEADERS = { 'X-Auth-Email': AUTH_EMAIL, 'X-Auth-Key': API_KEY, 'Content-Type': 'application/json' }

def check_http_error_code(resp):
    if resp.status_code != requests.codes.ok:
        print(resp.status_code)
        print(resp.text)
        raise Exception("HTTP return code was not ok!")

def get_dns_records(Type, Name):
    resp = requests.get(CF_API_URL + "/zones/" + ZONE_ID + "/dns_records&type={0}&name={1}".format(Type, Name), headers=AUTH_HEADERS)
    check_http_error_code(resp)
    jresp = resp.json()
    return(jresp["result"][0]['id'])

def get_own_ip_address(version = 4):
    if version == 6:
        IPIFY_API_URL="https://api6.ipify.org"
    elif version == 4:
        IPIFY_API_URL="https://api.ipify.org"
    resp = requests.get(IPIFY_API_URL)
    check_http_error_code(resp)
    return(resp.text)

def set_dns_record(DNS_ID, Type, Name, IP_Address):
    Payload = {'type': Type, 'name': Name, 'content': IP_Address, 'proxied': False, 'ttl': 1800 }
    resp = requests.put(CF_API_URL + "/zones/" + ZONE_ID + "/dns_records/" + DNS_ID, json=Payload, headers=AUTH_HEADERS )
    check_http_error_code(resp)

print("Connecting to the CloudFlare API to determin the DNS record id...")
try:
    DNS_ID_A = get_dns_records("A", DOMAIN_NAME)
    DNS_ID_AAAA = ""
    DNS_ID_AAAA = get_dns_records("AAAA", DOMAIN_NAME)
except:
    raise
else:
    print("The DNS A record id is {0}, the DNS AAAA record id is {1}".format(DNS_ID_A, DNS_ID_AAAA))

print("Get public IP address...")
try:
    IP_Address_v4 = get_own_ip_address()
    IP_Address_v6 = ""
    IP_Address_v6 = get_own_ip_address(6)
except:
    raise
else:
    print("IPv4 address is {0}, IPv6 address is {1}".format(IP_Address_v4, IP_Address_v6))
print("Push the new DNS records to CloudFlare via the API...")
try:
    set_dns_record(DNS_ID_A, "A", DOMAIN_NAME, IP_Address_v4)
    set_dns_record(DNS_ID_AAAA, "AAAA", DOMAIN_NAME, IP_Address_v6)
except:
    raise
else:
    print("Successfully pushed to the CloudFlare API")
