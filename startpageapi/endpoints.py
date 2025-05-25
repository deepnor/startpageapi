BASE_URL = "https://www.startpage.com"
SEARCH_URL = f"{BASE_URL}/sp/search"
SUGGESTIONS_URL = f"{BASE_URL}/suggestions"
QI_URL = f"{BASE_URL}/sp/qi"
SXPR_URL = f"{BASE_URL}/sp/sxpr"
IMAGES_URL = f"{BASE_URL}/sp/search"
VIDEOS_URL = f"{BASE_URL}/sp/search"
NEWS_URL = f"{BASE_URL}/sp/search"
PLACES_URL = f"{BASE_URL}/sp/search"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

SEARCH_CATEGORIES = {
    "web": "web",
    "images": "images", 
    "videos": "video",
    "news": "news",
    "places": "places"
}

LANGUAGE_CODES = {
    "english": "en",
    "german": "de", 
    "french": "fr",
    "spanish": "es",
    "italian": "it",
    "dutch": "nl",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja"
}

REGION_CODES = {
    "all": "all",
    "us": "us",
    "uk": "uk", 
    "ca": "ca",
    "au": "au",
    "de": "de",
    "fr": "fr",
    "es": "es",
    "it": "it",
    "nl": "nl"
}

SAFE_SEARCH_LEVELS = {
    "strict": "1",
    "moderate": "0", 
    "off": "2"
}

TIME_FILTERS = {
    "any": "",
    "day": "d",
    "week": "w", 
    "month": "m",
    "year": "y"
}

IMAGE_SIZES = {
    "any": "",
    "small": "s",
    "medium": "m",
    "large": "l",
    "wallpaper": "w"
}

VIDEO_DURATIONS = {
    "any": "",
    "short": "s",
    "medium": "m", 
    "long": "l"
}

ADVANCED_SEARCH_PARAMS = {
    "sc": "search_source",
    "sr": "search_results",
    "sxap": "search_expander_api_path",
    "qimsn": "query_instant_mode_search_number",
    "with_date": "time_filter",
    "abp": "ad_block_plus",
    "t": "search_type_modifier"
}

SEARCH_EXPANDER_PARAMS = {
    "se": "search_engine",
    "q": "query",
    "results": "search_results_data",
    "lang": "language_code",
    "allowAudio": "enable_audio_results",
    "externalLinksOpenInNewTab": "external_links_behavior",
    "sxAttribution": "search_expander_attribution",
    "showLoadingState": "loading_state_config",
    "screenBreakpoint": "responsive_breakpoint"
}
