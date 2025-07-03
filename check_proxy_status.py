import requests
import sys
import json
import time

# Zabbix API'ye istek gönderen yardımcı fonksiyon
def zabbix_api_request(url, payload):
    headers = {'Content-Type': 'application/json-rpc'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    return response.json()

if len(sys.argv) < 5:
    print("Kullanım: python check_proxy_status.py <zabbix_url> <zabbix_user> <zabbix_password> <proxy_name>")
    sys.exit(1)

zabbix_url = sys.argv[1]
zabbix_user = sys.argv[2]
zabbix_password = sys.argv[3]
proxy_name = sys.argv[4]

# 1. Login
login_payload = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "username": zabbix_user,
        "password": zabbix_password
    },
    "id": 1
}
login_response = zabbix_api_request(zabbix_url, login_payload)
if "result" not in login_response:
    print("Zabbix API login başarısız:", login_response)
    sys.exit(2)
auth_token = login_response["result"]

# 2. Proxy listesini çek
proxy_list_payload = {
    "jsonrpc": "2.0",
    "method": "proxy.get",
    "params": {
        "output": ["proxyid", "name", "address", "lastaccess"]
    },
    "auth": auth_token,
    "id": 2
}
proxy_response = zabbix_api_request(zabbix_url, proxy_list_payload)
if "result" not in proxy_response or not proxy_response["result"]:
    print("Zabbix proxy listesi alınamadı veya boş.")
    sys.exit(3)

# 3. Proxy'leri debug için ekrana yaz
print("DEBUG: Zabbix'ten dönen proxy listesi:")
for proxy in proxy_response["result"]:
    print(f"  - name: {proxy.get('name')}, address: {proxy.get('address')}")

# 4. Name'e göre proxy'yi bul
proxy_info = None
for proxy in proxy_response["result"]:
    if proxy.get("name") == proxy_name:
        proxy_info = proxy
        break

if not proxy_info:
    print(f"Proxy adı '{proxy_name}' ile eşleşen proxy bulunamadı.")
    sys.exit(4)

lastaccess = int(proxy_info.get("lastaccess", 0))
now = int(time.time())
diff = now - lastaccess

# 5. Erişilebilirlik Kontrolü (ör: 180 saniye eşik)
if lastaccess > 0 and diff < 180:
    print(f"Proxy (Name: {proxy_name}, Address: {proxy_info.get('address')}) erişilebilir. (Son erişim: {diff} sn önce)")
    sys.exit(0)
else:
    print(f"Proxy (Name: {proxy_name}, Address: {proxy_info.get('address')}) erişilemez! (Son erişim: {diff} sn önce)")
    sys.exit(5) 