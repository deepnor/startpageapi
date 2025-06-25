"""
Defines constants for the Startpage API client.

This module contains base URLs, specific endpoint URLs, default HTTP headers,
and mappings for various search parameters like categories, language codes,
region codes, safe search levels, time filters, image sizes, video durations,
and advanced search parameter keys. These constants are used by the client
to construct and send requests to the Startpage service.
"""

# Base URLs
BASE_URL = "https://www.startpage.com"

# Specific Endpoint URLs
SEARCH_URL = f"{BASE_URL}/sp/search"
SUGGESTIONS_URL = f"{BASE_URL}/suggestions"
QI_URL = f"{BASE_URL}/sp/qi"  # Quick Information / Instant Answer endpoint (potentially)
SXPR_URL = f"{BASE_URL}/sp/sxpr" # Search Expander endpoint (potentially)

# Note: The following URLs are currently identical to SEARCH_URL.
# They are kept for conceptual separation and potential future API changes
# where these categories might get distinct endpoints.
IMAGES_URL = SEARCH_URL # f"{BASE_URL}/sp/search"
VIDEOS_URL = SEARCH_URL # f"{BASE_URL}/sp/search"
NEWS_URL = SEARCH_URL   # f"{BASE_URL}/sp/search"
PLACES_URL = SEARCH_URL # f"{BASE_URL}/sp/search"


# Default HTTP Headers sent with requests
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1", # Do Not Track
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none", # Indicates a top-level navigation
    "Cache-Control": "max-age=0",
}

# Mapping of user-friendly search categories to Startpage's internal POST parameters
# The client uses these keys (e.g. "images") and the values are sent to Startpage
# (e.g. "pics" for images, "video" for videos).
# This mapping is used by the client's _perform_search_request method.
# The `category_for_parser` in `_perform_search_request` uses the *keys* from here.
SEARCH_CATEGORIES = {
    "web": "web",       # Standard web search
    "images": "pics",   # Image search (Startpage uses "pics")
    "videos": "video",  # Video search
    "news": "news",     # News search
    "places": "map",    # Places/Maps search (Startpage uses "map")
}

# Mapping of human-readable language names to Startpage language codes
LANGUAGE_CODES = {
    "english": "en",
    "german": "de",
    "french": "fr",
    "spanish": "es",
    "italian": "it",
    "dutch": "nl",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh", # Simplified Chinese typically
    "japanese": "ja",
    # Add more as needed or refer to Startpage's own list if available
}

# Mapping of human-readable region names to Startpage region codes
REGION_CODES = {
    "all": "all", # Or can be an empty string depending on API
    "us": "us",   # United States
    "uk": "uk",   # United Kingdom
    "ca": "ca",   # Canada
    "au": "au",   # Australia
    "de": "de",   # Germany
    "fr": "fr",   # France
    "es": "es",   # Spain
    "it": "it",   # Italy
    "nl": "nl",   # Netherlands
    # Add more as needed
}

# Mapping of safe search levels to Startpage's parameter values
SAFE_SEARCH_LEVELS = {
    "strict": "1",   # Strictest filtering
    "moderate": "0", # Moderate filtering (often default)
    "off": "2",      # No filtering
}

# Mapping of time filter options to Startpage's parameter values
TIME_FILTERS = {
    "any": "",    # No time filter
    "day": "d",   # Past 24 hours
    "week": "w",  # Past week
    "month": "m", # Past month
    "year": "y",  # Past year (Startpage might use specific date ranges instead)
}

# Mapping of image size filters to Startpage's parameter values
IMAGE_SIZES = {
    "any": "",         # Any size
    "small": "s",
    "medium": "m",
    "large": "l",
    "wallpaper": "w", # Or "wallpaper", "xtralarge" - check Startpage specifics
}

# Mapping of video duration filters to Startpage's parameter values
VIDEO_DURATIONS = {
    "any": "",    # Any duration
    "short": "s", # Typically < 4 minutes
    "medium": "m",# Typically 4-20 minutes
    "long": "l",  # Typically > 20 minutes
}

# Mapping of readable advanced search keys to actual Startpage POST parameter names.
# These are used in the `advanced_search` method of the client.
ADVANCED_SEARCH_PARAMS = {
    # Example: "exact_phrase": "qexact" (if Startpage had such a param)
    # These seem to be more related to internal Startpage functionality or specific features
    # rather than common user-facing advanced search operators.
    "search_source": "sc",                      # Source of the search (e.g. web, image)
    "search_results": "sr",                   # Potentially related to results data
    "search_expander_api_path": "sxap",       # Path for search expander API
    "query_instant_mode_search_number": "qimsn", # Related to instant search behavior
    "time_filter": "with_date",               # Parameter name for time filtering
    "ad_block_plus": "abp",                   # AdBlock Plus related parameter
    "search_type_modifier": "t",              # General search type modifier
    # Common advanced search operators that could be mapped if supported:
    # "site_restrict": "sitesearch", (e.g. query site:example.com)
    # "file_type": "filetype", (e.g. query filetype:pdf)
}

# Parameters potentially related to Startpage's "Search Expander" feature.
# The keys are readable names, values are potential Startpage parameter names.
# Use and meaning might require deeper inspection of Startpage's requests.
SEARCH_EXPANDER_PARAMS = {
    "se": "search_engine",
    "q": "query",
    "results": "search_results_data",
    "lang": "language_code",
    "allow_audio": "enable_audio_results",
    "external_links_open_in_new_tab": "external_links_behavior",
    "sx_attribution": "search_expander_attribution",
    "show_loading_state": "loading_state_config",
    "screen_breakpoint": "responsive_breakpoint",
}
