"""
Provides a synchronous client for interacting with the Startpage Search API.

This module defines the `StartpageAPI` class, which allows users to perform
various types of searches (web, images, videos, news, places), fetch
search suggestions, and retrieve instant answers. It handles request
construction, network communication using `urllib`, rate limiting,
and basic parsing of results by delegating to `StartpageParser`.
"""

import gzip
import json # Not actively used, consider removing if not needed for future plans
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup # For instant_answers HTML parsing

from .async_client import AsyncStartpageClient
from .endpoints import (
    ADVANCED_SEARCH_PARAMS,
    DEFAULT_HEADERS,
    IMAGE_SIZES,
    LANGUAGE_CODES,
    QI_URL, # Not actively used, consider removing
    REGION_CODES,
    SAFE_SEARCH_LEVELS,
    SEARCH_CATEGORIES,
    SEARCH_URL,
    SUGGESTIONS_URL,
    TIME_FILTERS,
    VIDEO_DURATIONS,
)
from .exceptions import (
    StartpageError,
    StartpageHTTPError,
    StartpageRateLimitError,
)
from .parser import StartpageParser


class StartpageAPI:
    """
    A synchronous client for the Startpage Search API.

    This class provides methods to interact with Startpage search functionalities,
    including web, image, video, news, and places searches, as well as
    fetching search suggestions and instant answers.

    It manages request throttling, proxy configuration, and timeout settings.
    It uses `urllib` for HTTP requests and relies on `StartpageParser` for
    processing the HTML responses.

    An asynchronous version of the client is available via the `aio` attribute.

    Attributes:
        proxy (Optional[str]): Proxy URL to use for requests (e.g., "http://localhost:8080").
        timeout (int): Timeout in seconds for network requests.
        delay (float): Minimum delay in seconds between consecutive requests.
        last_request_time (float): Timestamp of the last request made.
        session_id (str): A generated ID for the current "session" (cosmetic).
        aio (AsyncStartpageClient): An instance of the asynchronous client.
    """

    def __init__(
        self,
        proxy: Optional[str] = None,
        timeout: int = 30,
        delay: float = 1.0,
    ):
        """
        Initializes the StartpageAPI client.

        Args:
            proxy: Optional proxy server URL.
            timeout: Request timeout in seconds.
            delay: Minimum delay between requests in seconds to respect rate limits.
        """
        self.proxy = proxy
        self.timeout = timeout
        self.delay = delay
        self.last_request_time: float = 0.0
        self.session_id: str = self._generate_session_id()
        self.aio: AsyncStartpageClient = AsyncStartpageClient(self)

    def _generate_session_id(self) -> str:
        """
        Generates a pseudo-random session ID string.

        This ID is primarily for cosmetic or light tracking purposes if Startpage
        uses such a parameter, though its direct impact isn't guaranteed.

        Returns:
            A string representing the session ID (e.g., "sp_1678886400_1234").
        """
        return f"sp_{int(time.time())}_{random.randint(1000, 9999)}"

    def _get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        Constructs request headers, optionally adding a Referer.

        Args:
            referer: The Referer URL to include in the headers.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = DEFAULT_HEADERS.copy()
        if referer:
            headers["Referer"] = referer
        return headers

    def _respect_delay(self) -> None:
        """
        Ensures a minimum delay between requests to avoid rate limiting.

        Pauses execution if the time since the last request is less than
        the configured `self.delay`.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Makes an HTTP request to the specified URL.

        Handles GET or POST requests, proxy configuration, GZIP decompression,
        and error handling.

        Args:
            url: The URL to request.
            data: Optional dictionary of data to send (for POST requests).
                  If None, a GET request is made.
            headers: Optional dictionary of HTTP headers to use. If None,
                     default headers are generated.

        Returns:
            The decoded response content as a string.

        Raises:
            StartpageRateLimitError: If a 429 HTTP error (rate limit) occurs.
            StartpageHTTPError: For other HTTP errors.
            StartpageError: For network errors or other request failures.
        """
        self._respect_delay()

        if headers is None:
            headers = self._get_headers()

        req: urllib.request.Request
        try:
            if data:
                # POST request
                data_encoded = urllib.parse.urlencode(data).encode("utf-8")
                req = urllib.request.Request(url, data=data_encoded, headers=headers)
            else:
                # GET request
                req = urllib.request.Request(url, headers=headers)

            opener: urllib.request.OpenerDirector
            if self.proxy:
                proxy_handler = urllib.request.ProxyHandler(
                    {"http": self.proxy, "https": self.proxy}
                )
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=self.timeout)
            else:
                response = urllib.request.urlopen(req, timeout=self.timeout)

            content: bytes = response.read()

            if response.headers.get("content-encoding") == "gzip":
                content = gzip.decompress(content)

            return content.decode("utf-8", errors="ignore")

        except urllib.error.HTTPError as e:
            if e.code == 429: # Too Many Requests
                raise StartpageRateLimitError(
                    f"Rate limit exceeded: {e.code} {e.reason}"
                )
            raise StartpageHTTPError(e.code, f"HTTP error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise StartpageError(f"Network error: {e.reason}")
        except Exception as e: # Catch any other unexpected errors
            raise StartpageError(f"Request failed due to an unexpected error: {str(e)}")

    def _build_search_params(
        self,
        query: str,
        category: str,
        language: str,
        region: str,
        page: int,
        results_per_page: int, # Note: Startpage might override this for some categories
        safe_search: Optional[str] = None,
        time_filter: Optional[str] = None,
        size: Optional[str] = None,
        duration: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Constructs the dictionary of parameters for a search request.

        Helper method to consolidate parameter building logic.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        params: Dict[str, Any] = {
            "query": query.strip(),
            "cat": category,
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language), # Language UI
            "pl": REGION_CODES.get(region, region),
            # Startpage uses 'startat' for pagination, 0-indexed
            "startat": str((page - 1) * results_per_page),
        }

        # Safe search (ff parameter) - not used by news or places directly
        if safe_search and category not in ["news", "places"]:
            params["ff"] = SAFE_SEARCH_LEVELS.get(safe_search, "0") # Default to moderate

        # Results per page ('num') - primarily for web search
        if category == "web":
            params["num"] = str(results_per_page)

        # Category-specific parameters
        if time_filter and time_filter != "any" and category in ["web", "video", "news"]:
            params["with_date"] = TIME_FILTERS.get(time_filter, time_filter)

        if size and size != "any" and category == "images":
            params["size"] = IMAGE_SIZES.get(size, size)

        if duration and duration != "any" and category == "video":
            params["duration"] = VIDEO_DURATIONS.get(duration, duration)

        if latitude is not None and longitude is not None and category == "places":
            params["latitude"] = str(latitude)
            params["longitude"] = str(longitude)

        if radius is not None and category == "places":
            params["radius"] = str(radius) # In meters

        params.update(kwargs) # Include any additional keyword arguments
        return params

    def _perform_search_request(
        self,
        query: str,
        category: str, # Internal category name for Startpage
        category_for_parser: str, # Category name for the parser
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        page: int = 1,
        results_per_page: int = 10,
        time_filter: Optional[str] = None,
        size: Optional[str] = None,
        duration: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs a generic search request and parses the results.

        This is a core internal method used by specific search type methods.

        Args:
            query: The search query.
            category: The Startpage internal category for the search (e.g., "web", "pics").
            category_for_parser: The category name expected by the parser.
            language: Language code (e.g., "en", "de").
            region: Region code (e.g., "us", "all").
            safe_search: Safe search level.
            page: Page number of results.
            results_per_page: Number of results per page (actual number may vary).
            time_filter: Time filter for results.
            size: Image size filter.
            duration: Video duration filter.
            latitude: Latitude for places search.
            longitude: Longitude for places search.
            radius: Radius for places search (in meters).
            **kwargs: Additional parameters to pass to the API.

        Returns:
            A dictionary containing the parsed search results.

        Raises:
            ValueError: If the query is empty or whitespace.
            StartpageError: For network or parsing issues.
        """
        params = self._build_search_params(
            query=query,
            category=category,
            language=language,
            region=region,
            page=page,
            results_per_page=results_per_page,
            safe_search=safe_search,
            time_filter=time_filter,
            size=size,
            duration=duration,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            **kwargs,
        )

        html_content = self._make_request(SEARCH_URL, data=params)
        return StartpageParser.parse_search_results(html_content, category_for_parser)

    def search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        time_filter: str = "any", # e.g., "day", "week", "month"
        page: int = 1,
        results_per_page: int = 10,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs a web search.

        Args:
            query: The search query.
            language: Language code for the search.
            region: Region code for the search.
            safe_search: Safe search level ("off", "moderate", "strict").
            time_filter: Time filter for results ("any", "day", "week", "month").
            page: Page number of results to retrieve.
            results_per_page: Desired number of results per page (typically 10).
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing web search results.
        """
        return self._perform_search_request(
            query=query,
            category="web", # Startpage internal category for web
            category_for_parser="web",
            language=language,
            region=region,
            safe_search=safe_search,
            page=page,
            results_per_page=results_per_page,
            time_filter=time_filter,
            **kwargs,
        )

    def images_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        size: str = "any", # e.g., "small", "medium", "large", "wallpaper"
        page: int = 1,
        # results_per_page for images is often fixed by Startpage, e.g., to 20 or more.
        # The parameter is kept for consistency but might not be fully respected.
        results_per_page: int = 20, # Typical default for image searches
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs an image search.

        Args:
            query: The search query for images.
            language: Language code for the search.
            region: Region code for the search.
            safe_search: Safe search level.
            size: Filter by image size ("any", "small", "medium", "large", "wallpaper").
            page: Page number of results.
            results_per_page: Desired number of results (actual count may vary).
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing image search results.
        """
        return self._perform_search_request(
            query=query,
            category="pics", # Startpage internal category for images
            category_for_parser="images",
            language=language,
            region=region,
            safe_search=safe_search,
            page=page,
            results_per_page=results_per_page, # Actual number may be fixed by Startpage
            size=size,
            **kwargs,
        )

    def videos_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        duration: str = "any", # e.g., "short", "medium", "long"
        time_filter: str = "any", # e.g., "day", "week", "month"
        page: int = 1,
        results_per_page: int = 10, # Typical default for video searches
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs a video search.

        Args:
            query: The search query for videos.
            language: Language code.
            region: Region code.
            safe_search: Safe search level.
            duration: Filter by video duration ("any", "short", "medium", "long").
            time_filter: Time filter for results.
            page: Page number of results.
            results_per_page: Desired number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing video search results.
        """
        return self._perform_search_request(
            query=query,
            category="video", # Startpage internal category for videos
            category_for_parser="videos",
            language=language,
            region=region,
            safe_search=safe_search,
            page=page,
            results_per_page=results_per_page,
            duration=duration,
            time_filter=time_filter,
            **kwargs,
        )

    def news_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        time_filter: str = "any", # e.g., "day", "week", "month", "year"
        page: int = 1,
        results_per_page: int = 10, # Typical default for news searches
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs a news search.

        Note: Safe search is not directly applicable to news search in Startpage
              in the same way as web search.

        Args:
            query: The search query for news.
            language: Language code.
            region: Region code.
            time_filter: Time filter for news results.
            page: Page number of results.
            results_per_page: Desired number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing news search results.
        """
        return self._perform_search_request(
            query=query,
            category="news", # Startpage internal category for news
            category_for_parser="news",
            language=language,
            region=region,
            safe_search=None, # Safe search 'ff' param not typically used for news
            page=page,
            results_per_page=results_per_page,
            time_filter=time_filter,
            **kwargs,
        )

    def places_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all", # Can be a specific city/country or "all"
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None, # Search radius in meters
        page: int = 1,
        results_per_page: int = 10, # Typical default for places searches
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Performs a places (maps/local) search.

        Args:
            query: The search query for places (e.g., "restaurants near me", "Eiffel Tower").
            language: Language code.
            region: General region for the search.
            latitude: Optional latitude for location-specific search.
            longitude: Optional longitude for location-specific search.
            radius: Optional search radius in meters if lat/lon are provided.
            page: Page number of results.
            results_per_page: Desired number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing places search results.
        """
        return self._perform_search_request(
            query=query,
            category="map", # Startpage internal category for places/maps
            category_for_parser="places",
            language=language,
            region=region,
            safe_search=None, # Safe search 'ff' param not typically used for places
            page=page,
            results_per_page=results_per_page,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            **kwargs,
        )

    def suggestions(self, query_part: str, language: str = "en") -> List[str]:
        """
        Fetches search suggestions for a partial query.

        Args:
            query_part: The partial query string to get suggestions for.
            language: Language code for suggestions.

        Returns:
            A list of suggestion strings. Returns an empty list if query_part is empty.

        Raises:
            StartpageError: For network or parsing issues.
        """
        if not query_part.strip():
            return []

        params = {
            "q": query_part.strip(),
            "segment": "startpage.ucp", # Standard segment for Startpage suggestions
            "format": "opensearch",    # Standard format for suggestions
            "lang": LANGUAGE_CODES.get(language, language),
        }

        # Suggestions URL usually takes parameters in the query string itself
        query_string = urllib.parse.urlencode(params)
        full_url = f"{SUGGESTIONS_URL}?{query_string}"

        response_text = self._make_request(full_url) # GET request
        return StartpageParser.parse_suggestions(response_text)

    def _extract_instant_answer_from_sxpr(
        self, soup: BeautifulSoup, query: str
    ) -> Optional[str]:
        """Helper to find instant answers from Startpage's knowledge system (sxpr)."""
        sxpr_elements = soup.find_all(
            ["div", "section"],
            attrs={"class": re.compile(r".*(sxpr|search-expander|sx-|wiki).*", re.I)},
        )
        for element in sxpr_elements:
            text_content = StartpageParser._extract_text(element).strip()
            if text_content and 20 < len(text_content) < 300:
                 # Prioritize if query implies a direct question
                question_indicators = [
                    "what is", "what are", "who is", "who are",
                    "how much", "how many", "when is", "where is",
                    "define", "definition", "time in"
                ]
                if any(indicator in query.lower() for indicator in question_indicators):
                    return text_content
        return None

    def _extract_knowledge_panel_from_sxpr(
        self, soup: BeautifulSoup
    ) -> Optional[Dict[str, Any]]:
        """Helper to find knowledge panels from Startpage's sxpr elements."""
        sxpr_elements = soup.find_all(
            ["div", "section"],
            attrs={"class": re.compile(r".*(sxpr|search-expander|sx-|wiki).*", re.I)},
        )
        for element in sxpr_elements:
            text_content = StartpageParser._extract_text(element).strip()
            if len(text_content) > 20: # Needs some substance
                panel = {
                    "title": "",
                    "description": text_content[:800] + ("..." if len(text_content) > 800 else ""),
                    "facts": {},
                    "source": "Startpage Knowledge",
                }
                title_elem = element.find(["h1", "h2", "h3", "h4"])
                if title_elem:
                    panel["title"] = StartpageParser._extract_text(title_elem).strip()
                # If it's a long text and no specific instant answer pattern matched,
                # treat it as a knowledge panel description.
                if len(text_content) >= 300 or panel["title"]:
                    return panel
        return None

    def _extract_calculator_answer(self, html_content: str) -> Optional[str]:
        """Helper to find calculator or unit conversion results."""
        # More specific patterns to avoid false positives
        calc_patterns = [
            r'<span class="wob_t" style="display:inline">([-−]?[\d,.]+)</span>', # Weather temp
            r'id="cwos">([-−]?[\d,.]+)</span>', # Currency / Unit converter output
            r'<div class="vk_ans">([-−]?[\d,.]+)</div>', # General answer box
            r'calc_result_val">([-−]?[\d,.\s]+)</span>', # Calculator result specific class
             # Simpler pattern for results like "= 1,234.56"
            r'(?:=\s*|is\s*|equals\s*)([-−]?[\d,.\s]+[A-Za-z%]*)',
        ]
        for pattern in calc_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_time_date_answer(self, html_content: str, query: str) -> Optional[str]:
        """Helper to find time or date related answers."""
        if not any(kw in query.lower() for kw in ["time", "date", "today", "now"]):
            return None

        # Patterns are broad, context of query is important
        time_patterns = [
            r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\b',  # 10:30 AM
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b, \w+ \d{1,2}, \d{4}', # Mon, Jan 1, 2024
            r'\b\w+ \d{1,2}, \d{4}\b', # January 1, 2024
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b' # 01/01/2024
        ]
        for pattern in time_patterns:
            match = re.search(pattern, html_content, re.I)
            if match:
                # Check if the match is within a prominent element
                # This is hard without full DOM, so we rely on pattern specificity
                return match.group(0).strip()
        return None

    def _extract_weather_answer(self, soup: BeautifulSoup, query: str) -> Optional[str]:
        """Helper to find weather-related answers."""
        if "weather" not in query.lower():
            return None

        # Look for common weather text patterns within relevant-looking class names
        weather_elements = soup.find_all(
            ["span", "div"],
            attrs={"class": re.compile(r".*(temp|weather|climate|condition|forecast).*", re.I)},
        )
        for elem in weather_elements:
            text = StartpageParser._extract_text(elem).strip()
            # Matches like "72°F", "10°C", "Sunny", "Cloudy with a chance of rain"
            if re.search(r'\d+°[CF]?|\b(Sunny|Cloudy|Rain|Snow)\b', text, re.I):
                # Try to get a concise snippet
                return text.split('\n')[0].strip()[:100] # First line, up to 100 chars
        return None

    def _extract_generic_knowledge_panel(
        self, soup: BeautifulSoup
    ) -> Optional[Dict[str, Any]]:
        """Helper for more generic knowledge panel detection (e.g., Wikipedia summaries)."""
        # Target containers that often hold summary info
        potential_panels = soup.find_all(
            ["div", "section", "aside"],
            attrs={
                "class": re.compile(
                    r".*(infobox|summary|description|knowledge|fact|panel|entity).*", re.I
                )
            },
        )

        for container in potential_panels:
            full_text = StartpageParser._extract_text(container)
            if not (200 < len(full_text) < 5000): # Reasonable length for a panel
                continue

            title_elem = container.find(["h1", "h2", "h3", "h4", "div"],
                                        attrs={"role": "heading"}) or \
                         container.find(["h1", "h2", "h3", "h4"])

            # Try to get a paragraph that's likely a description
            desc_elem = None
            paragraphs = container.find_all("p")
            if paragraphs:
                # Prefer paragraphs that are not too short and appear early
                for p_tag in paragraphs:
                    p_text = StartpageParser._extract_text(p_tag)
                    if len(p_text) > 50:
                        desc_elem = p_tag
                        break
                if not desc_elem and paragraphs: # Fallback to first paragraph
                     desc_elem = paragraphs[0]

            if not (title_elem or desc_elem):
                continue # Skip if no title or description found

            panel = {
                "title": StartpageParser._extract_text(title_elem).strip() if title_elem else "",
                "description": "",
                "facts": {}, # TODO: Add fact extraction if common patterns exist
                "source": "Knowledge Panel",
            }

            if desc_elem:
                panel["description"] = StartpageParser._extract_text(desc_elem).strip()[:800]
            elif title_elem and not desc_elem: # Use part of full_text if no <p>
                panel["description"] = full_text.replace(panel["title"], "").strip()[:800]

            # Basic check for relevance
            if panel["title"] or len(panel["description"]) > 100:
                 # Extract structured facts (e.g., from definition lists or tables)
                fact_elements = container.find_all(['dt', 'th'])
                for fact_elem in fact_elements:
                    fact_name = StartpageParser._extract_text(fact_elem).strip().rstrip(':')
                    fact_value_elem = fact_elem.find_next_sibling(['dd', 'td'])
                    if fact_value_elem:
                        fact_value = StartpageParser._extract_text(fact_value_elem).strip()
                        if fact_name and fact_value and len(fact_name) < 50 and len(fact_value) < 200:
                            panel["facts"][fact_name] = fact_value
                return panel
        return None

    def instant_answers(
        self, query: str, language: str = "en", **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Fetches instant answers and knowledge panel information for a query.

        This method performs a web search and then attempts to parse the
        resulting HTML for common patterns of instant answers (like definitions,
        calculations, weather) and knowledge panels (like Wikipedia summaries).

        The reliability of this feature depends heavily on Startpage's HTML
        structure, which can change.

        Args:
            query: The search query.
            language: Language code for the search.
            **kwargs: Additional parameters for the web search.

        Returns:
            A dictionary with keys "instant_answer" (Optional[str]) and
            "knowledge_panel" (Optional[Dict[str, Any]]).
            The knowledge_panel dict may contain "title", "description", "facts", "source".

        Raises:
            ValueError: If the query is empty.
            StartpageError: For network or underlying search issues.
        """
        if not query.strip():
            # Return empty structure instead of raising ValueError to align with suggestion behavior
            return {"instant_answer": None, "knowledge_panel": None}

        # Base search parameters for fetching a page likely to contain answers
        search_params: Dict[str, Any] = {
            "query": query.strip(),
            "cat": "web", # Instant answers are usually on web results
            "cmd": "process_search",
            "language": LANGUAGE_CODES.get(language, language),
            "lui": LANGUAGE_CODES.get(language, language), # UI language
        }
        search_params.update(kwargs) # Allow overrides and additional params

        html_content = self._make_request(SEARCH_URL, data=search_params)
        soup = BeautifulSoup(html_content, "lxml") # 'lxml' is generally fast

        instant_answer: Optional[str] = None
        knowledge_panel: Optional[Dict[str, Any]] = None

        # Attempt extraction in a specific order of likelihood / specificity
        if not instant_answer:
            instant_answer = self._extract_instant_answer_from_sxpr(soup, query)
        
        if not instant_answer:
            instant_answer = self._extract_calculator_answer(html_content)

        if not instant_answer:
            instant_answer = self._extract_time_date_answer(html_content, query)

        if not instant_answer:
            instant_answer = self._extract_weather_answer(soup, query)
        
        # Knowledge panel extraction attempts
        if not knowledge_panel:
             # Try sxpr first as it's more Startpage specific
            knowledge_panel = self._extract_knowledge_panel_from_sxpr(soup)

        if not knowledge_panel:
            knowledge_panel = self._extract_generic_knowledge_panel(soup)
            
        # If an instant answer is very similar to knowledge panel description, clear one.
        if instant_answer and knowledge_panel and knowledge_panel.get("description"):
            if instant_answer in knowledge_panel["description"] or \
               knowledge_panel["description"] in instant_answer :
                # Prefer knowledge panel if it has a title, otherwise instant answer
                if knowledge_panel.get("title"):
                    instant_answer = None
                else:
                    knowledge_panel = None
                    
        return {"instant_answer": instant_answer, "knowledge_panel": knowledge_panel}

    def get_search_url(
        self, query: str, search_type: str = "web", **params: Any
    ) -> str:
        """
        Constructs the full search URL for a given query and parameters.

        Useful for debugging or if you need to make the request manually.

        Args:
            query: The search query.
            search_type: The type of search (e.g., "web", "images", "videos").
                         Refers to keys in `SEARCH_CATEGORIES`.
            **params: Additional URL parameters to include.

        Returns:
            The fully formed Startpage search URL string.
        """
        base_query_params: Dict[str, Any] = {
            "query": query,
            # Use internal category name from endpoints.py, default to 'web'
            "cat": SEARCH_CATEGORIES.get(search_type, "web"),
            "cmd": "process_search", # Standard command for search
        }
        # Allow user to override default params or add new ones
        base_query_params.update(params)
        return f"{SEARCH_URL}?{urllib.parse.urlencode(base_query_params)}"

    def advanced_search(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Performs an "advanced" web search using specific filter parameters.

        This method maps common advanced search concepts to Startpage's
        URL parameters if direct equivalents exist in `ADVANCED_SEARCH_PARAMS`.
        It defaults to a web search.

        Args:
            query: The primary search query.
            **kwargs: Advanced search parameters. Keys should match those defined
                      in `startpageapi.endpoints.ADVANCED_SEARCH_PARAMS` keys
                      (e.g., "exact_phrase", "site_restrict").
                      Unknown parameters will be ignored by this mapping but can
                      still be passed if they are valid Startpage parameters.

        Returns:
            A dictionary containing search results, parsed as web results.

        Raises:
            ValueError: If the query is empty.
            StartpageError: For network or parsing issues.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty for advanced search.")

        # Base parameters for a web search
        params: Dict[str, Any] = {
            "query": query.strip(),
            "cat": "web", # Advanced search is typically a refinement of web search
            "cmd": "process_search",
        }

        # Map provided kwargs to Startpage's specific advanced parameter names
        for key, value in kwargs.items():
            if key in ADVANCED_SEARCH_PARAMS:
                # ADVANCED_SEARCH_PARAMS maps readable key to actual Startpage param name
                startpage_param_key = ADVANCED_SEARCH_PARAMS[key]
                params[startpage_param_key] = value
            elif key in params: # Allow overriding base params like 'language'
                params[key] = value
            # else: Silently ignore unknown keys for this specific mapping
            # but they might be passed if _perform_search_request is used directly

        # Use _perform_search_request to leverage existing logic
        # It will handle the actual request and parsing
        # We pass 'web' as category_for_parser as advanced search yields web results
        return self._perform_search_request(
            query=params.pop("query"), # query is special, already handled
            category=params.pop("cat"),
            category_for_parser="web",
            **params, # Pass all other constructed params
        )
