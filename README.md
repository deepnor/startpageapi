# StartpageAPI

An unofficial Python library for searching Startpage.com with a focus on privacy and accurate results.

## Overview

StartpageAPI is a Python library that allows developers to access search results from Startpage.com, a privacy-focused search engine. This library enables various search operations such as web search, image search, video search, news search, and places search, as well as retrieving search suggestions and instant answers.

## Features

1. Web Search - Search the web with multiple filtering options
2. Images Search - Find images with various size options
3. Videos Search - Discover videos with duration and time filtering
4. News Search - Get the latest news with time filtering
5. Places Search - Find locations with geographic coordinates support
6. Search Suggestions - Get query suggestions as you type
7. Instant Answers - Receive quick answers and knowledge panels

## Installation

You can install the library using one of the following methods:

### Option 1: Install from PyPI

The easiest way to install the library is using pip:

```bash
pip install startpageapi
```

### Option 2: Install from GitHub

You can also install the latest version directly from the GitHub repository:

```bash
# Clone the repository
git clone https://github.com/deepnor/startpageapi.git

# Navigate to the project directory
cd startpageapi

# Install the package
pip install .
```

Or install directly using pip:

```bash
pip install git+https://github.com/deepnor/startpageapi.git
```

## Basic Usage

### Web Search

```python
from startpageapi import StartpageAPI

# Create API object
api = StartpageAPI()

# Perform a simple web search
results = api.search("Python programming language")

# Print results
for result in results.get('results', []):
    print(f"Title: {result.get('title')}")
    print(f"URL: {result.get('url')}")
    print(f"Description: {result.get('description')}")
    print("---")
```

### Image Search

```python
# Search for images
image_results = api.images_search("nature landscape", size="large")

# Print image results
for image in image_results.get('results', []):
    print(f"Title: {image.get('title')}")
    print(f"Image URL: {image.get('image_url')}")
    print(f"Source URL: {image.get('source_url')}")
    print("---")
```

### Video Search

```python
# Search for videos
video_results = api.videos_search("documentary", duration="long", time_filter="year")

# Print video results
for video in video_results.get('results', []):
    print(f"Title: {video.get('title')}")
    print(f"Video URL: {video.get('url')}")
    print(f"Duration: {video.get('duration')}")
    print("---")
```

### News Search

```python
# Search for news
news_results = api.news_search("technology", time_filter="week")

# Print news results
for news in news_results.get('results', []):
    print(f"Title: {news.get('title')}")
    print(f"URL: {news.get('url')}")
    print(f"Source: {news.get('source')}")
    print(f"Published Date: {news.get('published_date')}")
    print("---")
```

### Getting Search Suggestions

```python
# Get search suggestions
suggestions = api.suggestions("artificial intel")

# Print suggestions
for suggestion in suggestions:
    print(suggestion)
```

### Getting Instant Answers

```python
# Get instant answers
answers = api.instant_answers("what is the capital of France")

# Print instant answer
if answers.get('instant_answer'):
    print(f"Instant Answer: {answers.get('instant_answer')}")

# Print knowledge panel
if answers.get('knowledge_panel'):
    panel = answers.get('knowledge_panel')
    print(f"Title: {panel.get('title')}")
    print(f"Description: {panel.get('description')}")
    print("Facts:")
    for fact_name, fact_value in panel.get('facts', {}).items():
        print(f"  {fact_name}: {fact_value}")
```

## Advanced Options

### Using a Proxy

```python
# Create API object with proxy
api = StartpageAPI(proxy="http://your-proxy-server:port")

# Perform search through proxy
results = api.search("Python programming")
```

### Setting Timeout and Request Delay

```python
# Set connection timeout and request delay
api = StartpageAPI(timeout=60, delay=2.0)
```

### Searching in Different Languages and Regions

```python
# Search in Arabic language for Middle East region
results = api.search("Python programming", language="ar", region="me")
```

### Using the Asynchronous API

```python
import asyncio

async def main():
    # Create API object
    api = StartpageAPI()
    
    # Use asynchronous API
    results = await api.aio.search("Python programming")
    
    # Print results
    for result in results.get('results', []):
        print(f"Title: {result.get('title')}")
        print(f"URL: {result.get('url')}")
        print("---")

# Run the async function
asyncio.run(main())
```

## Supported Parameters

### Web Search

- `query`: Search query (required)
- `language`: Language code (default: "en")
- `region`: Region code (default: "all")
- `safe_search`: Safe search level ("off", "moderate", "strict") (default: "moderate")
- `time_filter`: Time filter ("any", "day", "week", "month", "year") (default: "any")
- `page`: Page number (default: 1)
- `results_per_page`: Number of results per page (default: 10)

### Image Search

- `query`: Search query (required)
- `language`: Language code (default: "en")
- `region`: Region code (default: "all")
- `safe_search`: Safe search level (default: "moderate")
- `size`: Image size ("small", "medium", "large", "any") (default: "any")
- `page`: Page number (default: 1)

### Video Search

- `query`: Search query (required)
- `language`: Language code (default: "en")
- `region`: Region code (default: "all")
- `safe_search`: Safe search level (default: "moderate")
- `duration`: Video duration ("short", "medium", "long", "any") (default: "any")
- `time_filter`: Time filter (default: "any")
- `page`: Page number (default: 1)

### News Search

- `query`: Search query (required)
- `language`: Language code (default: "en")
- `region`: Region code (default: "all")
- `time_filter`: Time filter (default: "any")
- `page`: Page number (default: 1)

### Places Search

- `query`: Search query (required)
- `language`: Language code (default: "en")
- `region`: Region code (default: "all")
- `latitude`: Latitude (optional)
- `longitude`: Longitude (optional)
- `radius`: Search radius in kilometers (optional)
- `page`: Page number (default: 1)

## Notes and Limitations

- This library is unofficial and not affiliated with Startpage.com.
- The API interface may change if Startpage.com's interface changes.
- Rate limiting may be imposed by Startpage.com, so it's recommended to use the `delay` parameter to avoid this.
- Please use the library responsibly and respect Startpage.com's terms of service.

## Test Results

Manual tests were performed on the library with the following results:

- ✅ Creating StartpageAPI object: Passed
- ✅ Basic web search: Passed
- ✅ Image search: Passed
- ✅ Video search: Passed
- ✅ News search: Passed
- ✅ Search suggestions: Passed
- ✅ Error handling: Passed

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or fix (`git checkout -b feature/amazing-feature`)
3. Make your changes and commit them (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

deepnor - [GitHub](https://github.com/deepnor)

Project Link: [https://github.com/deepnor/startpageapi](https://github.com/deepnor/startpageapi)
