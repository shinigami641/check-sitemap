import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import logging
from thirdparty.external_service import call_external_service

class SitemapScanner:
    """
    Model untuk melakukan scraping dan analisis sitemap website
    """
    
    def __init__(self, base_url):
        """
        Inisialisasi scanner dengan URL dasar
        
        Args:
            base_url (str): URL dasar website yang akan di-scan
        """
        self.base_url = base_url
        self.visited_urls = set()
        self.sitemap_urls = set()
        self.endpoints = []
        self.parameters = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
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
        
        self.visited_urls.add(url)
        found_urls = []
        
        try:
            self.logger.info(f"Crawling: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Only follow links to the same domain
                if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                    found_urls.append(full_url)
                    
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
            dict: Hasil pengujian kerentanan
        """
        # Implementasi dasar, akan dikembangkan lebih lanjut
        sqli_payloads = ["'", "1' OR '1'='1", "1; DROP TABLE users", "1' OR 1=1--"]
        vulnerable_params = {}
        
        for param_name, urls in parameters.items():
            for url in urls[:1]:  # Hanya uji URL pertama untuk setiap parameter
                for payload in sqli_payloads:
                    # Implementasi pengujian akan ditambahkan di sini
                    pass
        
        return vulnerable_params
    
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
        
        # 1. Scan sitemap
        sitemap_urls = self.fetch_sitemap()
        results["sitemap_urls"] = list(sitemap_urls)
        
        # 2. Parse robots.txt
        robots_paths = self.parse_robots_txt()
        results["robots_txt_paths"] = robots_paths
        
        # 3. Crawl website
        all_urls = list(sitemap_urls)
        all_urls.extend(robots_paths)
        
        # Start crawling from homepage if no URLs found
        if not all_urls:
            all_urls = [self.base_url]
        
        # Crawl each discovered URL
        crawled_urls = []
        for url in all_urls[:10]:  # Limit untuk demo
            found_urls = self.crawl_page(url, depth=1)
            crawled_urls.extend(found_urls)
        
        results["crawled_urls"] = list(set(crawled_urls))
        
        # 4. Extract and analyze parameters
        all_discovered_urls = list(set(all_urls + crawled_urls))
        parameters = self.extract_parameters(all_discovered_urls)
        results["parameters"] = parameters
        
        # 5. Scan for vulnerabilities (basic implementation)
        # vulnerabilities = self.scan_for_sqli_vulnerabilities(parameters)
        # results["potential_vulnerabilities"] = vulnerabilities
        
        return results