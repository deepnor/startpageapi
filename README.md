# StartpageAPI

**StartpageAPI** is an unofficial Python library for interacting with Startpage.com, a search engine that emphasizes user privacy. It allows developers to programmatically perform searches and retrieve results for web pages, images, videos, news, and places. Additionally, it supports fetching search suggestions and instant answers.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Core Client and Functions](#core-client-and-functions)
  - [`search()`](#search)
  - [`images_search()`](#images_search)
  - [`videos_search()`](#videos_search)
  - [`news_search()`](#news_search)
  - [`places_search()`](#places_search)
  - [`suggestions()`](#suggestions)
  - [`instant_answers()`](#instant_answers)
  - [`get_search_url()`](#get_search_url)
  - [`advanced_search()`](#advanced_search)
- [Advanced Configuration](#advanced-configuration)
  - [Using a Proxy](#using-a-proxy)
  - [Setting Timeout and Request Delay](#setting-timeout-and-request-delay)
- [Supported Parameters Overview](#supported-parameters-overview)
- [Notes and Limitations](#notes-and-limitations)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

This library provides a convenient way to integrate Startpage's search capabilities into Python applications. It offers both synchronous and asynchronous interfaces, making it flexible for different programming needs. Key features include:

- Web, image, video, news, and places search.
- Retrieval of search suggestions.
- Access to instant answers and knowledge panels.
- Support for advanced search parameters like language, region, and safe search.
- Options for using proxies and configuring request behavior (timeout, delay).

## Quick Start

```python
from startpageapi import StartpageAPI

# Initialize the API client
api = StartpageAPI()

# Perform a basic web search
results_data = api.search(query="Python programming language")

# Print titles and URLs of the first few results
print("Quick Search Results:")
for result in results_data.get('results', [])[:3]: # Limit to first 3 results for brevity
    print(f"- Title: {result.get('title')}\n  URL: {result.get('url')}")
print("---")
```

## Installation

You can install StartpageAPI using pip:

```bash
pip install startpageapi
```

Alternatively, install the latest version directly from the GitHub repository:

```bash
pip install git+https://github.com/deepnor/startpageapi.git
```

Or, clone and install manually:
```bash
git clone https://github.com/deepnor/startpageapi.git
cd startpageapi
pip install .
```

## Core Client and Functions

The primary way to use the library is through the `StartpageAPI` class.

```python
from startpageapi import StartpageAPI

# Initialize the synchronous client
api = StartpageAPI()

# For asynchronous operations, access the `aio` attribute:
# async_api = api.aio
```

### `search()`

Performs a web search.

**Description:** This function queries Startpage for general web results based on the provided search term and parameters.
It returns a dictionary containing a list of search results, the total number of results, and whether a next page is available.

**Synchronous Usage:**
```python
results_data = api.search(
    query="Python programming language",
    language="en",
    region="us",
    safe_search="moderate",
    time_filter="week",
    page=1,
    results_per_page=10
)

for result in results_data.get('results', []):
    print(f"Title: {result.get('title')}")
    print(f"URL: {result.get('url')}")
    print(f"Description: {result.get('description')}")
    print("---")

print(f"Total Results: {results_data.get('total_results')}")
print(f"Has Next Page: {results_data.get('has_next_page')}")
```

**Asynchronous Usage:**
```python
import asyncio

async def main():
    results_data = await api.aio.search(
        query="Python programming language",
        language="en"
    )
    for result in results_data.get('results', []):
        print(f"Title: {result.get('title')}, URL: {result.get('url')}")

# asyncio.run(main()) # Uncomment to run
```

### `images_search()`

Performs an image search.

**Description:** This function queries Startpage for images matching the search term. Results include image URLs, source URLs, and titles.

**Synchronous Usage:**
```python
image_results_data = api.images_search(
    query="beautiful landscapes",
    size="large",
    language="en",
    safe_search="moderate"
)

for image in image_results_data.get('results', []):
    print(f"Title: {image.get('title')}")
    print(f"Image URL: {image.get('image_url')}")
    print(f"Source URL: {image.get('source_url')}")
    print("---")
```

**Asynchronous Usage:**
```python
import asyncio

async def main_images():
    image_results_data = await api.aio.images_search(
        query="cute kittens",
        size="medium"
    )
    for image in image_results_data.get('results', []):
        print(f"Title: {image.get('title')}, Image URL: {image.get('image_url')}")

# asyncio.run(main_images()) # Uncomment to run
```

### `videos_search()`

Performs a video search.

**Description:** This function finds videos related to the query, providing details like title, URL, description, and duration.

**Synchronous Usage:**
```python
video_results_data = api.videos_search(
    query="Python tutorials",
    duration="short",
    time_filter="month"
)

for video in video_results_data.get('results', []):
    print(f"Title: {video.get('title')}")
    print(f"Video URL: {video.get('url')}")
    print(f"Duration: {video.get('duration')}")
    print("---")
```

**Asynchronous Usage:**
```python
import asyncio

async def main_videos():
    video_results_data = await api.aio.videos_search(
        query="latest movie trailers",
        duration="medium"
    )
    for video in video_results_data.get('results', []):
        print(f"Title: {video.get('title')}, URL: {video.get('url')}")

# asyncio.run(main_videos()) # Uncomment to run
```

### `news_search()`

Performs a news search.

**Description:** Retrieves news articles relevant to the query, including title, URL, source, and publication date.

**Synchronous Usage:**
```python
news_results_data = api.news_search(
    query="technology advancements",
    time_filter="day",
    region="us"
)

for news_item in news_results_data.get('results', []):
    print(f"Title: {news_item.get('title')}")
    print(f"URL: {news_item.get('url')}")
    print(f"Source: {news_item.get('source')}")
    print(f"Published: {news_item.get('published_date')}")
    print("---")
```

**Asynchronous Usage:**
```python
import asyncio

async def main_news():
    news_results_data = await api.aio.news_search(
        query="global economy",
        time_filter="week"
    )
    for news_item in news_results_data.get('results', []):
        print(f"Title: {news_item.get('title')}, Source: {news_item.get('source')}")

# asyncio.run(main_news()) # Uncomment to run
```

### `places_search()`

Performs a places (maps/local) search.

**Description:** Finds information about places, such as businesses or points of interest. Can use latitude/longitude for location-specific searches.

**Synchronous Usage:**
```python
places_results_data = api.places_search(
    query="restaurants near Eiffel Tower",
    language="en",
    # latitude=48.8584,  # Optional
    # longitude=2.2945,  # Optional
    # radius=1000        # Optional, in meters
)

for place in places_results_data.get('results', []):
    print(f"Name: {place.get('name')}")
    print(f"Address: {place.get('address')}")
    print(f"Phone: {place.get('phone')}")
    print(f"Rating: {place.get('rating')}")
    print("---")
```

**Asynchronous Usage:**
```python
import asyncio

async def main_places():
    places_results_data = await api.aio.places_search(
        query="coffee shops in downtown",
        latitude=34.0522,
        longitude=-118.2437
    )
    for place in places_results_data.get('results', []):
        print(f"Name: {place.get('name')}, Address: {place.get('address')}")

# asyncio.run(main_places()) # Uncomment to run
```

### `suggestions()`

Fetches search suggestions for a partial query.

**Description:** Provides a list of potential search queries based on the input string, useful for autocomplete features.

**Synchronous Usage:**
```python
search_suggestions = api.suggestions(query_part="artificial intel", language="en")
for suggestion in search_suggestions:
    print(suggestion)
```

**Asynchronous Usage:**
```python
import asyncio

async def main_suggestions():
    search_suggestions = await api.aio.suggestions(query_part="how to learn py")
    for suggestion in search_suggestions:
        print(suggestion)

# asyncio.run(main_suggestions()) # Uncomment to run
```

### `instant_answers()`

Fetches instant answers and knowledge panel information.

**Description:** This function attempts to retrieve direct answers to queries (e.g., definitions, calculations) and structured information from knowledge panels.

**Synchronous Usage:**
```python
answer_data = api.instant_answers(query="what is the capital of France", language="en")

if answer_data.get('instant_answer'):
    print(f"Instant Answer: {answer_data.get('instant_answer')}")

if answer_data.get('knowledge_panel'):
    panel = answer_data.get('knowledge_panel')
    print(f"Knowledge Panel Title: {panel.get('title')}")
    print(f"Description: {panel.get('description')}")
    if panel.get('facts'):
        print("Facts:")
        for fact_name, fact_value in panel.get('facts', {}).items():
            print(f"  {fact_name}: {fact_value}")
```

**Asynchronous Usage:**
```python
import asyncio

async def main_answers():
    answer_data = await api.aio.instant_answers(query="current time in London")
    if answer_data.get('instant_answer'):
        print(f"Instant Answer: {answer_data.get('instant_answer')}")
    # Further processing of knowledge_panel if needed

# asyncio.run(main_answers()) # Uncomment to run
```

### `get_search_url()`

Constructs the full search URL for a given query and parameters.

**Description:** Useful for debugging or if you need to understand the URL structure StartpageAPI uses for its requests.

**Synchronous Usage:** (This function is part of the synchronous client only)
```python
search_url = api.get_search_url(
    query="Python programming",
    search_type="web",  # "web", "images", "videos", "news", "places"
    language="de",
    region="de"
)
print(f"Constructed Search URL: {search_url}")
```

### `advanced_search()`

Performs an "advanced" web search using specific filter parameters.

**Description:**
The `advanced_search()` method allows you to refine web searches by utilizing specific filter parameters that Startpage supports. These parameters are defined in `startpageapi.endpoints.ADVANCED_SEARCH_PARAMS`. The method essentially constructs a web search query incorporating these advanced options. If you need to apply similar advanced filtering to other search types (images, videos, etc.), you would pass the relevant parameters directly to their respective search functions (e.g., `images_search(query="cats", size="large", time_filter="week")`) if those functions support them as keyword arguments.

**Synchronous Usage:**
The `advanced_search()` method takes a `query` and additional keyword arguments that correspond to the keys in `ADVANCED_SEARCH_PARAMS` or other general search parameters.

```python
# api is an instance of StartpageAPI()

# Example using 'time_filter', which is a common parameter also mapped in ADVANCED_SEARCH_PARAMS.
# Let's assume 'ADVANCED_SEARCH_PARAMS' maps 'time_filter' to 'with_date'.
# The client internally handles this mapping.
advanced_results_data = api.advanced_search(
    query="latest developments in AI",
    time_filter="month",  # This key should exist in ADVANCED_SEARCH_PARAMS or be a general param
    language="en"
)

print("\nAdvanced Search Results (Synchronous):")
for result in advanced_results_data.get('results', [])[:2]: # First 2 results
    print(f"- Title: {result.get('title')}")
    print(f"  URL: {result.get('url')}")
print("---")

# Example using a hypothetical parameter from ADVANCED_SEARCH_PARAMS
# Assuming ADVANCED_SEARCH_PARAMS = {"search_source": "sc", ...}
# advanced_results_custom = api.advanced_search(
#     query="specific query",
#     search_source="news" # Using a key from ADVANCED_SEARCH_PARAMS
# )
# print("\nCustom Advanced Search Results:")
# for result in advanced_results_custom.get('results', [])[:2]:
#     print(f"- Title: {result.get('title')}")
```
*Note: The exact behavior and available parameters for `advanced_search` depend on the `ADVANCED_SEARCH_PARAMS` mapping in `startpageapi/endpoints.py` and the underlying Startpage functionality. The primary purpose is to provide a dedicated method for web searches that might use very specific, less common Startpage parameters.*

**Asynchronous Usage:**
For asynchronous operations, advanced search parameters are typically passed as keyword arguments directly to the standard asynchronous search methods like `api.aio.search()`. There isn't a dedicated `api.aio.advanced_search()` distinct from `api.aio.search()` with extra parameters.

```python
import asyncio

# api is an instance of StartpageAPI()

async def main_advanced_async():
    print("\nAdvanced Search Results (Asynchronous):")
    # Pass advanced parameters directly to the relevant async search method
    results_async_data = await api.aio.search(
        query="future of renewable energy",
        time_filter="year", # Example of an advanced parameter
        language="en",
        safe_search="strict"
    )
    for result in results_async_data.get('results', [])[:2]: # First 2 results
        print(f"- Title: {result.get('title')}")
        print(f"  URL: {result.get('url')}")
    print("---")

# To run this example:
# async def run_all_async():
#     await main_advanced_async()
# asyncio.run(run_all_async())
```

## Advanced Configuration

### Using a Proxy

You can configure the `StartpageAPI` client to use an HTTP/HTTPS proxy.

```python
api_with_proxy = StartpageAPI(proxy="http://your-proxy-server:port")
# All searches using api_with_proxy will go through the proxy
results = api_with_proxy.search("test query")
```

### Setting Timeout and Request Delay

Control network request behavior:
- `timeout`: Maximum time (in seconds) to wait for a response.
- `delay`: Minimum time (in seconds) to wait between consecutive requests to avoid rate limiting.

```python
custom_api = StartpageAPI(timeout=60, delay=2.0) # 60s timeout, 2s delay
results = custom_api.search("another query")
```

## Supported Parameters Overview

Each search function accepts various parameters to refine the results. Here's a general overview (refer to specific function documentation above for exact parameters per function):

- **`query`**: The search term (required for most searches).
- **`language`**: Two-letter language code (e.g., "en", "de"). Defaults to "en".
- **`region`**: Two-letter region code (e.g., "us", "gb"). Defaults to "all".
- **`safe_search`**: Filtering level ("off", "moderate", "strict"). Default varies.
- **`time_filter`**: Time period for results ("any", "day", "week", "month", "year"). Default varies.
- **`page`**: Page number of results to fetch. Defaults to 1.
- **`results_per_page`**: Number of results per page (primarily for web search). Defaults to 10.
- **Image Specific:** `size` ("any", "small", "medium", "large", "wallpaper").
- **Video Specific:** `duration` ("any", "short", "medium", "long").
- **Places Specific:** `latitude`, `longitude`, `radius` (in meters).

## Error Handling

When using StartpageAPI, you might encounter several types of errors. Here’s a brief guide to common ones and how to approach them:

- **`StartpageHTTPError`**: This is raised for HTTP errors returned by Startpage (e.g., 4xx client errors, 5xx server errors).
    - **Troubleshooting**:
        - Check the status code and message from the error.
        - A `429 Too Many Requests` error is specifically caught as `StartpageRateLimitError`. If you see this, increase the `delay` parameter when initializing `StartpageAPI` (e.g., `StartpageAPI(delay=2.0)`).
        - Other 4xx errors might indicate an issue with your request parameters.
        - 5xx errors usually indicate a problem on Startpage's end; try again later.

- **`StartpageRateLimitError`**: A subclass of `StartpageHTTPError`, specifically for 429 errors.
    - **Troubleshooting**: Increase the `delay` when creating the `StartpageAPI` instance (e.g., `StartpageAPI(delay=2.0)` or higher).

- **`StartpageParseError`**: Raised if the library fails to parse the HTML response from Startpage.
    - **Troubleshooting**:
        - This might happen if Startpage changes its website structure. Check if there's an updated version of the library or report the issue.
        - Ensure your query is valid and likely to return parseable results.

- **`StartpageError`**: A general base exception for other library-specific issues, such as network problems not covered by HTTP errors (e.g., DNS failure, connection refused). It can also be raised for unexpected issues during a request.
    - **Troubleshooting**:
        - Check your internet connection.
        - If using a proxy, ensure the proxy is working correctly.
        - The error message might provide more details.

- **`requests.exceptions.Timeout` (or `urllib.error.URLError` with timeout context)**: If a request takes longer than the specified `timeout` value.
    - **Troubleshooting**:
        - Increase the `timeout` parameter during `StartpageAPI` initialization (e.g., `StartpageAPI(timeout=60)`).
        - Check your network speed and stability.

- **`ValueError`**: Often raised for invalid input parameters, like an empty query string.
    - **Troubleshooting**: Ensure all required parameters are provided and are of the correct type/format.

**General Advice for Handling Errors:**

- **Use `try-except` blocks**: Wrap your API calls in `try-except` blocks to catch these specific exceptions and handle them gracefully in your application.
  ```python
  from startpageapi import StartpageAPI, StartpageError, StartpageHTTPError

  api = StartpageAPI(delay=1.0, timeout=30)
  try:
      results = api.search("complex query")
      # Process results
  except StartpageRateLimitError:
      print("Rate limit hit. Please wait before trying again or increase delay.")
  except StartpageHTTPError as e:
      print(f"An HTTP error occurred: {e.status_code} - {e.message}")
  except StartpageError as e:
      print(f"A StartpageAPI error occurred: {e}")
  except Exception as e: # Catch any other unexpected errors
      print(f"An unexpected error occurred: {e}")
  ```
- **Logging**: Implement logging to record errors, which can help in debugging issues, especially for applications running in the background.

By anticipating these common errors, you can build more resilient applications using StartpageAPI.

## Notes and Limitations

- This library is unofficial and not affiliated with Startpage.com.
- Startpage.com may change its website structure or API, which could break this library. Efforts will be made to keep it updated.
- Be mindful of Startpage.com's terms of service and use the library responsibly. Aggressive scraping is discouraged.
- Rate limiting can occur if too many requests are made in a short period. Use the `delay` parameter in `StartpageAPI` constructor to mitigate this.

## Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository.
2. Create a new branch for your feature or fix (e.g., `git checkout -b feature/new-search-filter`).
3. Make your changes and commit them with clear messages.
4. Push your branch to your fork (`git push origin feature/new-search-filter`).
5. Open a Pull Request against the `main` branch of the original repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Created by **deepnor**.
- GitHub: [https://github.com/deepnor](https://github.com/deepnor)
- Project Link: [https://github.com/deepnor/startpageapi](https://github.com/deepnor/startpageapi)
