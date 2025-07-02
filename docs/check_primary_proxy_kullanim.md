# Primary Proxy Kontrol Playbook'u Kullanım Dokümanı

## Amaç

Bu playbook, bir Zabbix proxy'nin erişilebilir olup olmadığını önce Zabbix API üzerinden, ardından ICMP ping ile kontrol eder. Sonucu `success` veya `failure` olarak belirtir.  
Playbook, AWX'te bir Job Template olarak çalıştırılır ve değişkenler (variables) YAML formatında input olarak girilir.

---

## Gerekli Inputlar (Variables)

AWX Job Template'te, playbook'u başlatırken aşağıdaki gibi bir YAML formatında değişkenler girilmelidir:

```yaml
---
zabbix_url: "http://10.134.16.210/zabbix/api_jsonrpc.php"
zabbix_user: "Admin"
zabbix_password: "zabbix"
primary_proxy_host: "zabbix-demo-proxy-1"
dr_proxy_host: "zabbix-demo-proxy-dr-1"
```

| Değişken Adı         | Açıklama                                                      | Örnek Değer                                      |
|----------------------|--------------------------------------------------------------|--------------------------------------------------|
| `zabbix_url`         | Zabbix API endpoint adresi                                   | `http://10.134.16.210/zabbix/api_jsonrpc.php`    |
| `zabbix_user`        | Zabbix API kullanıcı adı                                     | `Admin`                                          |
| `zabbix_password`    | Zabbix API şifresi                                           | `zabbix`                                         |
| `primary_proxy_host` | Kontrol edilecek primary proxy'nin envanterdeki host adı     | `zabbix-demo-proxy-1`                            |
| `dr_proxy_host`      | İlgili DR proxy'nin envanterdeki host adı                   | `zabbix-demo-proxy-dr-1`                         |

> **Not:**  
> - `primary_proxy_host` ve `dr_proxy_host` değerleri, Ansible envanterinde tanımlı host isimleri olmalıdır.
> - Host variable'ları (ör: ansible_host, ansible_user, ansible_password, vb.) envanterde ilgili host altında tanımlı olmalıdır.

---

## Playbook'un Çalışma Mantığı

1. **Envanterden Host Bilgisi Alma:**  
   - Girilen `primary_proxy_host` ismine göre, envanterden ilgili host'un variable'ları alınır.

2. **Zabbix API ile Kontrol:**  
   - `check_script_path` ile belirtilen Python scripti, primary proxy hostunda çalıştırılır.
   - Script, Zabbix API'ye bağlanıp ilgili proxy'nin son erişim zamanını kontrol eder.
   - Eğer proxy erişilebiliyorsa, sonuç `success` olur.

3. **Ping ile Kontrol:**  
   - Eğer Zabbix API kontrolü başarısız olursa, primary proxy hostuna ping atılır.
   - Ping başarılıysa, sonuç yine `success` olur.

4. **Sonuç:**  
   - Her iki kontrol de başarısız olursa, sonuç `failure` olarak belirlenir.
   - Sonuç, playbook sonunda ekrana yazdırılır.

---

## Örnek Envanter Host Variable'ları

```yaml
zabbix-demo-proxy-1:
  ansible_host: 10.134.16.80
  ansible_user: root
  ansible_password: T33!S40!Rg1
  ansible_become: true
  ansible_become_method: su
  ansible_connection: ssh

zabbix-demo-proxy-dr-1:
  ansible_host: 10.134.16.90
  ansible_user: root
  ansible_password: T33!S40!Rg1
  ansible_become: true
  ansible_become_method: su
  ansible_connection: ssh
```

---

## AWX Üzerinde Kullanım

1. **Job Template** oluşturun ve ilgili playbook'u seçin.
2. "Prompt on launch" seçeneğini aktif edin veya değişkenleri template'e ekleyin.
3. Job başlatılırken aşağıdaki gibi değişkenleri YAML formatında girin:

```yaml
---
zabbix_url: "http://10.134.16.210/zabbix/api_jsonrpc.php"
zabbix_user: "Admin"
zabbix_password: "zabbix"
primary_proxy_host: "zabbix-demo-proxy-1"
dr_proxy_host: "zabbix-demo-proxy-dr-1"
```

4. Çalıştırdığınızda, sonuç olarak "Proxy kontrol sonucu: success" veya "Proxy kontrol sonucu: failure" mesajı göreceksiniz.

---

## Notlar

- Script ve playbook'un bulunduğu yolları ortamınıza göre güncelleyin.
- Zabbix API erişimi için gerekli izinlerin ve network erişiminin olduğundan emin olun.
- Ping işlemi için ansible_worker hostunun ilgili proxy'ye erişebiliyor olması gerekir. 