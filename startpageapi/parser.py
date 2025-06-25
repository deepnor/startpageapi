"""
Provides parsing utilities for processing HTML responses from Startpage.

This module defines the `StartpageParser` class, which contains static methods
to extract structured data from Startpage's search result pages. It handles
different types of search results (web, images, videos, news, places) and
search suggestions. The parser is designed to be resilient to minor changes
in HTML structure by using various fallback mechanisms and pattern matching.

Core functionalities include:
- Parsing main search results for titles, URLs, descriptions.
- Extracting image URLs, source URLs, and titles for image searches.
- Parsing video results for titles, URLs, descriptions, and durations.
- Extracting news articles with titles, URLs, sources, and publication dates.
- Parsing place information including name, address, phone, rating, and URL.
- Extracting search suggestions.
- Helper methods for text extraction and cleaning.
"""

import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, element # Import element for type hinting

from .exceptions import StartpageParseError


# Base URL for resolving relative links.
_STARTPAGE_BASE_URL = "https://www.startpage.com"


class StartpageParser:
    """
    A collection of static methods for parsing Startpage HTML content.

    This parser aims to extract meaningful data from the raw HTML of
    Startpage search results. It uses BeautifulSoup for HTML traversal
    and regular expressions for pattern matching. Each parsing method
    is tailored to a specific type of search result and includes
    fallbacks to handle variations in Startpage's page structure.
    """

    @staticmethod
    def _safe_json_loads(json_string: Optional[str]) -> Optional[Any]:
        """
        Safely attempts to parse a JSON string.

        Args:
            json_string: The string to parse as JSON. Can be None.

        Returns:
            The parsed JSON data, or None if parsing fails or input is None.
        """
        if json_string is None:
            return None
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _normalize_url(url: Optional[str], base_url: str = _STARTPAGE_BASE_URL) -> str:
        """
        Normalizes a URL, making it absolute if it's relative.

        Args:
            url: The URL string to normalize.
            base_url: The base URL to use for resolving relative paths.

        Returns:
            An absolute URL string. Returns an empty string if the input URL is None or empty.
        """
        if not url:
            return ""
        url = url.strip()
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            # Ensure no double slashes if base_url ends with / and url starts with /
            if base_url.endswith("/") and url.startswith("/"):
                return base_url + url[1:]
            return base_url + url
        return url

    @staticmethod
    def _extract_text(
        bs_element: Optional[element.Tag | element.NavigableString],
    ) -> str:
        """
        Extracts and cleans text content from a BeautifulSoup element.

        Uses `get_text(separator=" ", strip=True)` for better spacing and
        then performs additional cleaning.

        Args:
            bs_element: The BeautifulSoup element (Tag or NavigableString).

        Returns:
            Cleaned text content, or an empty string if element is None.
        """
        if bs_element is None:
            return ""

        text = bs_element.get_text(separator=" ", strip=True)

        # Further cleanup for excessive internal whitespace that get_text might leave
        # Also, replace non-breaking spaces with regular spaces.
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _find_next_page_link(soup: BeautifulSoup) -> bool:
        """
        Checks for a "next page" link or button in the HTML.

        Args:
            soup: A BeautifulSoup object representing the parsed HTML page.

        Returns:
            True if a next page link/button is found, False otherwise.
        """
        next_page_patterns = [
            re.compile(r"next", re.I),
            re.compile(r"more\s*results", re.I),
            re.compile(r">>", re.I),
            re.compile(r"load\s*more", re.I),
        ]

        # Check 'a' and 'button' tags using various attributes
        for tag_name in ["a", "button"]:
            for pattern in next_page_patterns:
                # Check text content
                if soup.find(tag_name, string=pattern): return True
                # Check title attribute
                if soup.find(tag_name, title=pattern): return True
                # Check aria-label attribute
                if soup.find(tag_name, attrs={"aria-label": pattern}): return True
                # Check specific class names (less reliable but a fallback)
                if soup.find(tag_name, class_=re.compile(r"next|pagination-next", re.I)): return True

        # Check for common pagination structures (e.g., <nav role="navigation">)
        pagination_nav = soup.find(
            ["nav", "div"],
            attrs={"role": "navigation", "aria-label": re.compile("pagination", re.I)}
        )
        if pagination_nav:
            links = pagination_nav.find_all(["a", "button"])
            if links:
                last_link_text = StartpageParser._extract_text(links[-1]).lower()
                # Check if the last interactive element implies "next"
                if "next" in last_link_text or \
                   re.search(r">\s*$", last_link_text) or \
                   re.search(r"\u2192", last_link_text): # Right arrow
                    # Ensure it's not disabled
                    if not links[-1].has_attr("disabled") and \
                       "disabled" not in links[-1].get("class", []):
                        return True
        return False

    @staticmethod
    def _extract_total_results(soup: BeautifulSoup) -> int:
        """
        Extracts the total number of results from the page.

        Searches for common patterns indicating total results count.

        Args:
            soup: A BeautifulSoup object of the search results page.

        Returns:
            The estimated total number of results, or 0 if not found.
        """
        text_content_sources = []

        # Prioritize specific elements known to hold result counts
        specific_elements = soup.find_all(
            ["div", "span", "p"],
            id=re.compile(r"results?_?count|num_results|search_stats|result-stats", re.I)
        )
        if specific_elements:
            for el in specific_elements:
                text_content_sources.append(StartpageParser._extract_text(el))

        # Fallback: check common stats containers
        stats_containers = soup.find_all(
            ["div", "p"],
            class_=re.compile(r"results?-?info|stats-text|summary", re.I)
        )
        for el in stats_containers:
            text_content_sources.append(StartpageParser._extract_text(el))

        # Broadest fallback: get all text from a main content area or whole page
        if not text_content_sources:
            main_content_area = soup.find("main") or soup.find("div", id="main_results") or soup
            text_content_sources.append(main_content_area.get_text(separator=" ", strip=True))

        # Regex patterns to find numbers followed by "results", "found", etc.
        patterns = [
            r"([0-9,]+)\s*(?:results|Ergebnisse|résultats|risultati|resultados|resultaten)",
            r"About\s*([0-9,]+)",
            r"Approximately\s*([0-9,]+)",
            r"Displaying\s*[\d,-]+\s*of\s*([0-9,]+)",
            r"([0-9,]+)\s*items found",
        ]
        for text_content in text_content_sources:
            for pattern in patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    try:
                        return int(match.group(1).replace(",", ""))
                    except (ValueError, IndexError):
                        continue
        return 0

    @staticmethod
    def parse_search_results(html: str, search_type: str = "web") -> Dict[str, Any]:
        """
        Main dispatcher for parsing search results based on search type.

        Args:
            html: The HTML content of the search results page.
            search_type: The type of search (e.g., "web", "images").

        Returns:
            A dictionary containing the parsed results, total results count,
            and a flag for whether a next page exists.

        Raises:
            StartpageParseError: If the search type is unknown or a general
                                 parsing failure occurs.
        """
        if not html:
            raise StartpageParseError("Cannot parse empty HTML content.")

        try:
            parser_method_map = {
                "web": StartpageParser._parse_web_results,
                "images": StartpageParser._parse_image_results,
                "videos": StartpageParser._parse_video_results,
                "news": StartpageParser._parse_news_results,
                "places": StartpageParser._parse_places_results,
            }
            if search_type in parser_method_map:
                return parser_method_map[search_type](html)
            else:
                raise StartpageParseError(f"Unknown search type for parsing: {search_type}")
        except Exception as e:
            # Catch any unexpected error during parsing dispatch or execution
            # and wrap it in a StartpageParseError for consistent error handling.
            # Avoid leaking raw HTML in error, just the type of error.
            error_type = type(e).__name__
            raise StartpageParseError(
                f"Failed to parse '{search_type}' results due to {error_type}: {str(e)}"
            )

    @staticmethod
    def _parse_web_results(html: str) -> Dict[str, Any]:
        """
        Parses web search results from HTML.

        Attempts to find result containers using various known class names and
        attributes. For each container, it extracts the title, URL, description,
        and display URL.

        Args:
            html: HTML content of the web search results page.

        Returns:
            A dictionary with "results", "total_results", and "has_next_page".
        """
        results: List[Dict[str, str]] = []
        soup = BeautifulSoup(html, "lxml")

        result_container_selectors = [
            "div.w-gl-result",
            "div.result",
            "article.result-item",
            "div[data-testid='result-item']",
            "div[class*='search-result-item']",
            "section.web-result", # Another common pattern
        ]
        
        result_elements: List[element.Tag] = []
        for selector in result_container_selectors:
            found_elements = soup.select(selector)
            if found_elements:
                result_elements = found_elements
                break
        
        if not result_elements:
            potential_containers = soup.find_all("div")
            for div_container in potential_containers:
                if div_container.select_one("h2 > a[href], h3 > a[href], h4 > a[href]") and \
                   div_container.select_one("p, span[class*='snippet'], span[class*='desc']"):
                    result_elements.append(div_container)

        for container in result_elements:
            try:
                title_tag = container.select_one("h2 > a, h3 > a, h4 > a, a > h2, a > h3, a > h4")
                if not title_tag:
                    title_tag = container.select_one("a[href][role='heading'], a[href][data-testid='result-title-a']")
                if not title_tag: # Broader link search if specific title structure fails
                    all_links = container.find_all("a", href=True)
                    title_tag = next((lk for lk in all_links if StartpageParser._extract_text(lk).strip()), None)

                if not title_tag:
                    continue

                title = StartpageParser._extract_text(title_tag)
                url = StartpageParser._normalize_url(title_tag.get("href"))

                if not title or not url:
                    continue

                desc_tag = container.select_one(
                    "p[class*='snippet'], p[class*='desc'], div[class*='snippet'], div[class*='desc'], .result-snippet"
                )
                if not desc_tag:
                    # Try to find a paragraph that isn't part of an ad or other meta-info
                    paragraphs = container.find_all("p")
                    desc_tag = next((p for p in paragraphs if not p.find_parent(class_=re.compile("ads|related", re.I))), None)
                description = StartpageParser._extract_text(desc_tag) if desc_tag else ""

                display_url_tag = container.select_one("cite, span[class*='url'], div[class*='breadcrumb'], .result__url")
                display_url = StartpageParser._extract_text(display_url_tag).split(" ")[0] if display_url_tag else ""
                if not display_url and url: # Fallback from main URL host
                    try:
                        display_url = re.match(r"https?://([^/]+)", url).group(1) # type: ignore
                    except AttributeError:
                        pass # keep display_url empty

                results.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "display_url": display_url,
                })
            except Exception:
                continue
        
        return {
            "results": results,
            "total_results": StartpageParser._extract_total_results(soup),
            "has_next_page": StartpageParser._find_next_page_link(soup),
        }

    @staticmethod
    def _parse_image_results(html: str) -> Dict[str, Any]:
        """
        Parses image search results from HTML.

        Prioritizes extracting data from JSON embedded in script tags if available.
        Falls back to parsing individual image elements (<img> tags) and their
        surrounding context for source URL, image URL, and title.

        Args:
            html: HTML content of the image search results page.

        Returns:
            A dictionary with "results", "total_results", and "has_next_page".
        """
        results: List[Dict[str, str]] = []
        soup = BeautifulSoup(html, "lxml")
        seen_image_urls = set()

        scripts = soup.find_all("script")
        for script in scripts:
            script_content = script.string
            if not script_content:
                continue
            try:
                # More targeted regex for script data if a pattern is known
                # Example: looking for something like "window.__IMAGE_DATA__ = [...]"
                # For now, using a generic JSON object search if it contains image-like keys
                potential_json_objects = re.findall(r"({[^{}]*?\"(image.?url|thumbnail.?url|content.?url)\":.*?})", script_content, re.I)
                for obj_match in potential_json_objects:
                    data = StartpageParser._safe_json_loads(obj_match[0]) # obj_match[0] is the full matched object string
                    if data and isinstance(data, dict):
                        img_url = StartpageParser._normalize_url(
                            data.get("thumbnailUrl") or data.get("contentUrl") or data.get("url") or data.get("imageUrl")
                        )
                        src_url = StartpageParser._normalize_url(
                            data.get("hostPageUrl") or data.get("source") or data.get("page")
                        )
                        title = data.get("name") or data.get("title") or data.get("alt") or "Image"
                        if img_url and img_url not in seen_image_urls:
                            results.append({
                                "image_url": img_url,
                                "source_url": src_url,
                                "title": str(title),
                            })
                            seen_image_urls.add(img_url)
            except Exception:
                continue

        if not results:
            image_item_selectors = [
                "div.image-result-item", "div.tile", "figure.image-container", "div.img-result"
            ]
            image_elements: List[element.Tag] = []
            for selector in image_item_selectors:
                found = soup.select(selector)
                if found:
                    image_elements.extend(found)

            if not image_elements:
                main_content = soup.find("main") or soup.find("div", id="main_results") or soup
                image_elements = main_content.find_all("div", class_=re.compile(r"image|img|pic", re.I))


            for item_container in image_elements:
                try:
                    img_tag = item_container.find("img")
                    if not img_tag:
                        continue

                    img_url = StartpageParser._normalize_url(
                        img_tag.get("data-src") or img_tag.get("src")
                    )
                    if not img_url or img_url in seen_image_urls:
                        continue

                    title = img_tag.get("alt") or img_tag.get("title")
                    if not title:
                        caption_tag = item_container.find("figcaption") or \
                                      item_container.find(["p", "span"], class_=re.compile("title|caption", re.I))
                        if caption_tag: title = StartpageParser._extract_text(caption_tag)
                    title = title or "Image"

                    link_tag = img_tag.find_parent("a", href=True) or item_container.find("a", href=True)
                    source_url = StartpageParser._normalize_url(link_tag.get("href")) if link_tag else ""

                    results.append({
                        "image_url": img_url,
                        "source_url": source_url,
                        "title": title.strip(),
                    })
                    seen_image_urls.add(img_url)
                except Exception:
                    continue
        
        return {
            "results": results,
            "total_results": StartpageParser._extract_total_results(soup),
            "has_next_page": StartpageParser._find_next_page_link(soup),
        }

    @staticmethod
    def _parse_video_results(html: str) -> Dict[str, Any]:
        """
        Parses video search results from HTML.

        Looks for containers holding video information and extracts title, URL,
        description, and duration.

        Args:
            html: HTML content of the video search results page.

        Returns:
            A dictionary with "results", "total_results", and "has_next_page".
        """
        results: List[Dict[str, str]] = []
        soup = BeautifulSoup(html, "lxml")

        video_container_selectors = [
            "div.video-result-item", "article.video-object",
            "div[class*='vid-item']", "div.search-result-video"
        ]
        video_elements: List[element.Tag] = []
        for selector in video_container_selectors:
            found = soup.select(selector)
            if found:
                video_elements = found
                break
        
        if not video_elements:
            video_elements = soup.find_all("div", class_=re.compile(r"result.*video", re.I))

        for container in video_elements:
            try:
                title_tag = container.select_one("h3 a, h4 a, .video-title a, .title a")
                if not title_tag:
                    continue

                title = StartpageParser._extract_text(title_tag)
                url = StartpageParser._normalize_url(title_tag.get("href"))

                if not title or not url:
                    continue

                desc_tag = container.select_one(".video-description, .snippet, .desc, .description")
                description = StartpageParser._extract_text(desc_tag) if desc_tag else ""

                duration_tag = container.select_one(".video-duration, .time, .duration, span[class*='duration']")
                duration = StartpageParser._extract_text(duration_tag) if duration_tag else ""
                duration_match = re.search(r"(\d{1,2}:\d{2}(?::\d{2})?)", duration) # Format like HH:MM:SS or MM:SS
                duration = duration_match.group(1) if duration_match else duration

                results.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "duration": duration,
                })
            except Exception:
                continue
        
        return {
            "results": results,
            "total_results": StartpageParser._extract_total_results(soup),
            "has_next_page": StartpageParser._find_next_page_link(soup),
        }

    @staticmethod
    def _parse_news_results(html: str) -> Dict[str, Any]:
        """
        Parses news search results from HTML.

        Extracts title, URL, description (snippet), source, and publication date
        for each news article.

        Args:
            html: HTML content of the news search results page.

        Returns:
            A dictionary with "results", "total_results", and "has_next_page".
        """
        results: List[Dict[str, str]] = []
        soup = BeautifulSoup(html, "lxml")

        news_container_selectors = [
            "article.news-item", "div.news-result",
            "div[class*='story-card']", "div.search-result-news"
        ]
        news_elements: List[element.Tag] = []
        for selector in news_container_selectors:
            found = soup.select(selector)
            if found:
                news_elements = found
                break
        
        if not news_elements:
             news_elements = soup.find_all("article", class_=re.compile(r"news|story|article", re.I))

        for container in news_elements:
            try:
                title_tag = container.select_one("h3 a, h4 a, .title a, .headline a, a .title")
                if not title_tag:
                    # If title is not in an <a>, try to find <a> at container level
                    title_tag_no_a = container.select_one("h3, h4, .title, .headline")
                    if title_tag_no_a:
                         link_for_title = title_tag_no_a.find_parent("a",href=True) or container.find("a",href=True)
                         if link_for_title:
                             title = StartpageParser._extract_text(title_tag_no_a)
                             url = StartpageParser._normalize_url(link_for_title.get("href"))
                         else: continue # Cannot determine URL
                    else: continue
                else:
                    title = StartpageParser._extract_text(title_tag)
                    url = StartpageParser._normalize_url(title_tag.get("href"))


                if not title or not url:
                    continue

                desc_tag = container.select_one(".snippet, .description, .summary, .article-summary")
                description = StartpageParser._extract_text(desc_tag) if desc_tag else ""

                source_tag = container.select_one(".source, .publisher, .attribution cite, .article-source")
                source = StartpageParser._extract_text(source_tag) if source_tag else ""
                
                date_tag = container.select_one(".date, .timestamp, time, .article-date")
                published_date = ""
                if date_tag:
                    published_date = date_tag.get("datetime") or StartpageParser._extract_text(date_tag)

                results.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "source": source,
                    "published_date": published_date,
                })
            except Exception:
                continue
        
        return {
            "results": results,
            "total_results": StartpageParser._extract_total_results(soup),
            "has_next_page": StartpageParser._find_next_page_link(soup),
        }

    @staticmethod
    def _parse_places_results(html: str) -> Dict[str, Any]:
        """
        Parses places (local/map) search results from HTML.

        Attempts to extract structured data (like `application/ld+json`) first.
        Falls back to parsing HTML elements for place name, address, phone,
        rating, and URL.

        Args:
            html: HTML content of the places search results page.

        Returns:
            A dictionary with "results", "total_results", and "has_next_page".
        """
        results: List[Dict[str, Any]] = []
        soup = BeautifulSoup(html, "lxml")
        seen_places_identifiers = set()

        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = StartpageParser._safe_json_loads(script.string)
                if not data: continue

                items_to_process = []
                if isinstance(data, list): items_to_process.extend(data)
                elif isinstance(data, dict):
                    if data.get("@type") == "ItemList": items_to_process.extend(data.get("itemListElement", []))
                    elif "@graph" in data and isinstance(data["@graph"], list): items_to_process.extend(data["@graph"])
                    else: items_to_process.append(data)

                for item_data in items_to_process:
                    # If item_data is from ItemList, it might be nested under "item"
                    item = item_data.get("item") if "item" in item_data and isinstance(item_data.get("item"),dict) else item_data

                    item_type = item.get("@type", "")
                    if isinstance(item_type, list): item_type = item_type[0] if item_type else ""

                    if item_type in ["Place", "LocalBusiness", "Restaurant", "Store", "Hotel", "PostalAddress"]:
                        name = item.get("name", "")
                        if not name and item_type == "PostalAddress": # For addresses that are items themselves
                            name = "Address"
                        if not name : continue

                        addr_obj = item.get("address")
                        addr_str = ""
                        if isinstance(addr_obj, dict):
                            addr_str = ", ".join(filter(None, [
                                addr_obj.get("streetAddress"), addr_obj.get("postOfficeBoxNumber"),
                                addr_obj.get("addressLocality"), addr_obj.get("addressRegion"),
                                addr_obj.get("postalCode"), addr_obj.get("addressCountry")
                            ]))
                        elif isinstance(addr_obj, str): addr_str = addr_obj

                        identifier = f"{name}|{addr_str}".lower()
                        if identifier in seen_places_identifiers: continue

                        agg_rating = item.get("aggregateRating")
                        rating_val = agg_rating.get("ratingValue") if isinstance(agg_rating, dict) else None
                        review_count = agg_rating.get("reviewCount") if isinstance(agg_rating, dict) else None

                        geo_obj = item.get("geo")
                        lat = geo_obj.get("latitude") if isinstance(geo_obj, dict) else None
                        lon = geo_obj.get("longitude") if isinstance(geo_obj, dict) else None

                        results.append({
                            "name": name, "address": addr_str,
                            "phone": item.get("telephone", ""),
                            "url": StartpageParser._normalize_url(item.get("url") or item.get("mainEntityOfPage")),
                            "rating": str(rating_val) if rating_val is not None else None,
                            "review_count": int(review_count) if review_count is not None else None,
                            "latitude": str(lat) if lat is not None else None,
                            "longitude": str(lon) if lon is not None else None,
                            "data_source": "ld+json",
                        })
                        seen_places_identifiers.add(identifier)
            except Exception:
                continue

        if not results:
            place_container_selectors = [
                "div.place-card", "article.local-result", "div[data-result-type='local']",
                "div[class*='place-result']", "div[class*='location-card']"
            ]
            place_elements: List[element.Tag] = []
            for selector in place_container_selectors:
                found = soup.select(selector)
                if found:
                    place_elements.extend(found)

            if not place_elements:
                place_elements = soup.find_all("div", class_=re.compile(r"result.*(place|local|map|location)", re.I))

            for container in place_elements:
                try:
                    name_tag = container.select_one("h3, h4, .place-name, .title, [role='heading']")
                    name = StartpageParser._extract_text(name_tag) if name_tag else ""
                    if not name: continue

                    addr_tag = container.select_one(".address, .adr, .place-address, [itemprop='address']")
                    address = StartpageParser._extract_text(addr_tag) if addr_tag else ""

                    identifier = f"{name}|{address}".lower()
                    if identifier in seen_places_identifiers: continue

                    phone_tag = container.select_one(".phone, .tel, .place-phone, [itemprop='telephone']")
                    phone = StartpageParser._extract_text(phone_tag) if phone_tag else ""

                    url_tag = container.select_one("a.website-link, a[href*='maps.google.com'], a[itemprop='url'], a.directions-link")
                    if not url_tag and name_tag : url_tag = name_tag.find_parent("a", href=True) or container.find("a",href=True)
                    url = StartpageParser._normalize_url(url_tag.get("href")) if url_tag else ""

                    rating_text = ""
                    rating_tag = container.select_one(".rating, .review-score, [aria-label*='star rating'], [itemprop='ratingValue']")
                    if rating_tag:
                        rating_text = rating_tag.get("content") or StartpageParser._extract_text(rating_tag)
                        rating_match = re.search(r"([0-9.]+)", rating_text)
                        rating_text = rating_match.group(1) if rating_match else rating_text

                    results.append({
                        "name": name, "address": address, "phone": phone, "url": url,
                        "rating": rating_text or None, "review_count": None,
                        "latitude": None, "longitude": None, "data_source": "html",
                    })
                    seen_places_identifiers.add(identifier)
                except Exception:
                    continue
        
        return {
            "results": results,
            "total_results": StartpageParser._extract_total_results(soup),
            "has_next_page": StartpageParser._find_next_page_link(soup),
        }

    @staticmethod
    def parse_suggestions(response_text: str) -> List[str]:
        """
        Parses search suggestions from JSON or HTML response.

        Args:
            response_text: The raw response text, expected to be JSON or HTML.

        Returns:
            A list of suggestion strings, up to a limit (e.g., 10).
            Returns an empty list if parsing fails or no suggestions are found.
        """
        suggestions: List[str] = []
        
        try:
            data = StartpageParser._safe_json_loads(response_text)
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                suggestions = [str(s) for s in data[1] if isinstance(s, (str, int, float))]
                return suggestions[:10]
        except Exception:
            pass

        try:
            soup = BeautifulSoup(response_text, "lxml")
            suggestion_item_selectors = [
                "li.suggestion-item", "div.autocomplete-suggestion",
                "option", "li[role='option']"
            ]
            suggestion_elements: List[element.Tag] = []

            for selector in suggestion_item_selectors:
                found = soup.select(selector)
                if found:
                    suggestion_elements.extend(found)
            
            if not suggestion_elements:
                 suggestion_elements = soup.find_all(["li", "div"], class_=re.compile(r"suggest|autocomplete", re.I))

            for elem in suggestion_elements:
                text = elem.get("value") or elem.get("data-suggestion") or StartpageParser._extract_text(elem)
                if text and text.strip() and text.strip() not in suggestions:
                    suggestions.append(text.strip())
            
            return suggestions[:10]
        except Exception:
            return []

    # Methods `_clean_html` and `_extract_total_results_bs` (and the html string version of total results)
    # are considered for removal/refactoring as their functionality is largely covered by
    # the improved `_extract_text` and the soup-based `_extract_total_results`.
    # Keeping them commented out for now in case any subtle use case was missed.

    # @staticmethod
    # def _extract_total_results_bs(soup: BeautifulSoup) -> int: ...

    # @staticmethod
    # def _clean_html(text: str) -> str: ...

    # @staticmethod
    # def _extract_total_results(html_str: str) -> int: ...