from bs4 import BeautifulSoup  # type: ignore
import xml.etree.ElementTree as ET
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
        self.visited_urls = set()
        self.sitemap_urls = set()
        self.endpoints = []
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
    
    def fetch_sitemap(self):
        """
        Mengambil dan mengurai sitemap.xml dari website
        
        Returns:
            list: Daftar URL yang ditemukan di sitemap
        """
        try:
            sitemap_url = urljoin(self.base_url, '/sitemap.xml')
            self.logger.info(f"Fetching sitemap from: {sitemap_url}")
            
            response = requests.get(sitemap_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch sitemap: HTTP {response.status_code}")
                return []
            
            # Parse XML sitemap
            root = ET.fromstring(response.content)
            
            # Extract URLs from sitemap
            urls = []
            # Namespace handling for sitemap XML
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Look for <url> elements and extract <loc>
            for url in root.findall('.//sm:url/sm:loc', ns):
                urls.append(url.text)
                self.sitemap_urls.add(url.text)
            
            # Look for sitemap index files
            for sitemap in root.findall('.//sm:sitemap/sm:loc', ns):
                sub_sitemap_url = sitemap.text
                self.logger.info(f"Found sub-sitemap: {sub_sitemap_url}")
                # Recursively process sub-sitemaps if needed
                # This would be implemented in a more complete version
            
            self.logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
            
        except ET.ParseError:
            self.logger.error("Failed to parse sitemap XML")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return []
    
    def parse_robots_txt(self):
        """
        Mengambil dan mengurai file robots.txt untuk menemukan path tersembunyi
        
        Returns:
            list: Daftar path yang ditemukan di robots.txt
        """
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.logger.info(f"Fetching robots.txt from: {robots_url}")
            
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch robots.txt: HTTP {response.status_code}")
                return []
            
            paths = []
            lines = response.text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('Disallow:') or line.startswith('Allow:'):
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        path = parts[1].strip()
                        if path and path != '/':
                            paths.append(urljoin(self.base_url, path))
            
            self.logger.info(f"Found {len(paths)} paths in robots.txt")
            return paths
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return []
    
    def crawl_page(self, url, depth=2):
        """
        Melakukan crawling halaman web untuk menemukan link
        
        Args:
            url (str): URL yang akan di-crawl
            depth (int): Kedalaman crawling
            
        Returns:
            list: Daftar URL yang ditemukan
        """
        if depth <= 0 or url in self.visited_urls:
            return []
        
        # Normalisasi URL agar memiliki scheme
        url = self._normalize_base_url(url)
        self.visited_urls.add(url)
        found_urls = []
        
        try:
            self.logger.info(f"Crawling: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # Extract all links (gunakan BeautifulSoup jika tersedia, jika tidak gunakan regex)
            links_hrefs = []
            if BeautifulSoup is not None:
                soup = BeautifulSoup(response.text, 'html.parser')
                links_hrefs = [link['href'] for link in soup.find_all('a', href=True)]
            else:
                # Fallback sederhana jika bs4 tidak terpasang
                import re
                self.logger.warning("BeautifulSoup (bs4) tidak terpasang; menggunakan fallback regex untuk ekstraksi link.")
                links_hrefs = re.findall(r'(?i)<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\']', response.text)

            for href in links_hrefs:
                full_url = urljoin(url, href)
                
                # Only follow links to the same domain
                if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                    found_urls.append(full_url)
                    # Emit output for each discovered URL so caller can persist
                    self._log(full_url)
                    
                    # Recursively crawl if not at max depth
                    if depth > 1 and full_url not in self.visited_urls:
                        sub_urls = self.crawl_page(full_url, depth - 1)
                        found_urls.extend(sub_urls)
            
            return found_urls
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while crawling {url}: {e}")
            return []
    
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
            "' OR 1=1--",
            "') OR ('1'='1",
            "1' OR '1'='1",
            "' UNION SELECT NULL--",
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
        ]

        findings = []

        # Batasi jumlah pengujian agar tidak terlalu agresif
        max_urls_per_param = 2
        max_payloads_per_param = 3

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

                    # Uji beberapa payload per URL
                    for payload in sqli_payloads[:max_payloads_per_param]:
                        mutated_pairs = [(k, (payload if k == param_name else v)) for (k, v) in pairs]
                        mutated_qs = '&'.join([f"{k}={v}" for (k, v) in mutated_pairs])
                        mutated_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{mutated_qs}"
                        try:
                            resp = requests.get(mutated_url, headers=self.headers, timeout=7)
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
                        except Exception:
                            # Abaikan error koneksi/timeouts agar scanner tetap berjalan
                            pass
                except Exception:
                    # Abaikan URL yang tidak dapat di-parse
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
            "sitemap_urls": [],
            "robots_txt_paths": [],
            "crawled_urls": [],
            "parameters": {},
            "potential_vulnerabilities": {}
        }
        
        # [Sementara] Nonaktifkan pengambilan dari sitemap dan robots.txt
        # sitemap_urls = self.fetch_sitemap()
        # results["sitemap_urls"] = list(sitemap_urls)
        # robots_paths = self.parse_robots_txt()
        # results["robots_txt_paths"] = robots_paths

        # Crawl domain menggunakan fungsi crawl_domain
        crawled = self.crawl_domain(max_pages=500, delay=0.5, include_subdomains=True)
        results["crawled_urls"] = crawled

        # Extract and analyze parameters dari hasil crawl saja
        parameters = self.extract_parameters(crawled)
        results["parameters"] = parameters
        
        # 5. Scan for vulnerabilities (aktifkan)
        vulnerabilities = self.scan_for_sqli_vulnerabilities(parameters)
        results["potential_vulnerabilities"] = vulnerabilities
        
        return results