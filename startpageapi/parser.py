import json
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from .exceptions import StartpageParseError

class StartpageParser:
    
    @staticmethod
    def parse_search_results(html: str, search_type: str = "web") -> Dict[str, Any]:
        try:
            if search_type == "web":
                return StartpageParser._parse_web_results(html)
            elif search_type == "images":
                return StartpageParser._parse_image_results(html)
            elif search_type == "videos":
                return StartpageParser._parse_video_results(html)
            elif search_type == "news":
                return StartpageParser._parse_news_results(html)
            elif search_type == "places":
                return StartpageParser._parse_places_results(html)
            else:
                raise StartpageParseError(f"Unknown search type: {search_type}")
        except Exception as e:
            raise StartpageParseError(f"Failed to parse search results: {str(e)}")
    
    @staticmethod
    def _parse_web_results(html: str) -> Dict[str, Any]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for different result container patterns used by Startpage
        result_containers = []
        
        # Try various class patterns
        for class_name in ['w-gl-result', 'w-gl-result w-gl-result--default', 'result', 'search-result']:
            containers = soup.find_all('div', class_=class_name)
            if containers:
                result_containers = containers
                break
        
        # Try with regex patterns
        if not result_containers:
            result_containers = soup.find_all('div', attrs={'class': re.compile(r'.*result.*')})
        
        # Try data attributes
        if not result_containers:
            result_containers = soup.find_all('div', {'data-testid': 'result'})
        
        # Fallback: look for divs with links and headings
        if not result_containers:
            all_divs = soup.find_all('div')
            result_containers = []
            for div in all_divs:
                if div.find('a') and (div.find('h3') or div.find('h2') or div.find('h4')):
                    result_containers.append(div)
        
        for container in result_containers:
            try:
                # Extract title and URL
                title_element = None
                url = None
                
                # Look for title in headings
                for tag in ['h3', 'h2', 'h4', 'h1']:
                    heading = container.find(tag)
                    if heading:
                        link = heading.find('a')
                        if link:
                            title_element = link
                            url = link.get('href', '')
                            break
                        else:
                            title_element = heading
                
                # If no title found in headings, look for any prominent link
                if not title_element:
                    link = container.find('a')
                    if link:
                        title_element = link
                        url = link.get('href', '')
                
                if not title_element:
                    continue
                
                # Extract title text
                title = StartpageParser._extract_text(title_element).strip()
                if not title:
                    continue
                
                # If no URL yet, look for it in container
                if not url:
                    link = container.find('a')
                    if link:
                        url = link.get('href', '')
                
                if not url:
                    continue
                
                # Extract description
                description = ""
                
                # Look for description in spans, paragraphs, divs
                for tag in ['span', 'p', 'div']:
                    desc_element = container.find(tag, attrs={'class': re.compile(r'.*(desc|snippet|summary).*', re.I)})
                    if desc_element:
                        description = StartpageParser._extract_text(desc_element).strip()
                        break
                
                # Extract display URL
                display_url = ""
                cite = container.find('cite')
                if cite:
                    display_url = StartpageParser._extract_text(cite).strip()
                else:
                    # Look for URL display elements
                    for tag in ['span', 'div']:
                        url_element = container.find(tag, attrs={'class': re.compile(r'.*url.*', re.I)})
                        if url_element:
                            display_url = StartpageParser._extract_text(url_element).strip()
                            break
                
                # Clean and validate URL
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = 'https://www.startpage.com' + url
                
                result = {
                    "title": title,
                    "url": url,
                    "description": description,
                    "display_url": display_url or url
                }
                
                results.append(result)
                
            except Exception:
                continue
        
        # Extract total results count
        total_results = StartpageParser._extract_total_results_bs(soup)
        
        # Check for next page
        has_next_page = bool(
            soup.find('a', string=re.compile(r'.*next.*', re.I)) or
            soup.find('button', string=re.compile(r'.*next.*', re.I))
        )
        
        return {
            "results": results,
            "total_results": total_results,
            "has_next_page": has_next_page
        }
    
    @staticmethod
    def _parse_image_results(html: str) -> Dict[str, Any]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Startpage images are embedded in a JavaScript data structure
        # Look for image data in script tags or data attributes
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_text = script.get_text() if script.string else ""
            # Look for image data patterns
            if 'data-src' in script_text or 'imageUrl' in script_text or '"url"' in script_text:
                # Try to extract JSON data containing images
                import json
                try:
                    # Look for JSON patterns that might contain image data
                    json_pattern = re.search(r'\{[^}]*"url"[^}]*\}', script_text)
                    if json_pattern:
                        json_data = json.loads(json_pattern.group())
                        if 'url' in json_data:
                            results.append({
                                "image_url": json_data['url'],
                                "source_url": json_data.get('source', ''),
                                "title": json_data.get('title', 'Image')
                            })
                except:
                    continue
        
        # Alternative: Look for standard image containers with more specific patterns
        if not results:
            # Look for images in result containers
            all_images = soup.find_all('img')
            for img in all_images:
                # Skip navigation and UI images
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if not src or any(skip in str(src).lower() for skip in ['icon', 'logo', 'button', 'ui']):
                    continue
                
                # Find parent container
                container = img.parent
                while container and container.name not in ['a', 'div', 'article']:
                    container = container.parent
                
                if not container:
                    continue
                
                # Get source URL
                source_url = ""
                if container.name == 'a':
                    source_url = container.get('href', '')
                else:
                    link_parent = container
                    for _ in range(3):  # Look up to 3 levels up
                        if link_parent and link_parent.name == 'a':
                            source_url = link_parent.get('href', '')
                            break
                        if link_parent:
                            link_parent = link_parent.parent
                
                # Get title from alt, title, or surrounding text
                title = img.get('alt') or img.get('title')
                if not title and container:
                    title_element = container.find(['h1', 'h2', 'h3', 'h4', 'span'])
                    if title_element:
                        title = StartpageParser._extract_text(title_element).strip()
                
                if not title:
                    title = "Image"
                
                # Clean URLs
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://www.startpage.com' + src
                
                if source_url and source_url.startswith('//'):
                    source_url = 'https:' + source_url
                elif source_url and source_url.startswith('/'):
                    source_url = 'https://www.startpage.com' + source_url
                
                result = {
                    "image_url": src,
                    "source_url": source_url,
                    "title": title
                }
                results.append(result)
        
        # Remove duplicates based on image URL
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['image_url'] not in seen_urls:
                seen_urls.add(result['image_url'])
                unique_results.append(result)
        
        return {
            "results": unique_results,
            "total_results": len(unique_results),
            "has_next_page": bool(soup.find('a', string=re.compile(r'.*next.*', re.I)))
        }
    
    @staticmethod
    def _parse_video_results(html: str) -> Dict[str, Any]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for video containers
        video_containers = soup.find_all('div', attrs={'class': re.compile(r'.*(video|vid).*', re.I)})
        
        if not video_containers:
            # Fallback: look for any containers with video-like content
            all_divs = soup.find_all('div')
            video_containers = [div for div in all_divs if div.find('a') and (div.find('h3') or div.find('h4'))]
        
        for container in video_containers:
            try:
                # Extract title and URL
                title_element = container.find('h3') or container.find('h4') or container.find('h2')
                if not title_element:
                    continue
                
                link = title_element.find('a') or container.find('a')
                if not link:
                    continue
                
                title = StartpageParser._extract_text(title_element).strip()
                url = link.get('href', '')
                
                if not title or not url:
                    continue
                
                # Extract description and duration
                description = ""
                duration = ""
                
                desc_element = container.find('span', attrs={'class': re.compile(r'.*(desc|snippet).*', re.I)})
                if desc_element:
                    description = StartpageParser._extract_text(desc_element).strip()
                
                duration_element = container.find('span', attrs={'class': re.compile(r'.*duration.*', re.I)})
                if duration_element:
                    duration = StartpageParser._extract_text(duration_element).strip()
                
                # Clean URL
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = 'https://www.startpage.com' + url
                
                result = {
                    "title": title,
                    "url": url,
                    "description": description,
                    "duration": duration
                }
                results.append(result)
                
            except Exception:
                continue
        
        return {
            "results": results,
            "total_results": len(results),
            "has_next_page": bool(soup.find('a', string=re.compile(r'.*next.*', re.I)))
        }
    
    @staticmethod
    def _parse_news_results(html: str) -> Dict[str, Any]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for news containers
        news_containers = soup.find_all('article') or soup.find_all('div', attrs={'class': re.compile(r'.*news.*', re.I)})
        
        if not news_containers:
            # Fallback
            all_divs = soup.find_all('div')
            news_containers = [div for div in all_divs if div.find('a') and div.find('h3')]
        
        for container in news_containers:
            try:
                # Extract title and URL
                title_element = container.find('h3') or container.find('h2') or container.find('h4')
                if not title_element:
                    continue
                
                link = title_element.find('a') or container.find('a')
                if not link:
                    continue
                
                title = StartpageParser._extract_text(title_element).strip()
                url = link.get('href', '')
                
                if not title or not url:
                    continue
                
                # Extract description, source, and date
                description = ""
                source = ""
                published_date = ""
                
                desc_element = container.find('p') or container.find('span', attrs={'class': re.compile(r'.*(desc|snippet).*', re.I)})
                if desc_element:
                    description = StartpageParser._extract_text(desc_element).strip()
                
                source_element = container.find('cite') or container.find('span', attrs={'class': re.compile(r'.*source.*', re.I)})
                if source_element:
                    source = StartpageParser._extract_text(source_element).strip()
                
                date_element = container.find('time') or container.find('span', attrs={'class': re.compile(r'.*(date|time).*', re.I)})
                if date_element:
                    published_date = StartpageParser._extract_text(date_element).strip()
                
                # Clean URL
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = 'https://www.startpage.com' + url
                
                result = {
                    "title": title,
                    "url": url,
                    "description": description,
                    "source": source,
                    "published_date": published_date
                }
                results.append(result)
                
            except Exception:
                continue
        
        return {
            "results": results,
            "total_results": len(results),
            "has_next_page": bool(soup.find('a', string=re.compile(r'.*next.*', re.I)))
        }
    
    @staticmethod
    def _parse_places_results(html: str) -> Dict[str, Any]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Startpage places often use map-based results or integrated location data
        # Look for map containers and location-specific elements
        
        # Try to find map/location containers first
        location_patterns = [
            'maps-result', 'location-result', 'place-result', 'business-result',
            'local-result', 'map-container', 'poi-result'
        ]
        
        place_containers = []
        for pattern in location_patterns:
            containers = soup.find_all('div', attrs={'class': re.compile(f'.*{pattern}.*', re.I)})
            if containers:
                place_containers.extend(containers)
        
        # Alternative: Look for address patterns and business info
        if not place_containers:
            # Look for elements that contain address-like text
            all_elements = soup.find_all(['div', 'article', 'section'])
            for element in all_elements:
                text = StartpageParser._extract_text(element)
                # Check if element contains address-like patterns
                if any(indicator in text.lower() for indicator in ['address', 'phone', 'hours', 'rating', 'reviews', 'directions']):
                    # Check if it also has a link or title
                    if element.find('a') or element.find(['h1', 'h2', 'h3', 'h4']):
                        place_containers.append(element)
        
        # Alternative: Look for structured data in scripts
        if not place_containers:
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    import json
                    data = json.loads(script.get_text())
                    if isinstance(data, dict) and data.get('@type') in ['LocalBusiness', 'Place', 'Restaurant']:
                        result = {
                            "name": data.get('name', ''),
                            "address": data.get('address', {}).get('streetAddress', '') if isinstance(data.get('address'), dict) else str(data.get('address', '')),
                            "phone": data.get('telephone', ''),
                            "rating": str(data.get('aggregateRating', {}).get('ratingValue', '')) if data.get('aggregateRating') else '',
                            "url": data.get('url', '')
                        }
                        if result['name']:
                            results.append(result)
                except:
                    continue
        
        # Process found containers
        for container in place_containers:
            try:
                # Extract name/title
                name_element = (container.find('h1') or container.find('h2') or 
                              container.find('h3') or container.find('h4') or
                              container.find('strong') or container.find('b'))
                
                if not name_element:
                    # Look for prominent link text
                    link = container.find('a')
                    if link:
                        name_element = link
                
                if not name_element:
                    continue
                
                name = StartpageParser._extract_text(name_element).strip()
                if not name or len(name) < 2:
                    continue
                
                # Extract URL
                url = ""
                link = container.find('a')
                if link:
                    url = link.get('href', '')
                
                # Extract address (look for text that looks like an address)
                address = ""
                text_content = StartpageParser._extract_text(container)
                
                # Look for address patterns
                address_patterns = [
                    r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[^,]*',
                    r'[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}',  # City, STATE ZIP
                    r'\d+[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}'  # Number, City, State
                ]
                
                for pattern in address_patterns:
                    match = re.search(pattern, text_content)
                    if match:
                        address = match.group(0).strip()
                        break
                
                # Extract phone number
                phone = ""
                phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
                phone_match = re.search(phone_pattern, text_content)
                if phone_match:
                    phone = phone_match.group(0).strip()
                
                # Extract rating
                rating = ""
                rating_patterns = [
                    r'(\d+\.?\d*)\s*(?:stars?|out of|/\s*5|\★)',
                    r'★+\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*★'
                ]
                
                for pattern in rating_patterns:
                    match = re.search(pattern, text_content)
                    if match:
                        rating = match.group(1).strip()
                        break
                
                # Clean URL
                if url and url.startswith('//'):
                    url = 'https:' + url
                elif url and url.startswith('/'):
                    url = 'https://www.startpage.com' + url
                
                result = {
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "rating": rating,
                    "url": url
                }
                results.append(result)
                
            except Exception:
                continue
        
        # Remove duplicates based on name
        seen_names = set()
        unique_results = []
        for result in results:
            if result['name'] not in seen_names:
                seen_names.add(result['name'])
                unique_results.append(result)
        
        return {
            "results": unique_results,
            "total_results": len(unique_results),
            "has_next_page": bool(soup.find('a', string=re.compile(r'.*next.*', re.I)))
        }
    
    @staticmethod
    def parse_suggestions(response_text: str) -> List[str]:
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('['):
                data = json.loads(response_text)
                if isinstance(data, list) and len(data) > 1:
                    return data[1] if isinstance(data[1], list) else []
            
            # Fallback: extract suggestions from HTML
            soup = BeautifulSoup(response_text, 'lxml')
            suggestions = []
            
            # Look for suggestion elements
            suggestion_elements = soup.find_all('li') or soup.find_all('div', attrs={'class': re.compile(r'.*suggest.*', re.I)})
            
            for element in suggestion_elements:
                text = StartpageParser._extract_text(element).strip()
                if text and text not in suggestions:
                    suggestions.append(text)
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception:
            return []
    
    @staticmethod
    def _extract_text(element) -> str:
        """Extract clean text from BeautifulSoup element"""
        if element is None:
            return ""
        
        if hasattr(element, 'get_text'):
            text = element.get_text()
        else:
            text = str(element)
        
        # Clean HTML entities and whitespace
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _extract_total_results_bs(soup) -> int:
        """Extract total results count from BeautifulSoup object"""
        try:
            # Look for results count indicators
            for pattern in [
                r'(\d+(?:,\d+)*)\s*results?',
                r'(\d+(?:,\d+)*)\s*of\s*',
                r'about\s*(\d+(?:,\d+)*)',
                r'(\d+(?:,\d+)*)\s*found'
            ]:
                text = soup.get_text()
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return int(match.group(1).replace(',', ''))
            
            return 0
        except Exception:
            return 0
    
    @staticmethod
    def _clean_html(text: str) -> str:
        """Clean HTML tags and entities from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode common HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#x27;': "'",
            '&#x2F;': '/',
            '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _extract_total_results(html: str) -> int:
        """Extract total results count from HTML string"""
        try:
            patterns = [
                r'(\d+(?:,\d+)*)\s*results?',
                r'(\d+(?:,\d+)*)\s*of\s*',
                r'about\s*(\d+(?:,\d+)*)',
                r'(\d+(?:,\d+)*)\s*found'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    return int(match.group(1).replace(',', ''))
            
            return 0
        except Exception:
            return 0