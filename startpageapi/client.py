import urllib.request
import urllib.parse
import urllib.error
import json
import time
import random
import re
from typing import Dict, List, Any, Optional, Union
from .endpoints import (
    SEARCH_URL, SUGGESTIONS_URL, QI_URL, DEFAULT_HEADERS, SEARCH_CATEGORIES,
    LANGUAGE_CODES, REGION_CODES, SAFE_SEARCH_LEVELS, TIME_FILTERS,
    IMAGE_SIZES, VIDEO_DURATIONS, ADVANCED_SEARCH_PARAMS
)
from .parser import StartpageParser
from .exceptions import StartpageHTTPError, StartpageRateLimitError, StartpageError
from .async_client import AsyncStartpageClient

class StartpageAPI:
    
    def __init__(self, proxy: Optional[str] = None, timeout: int = 30, delay: float = 1.0):
        self.proxy = proxy
        self.timeout = timeout
        self.delay = delay
        self.last_request_time = 0.0
        self.session_id = self._generate_session_id()
        self.aio = AsyncStartpageClient(self)
    
    def _generate_session_id(self) -> str:
        return f"sp_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        headers = DEFAULT_HEADERS.copy()
        if referer:
            headers["Referer"] = referer
        return headers
    
    def _make_request(self, url: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> str:
        self._respect_delay()
        
        if headers is None:
            headers = self._get_headers()
        
        try:
            if data:
                data_encoded = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=data_encoded, headers=headers)
            else:
                req = urllib.request.Request(url, headers=headers)
            
            if self.proxy:
                proxy_handler = urllib.request.ProxyHandler({'http': self.proxy, 'https': self.proxy})
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=self.timeout)
            else:
                response = urllib.request.urlopen(req, timeout=self.timeout)
            
            content = response.read()
            
            if response.headers.get('content-encoding') == 'gzip':
                import gzip
                content = gzip.decompress(content)
            
            return content.decode('utf-8', errors='ignore')
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise StartpageRateLimitError()
            raise StartpageHTTPError(e.code, str(e))
        except urllib.error.URLError as e:
            raise StartpageError(f"Network error: {str(e)}")
        except Exception as e:
            raise StartpageError(f"Request failed: {str(e)}")
    
    def _respect_delay(self) -> None:
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        self.last_request_time = time.time()
    
    def search(self, 
               query: str,
               language: str = "en",
               region: str = "all", 
               safe_search: str = "moderate",
               time_filter: str = "any",
               page: int = 1,
               results_per_page: int = 10,
               **kwargs) -> Dict[str, Any]:
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "web",
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language),
            "pl": REGION_CODES.get(region, region),
            "ff": SAFE_SEARCH_LEVELS.get(safe_search, "0"),
            "startat": str((page - 1) * results_per_page),
            "num": str(results_per_page)
        }
        
        if time_filter and time_filter != "any":
            params["with_date"] = TIME_FILTERS.get(time_filter, time_filter)
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "web")
    
    def images_search(self,
                     query: str,
                     language: str = "en", 
                     region: str = "all",
                     safe_search: str = "moderate",
                     size: str = "any",
                     page: int = 1,
                     **kwargs) -> Dict[str, Any]:
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "images",
            "cmd": "process_search", 
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language),
            "pl": REGION_CODES.get(region, region),
            "ff": SAFE_SEARCH_LEVELS.get(safe_search, "0"),
            "startat": str((page - 1) * 20)
        }
        
        if size and size != "any":
            params["size"] = IMAGE_SIZES.get(size, size)
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "images")
    
    def videos_search(self,
                     query: str,
                     language: str = "en",
                     region: str = "all", 
                     safe_search: str = "moderate",
                     duration: str = "any",
                     time_filter: str = "any",
                     page: int = 1,
                     **kwargs) -> Dict[str, Any]:
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "video",
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language), 
            "lui": LANGUAGE_CODES.get(language, language),
            "pl": REGION_CODES.get(region, region),
            "ff": SAFE_SEARCH_LEVELS.get(safe_search, "0"),
            "startat": str((page - 1) * 10)
        }
        
        if duration and duration != "any":
            params["duration"] = VIDEO_DURATIONS.get(duration, duration)
            
        if time_filter and time_filter != "any":
            params["with_date"] = TIME_FILTERS.get(time_filter, time_filter)
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "videos")
    
    def news_search(self,
                   query: str,
                   language: str = "en",
                   region: str = "all",
                   time_filter: str = "any", 
                   page: int = 1,
                   **kwargs) -> Dict[str, Any]:
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "news",
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language), 
            "pl": REGION_CODES.get(region, region),
            "startat": str((page - 1) * 10)
        }
        
        if time_filter and time_filter != "any":
            params["with_date"] = TIME_FILTERS.get(time_filter, time_filter)
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "news")
    
    def places_search(self,
                     query: str, 
                     language: str = "en",
                     region: str = "all",
                     latitude: Optional[float] = None,
                     longitude: Optional[float] = None,
                     radius: Optional[int] = None,
                     page: int = 1,
                     **kwargs) -> Dict[str, Any]:
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "places",
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language),
            "pl": REGION_CODES.get(region, region),
            "startat": str((page - 1) * 10)
        }
        
        if latitude is not None and longitude is not None:
            params["latitude"] = str(latitude)
            params["longitude"] = str(longitude)
            
        if radius is not None:
            params["radius"] = str(radius)
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "places")
    
    def suggestions(self, query_part: str, language: str = "en") -> List[str]:
        if not query_part.strip():
            return []
        
        params = {
            "q": query_part.strip(),
            "segment": "startpage.ucp",
            "format": "opensearch",
            "lang": LANGUAGE_CODES.get(language, language)
        }
        
        url = f"{SUGGESTIONS_URL}?{urllib.parse.urlencode(params)}"
        response_text = self._make_request(url)
        return StartpageParser.parse_suggestions(response_text)
    
    def instant_answers(self, query: str, language: str = "en", **kwargs) -> Dict[str, Any]:
        if not query.strip():
            return {"instant_answer": None, "knowledge_panel": None}
        
        # Perform a regular web search and extract instant answers from the results
        params = {
            "query": query.strip(),
            "cat": "web",
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language)
        }
        
        params.update(kwargs)
        
        html = self._make_request(SEARCH_URL, params)
        
        # Parse for instant answers and knowledge panels using enhanced detection
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        
        instant_answer = None
        knowledge_panel = None
        
        # Look for Search Expander (sxpr) content - Startpage's knowledge system
        sxpr_elements = soup.find_all(['div', 'section'], attrs={'class': re.compile(r'.*(sxpr|search-expander|sx-|wiki).*', re.I)})
        
        for element in sxpr_elements:
            text_content = StartpageParser._extract_text(element).strip()
            if text_content and len(text_content) > 20:
                # Check if this looks like an instant answer (short, factual)
                if len(text_content) < 300 and any(indicator in query.lower() for indicator in ['what is', 'how much', 'when', 'where', 'time']):
                    instant_answer = text_content
                else:
                    # Treat as knowledge panel
                    knowledge_panel = {
                        "title": "",
                        "description": text_content[:800] + "..." if len(text_content) > 800 else text_content,
                        "facts": {},
                        "source": "Startpage Knowledge"
                    }
                    
                    # Try to extract title from headings
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                    if title_elem:
                        knowledge_panel["title"] = StartpageParser._extract_text(title_elem).strip()
                    
                    break
        
        # Look for calculator/converter results in the page content
        if not instant_answer:
            calc_patterns = [
                r'= ([\d,.\s]+)',  # Calculator results
                r'([\d,.\s]+ [A-Za-z]+)',  # Unit conversions
                r'\b(\d+[\d,.]* [A-Za-z]{2,})\b'  # Measurements
            ]
            
            for pattern in calc_patterns:
                match = re.search(pattern, html)
                if match:
                    instant_answer = match.group(1).strip()
                    break
        
        # Look for time/date answers
        if not instant_answer and any(time_word in query.lower() for time_word in ['time', 'date', 'today', 'now']):
            time_patterns = [
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\b',  # Time
                r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',  # Day
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'  # Date
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, html, re.I)
                if match:
                    instant_answer = match.group(0).strip()
                    break
        
        # Look for weather information
        if not instant_answer and 'weather' in query.lower():
            weather_elements = soup.find_all(['span', 'div'], attrs={'class': re.compile(r'.*(temp|weather|degree).*', re.I)})
            for elem in weather_elements:
                text = StartpageParser._extract_text(elem).strip()
                if re.search(r'\d+°[CF]?', text):
                    instant_answer = text
                    break
        
        # Enhanced knowledge panel detection for Wikipedia/factual content
        if not knowledge_panel:
            wiki_indicators = ['wikipedia', 'wiki', 'encyclopedia', 'britannica']
            factual_containers = soup.find_all(['div', 'section', 'aside'], 
                                             attrs={'class': re.compile(r'.*(wiki|knowledge|info|fact|panel).*', re.I)})
            
            for container in factual_containers:
                container_text = StartpageParser._extract_text(container).lower()
                full_text = StartpageParser._extract_text(container)
                
                if any(indicator in container_text for indicator in wiki_indicators) or len(full_text) > 200:
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                    desc_elem = container.find('p')
                    
                    if title_elem or desc_elem:
                        knowledge_panel = {
                            "title": StartpageParser._extract_text(title_elem).strip() if title_elem else "",
                            "description": StartpageParser._extract_text(desc_elem).strip() if desc_elem else full_text[:500],
                            "facts": {},
                            "source": "Knowledge Panel"
                        }
                        
                        # Extract structured facts if available
                        fact_elements = container.find_all(['dt', 'th'])
                        for fact_elem in fact_elements:
                            fact_name = StartpageParser._extract_text(fact_elem).strip()
                            fact_value_elem = fact_elem.find_next_sibling(['dd', 'td'])
                            if fact_value_elem:
                                fact_value = StartpageParser._extract_text(fact_value_elem).strip()
                                if fact_name and fact_value:
                                    knowledge_panel["facts"][fact_name] = fact_value
                        
                        break
        
        return {
            "instant_answer": instant_answer,
            "knowledge_panel": knowledge_panel
        }
    
    def get_search_url(self, query: str, search_type: str = "web", **params) -> str:
        base_params = {
            "query": query,
            "cat": SEARCH_CATEGORIES.get(search_type, "web")
        }
        base_params.update(params)
        return f"{SEARCH_URL}?{urllib.parse.urlencode(base_params)}"
    
    def advanced_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Perform an advanced search with custom parameters.
        
        Args:
            query: Search query
            **kwargs: Advanced search parameters
        
        Returns:
            Dict containing search results
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        params = {
            "query": query.strip(),
            "cat": "web",
            "cmd": "process_search"
        }
        
        # Add advanced search parameters
        for key, value in kwargs.items():
            if key in ADVANCED_SEARCH_PARAMS:
                params[ADVANCED_SEARCH_PARAMS[key]] = value
        
        html = self._make_request(SEARCH_URL, params)
        return StartpageParser.parse_search_results(html, "web")
