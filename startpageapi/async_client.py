"""
Provides an asynchronous client for interacting with the Startpage API.

This module defines the `AsyncStartpageClient` class, which wraps the
synchronous `StartpageAPI` client's methods to be awaitable using
`asyncio.to_thread`. This allows for non-blocking API calls in an
asynchronous Python application.
"""

import asyncio
from typing import Any, Dict, List, Optional

# Assuming StartpageAPI is the synchronous client from .client
# This import might need adjustment based on actual project structure
# For now, we'll assume it's available or will be type hinted.
# from .client import StartpageAPI


class AsyncStartpageClient:
    """
    An asynchronous wrapper client for the Startpage API.

    This client delegates its calls to a synchronous StartpageAPI client,
    executing them in a separate thread to achieve asynchronous behavior.
    It is intended for use in asyncio-based applications.

    Note:
        Session management (like `session.close()`) and direct HTTP error
        handling are managed by the underlying synchronous client. This wrapper
        primarily facilitates non-blocking calls.
    """

    def __init__(self, sync_client: Any):  # TODO: Replace Any with StartpageAPI
        """
        Initializes the AsyncStartpageClient.

        Args:
            sync_client: An instance of the synchronous StartpageAPI client.
        """
        self.sync_client = sync_client

    async def search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        time_filter: str = "any",
        page: int = 1,
        results_per_page: int = 10,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Asynchronously performs a web search.

        Delegates to the synchronous `search` method of the `sync_client`.

        Args:
            query: The search query string.
            language: The language for the search (e.g., "en", "de").
            region: The region for the search (e.g., "us", "all").
            safe_search: The safe search level ("off", "moderate", "strict").
            time_filter: Time filter for results ("any", "day", "week", "month").
            page: The page number of results to retrieve.
            results_per_page: Number of results to display per page.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the search results.

        Raises:
            Propagates exceptions from the synchronous client, which may include
            StartpageError, StartpageHTTPError, etc.
        """
        return await asyncio.to_thread(
            self.sync_client.search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            time_filter=time_filter,
            page=page,
            results_per_page=results_per_page,
            **kwargs,
        )

    async def images_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        size: str = "any",
        page: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Asynchronously performs an image search.

        Delegates to the synchronous `images_search` method.

        Args:
            query: The search query string for images.
            language: The language for the search.
            region: The region for the search.
            safe_search: The safe search level.
            size: Filter by image size ("any", "small", "medium", "large", "wallpaper").
            page: The page number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the image search results.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.images_search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            size=size,
            page=page,
            **kwargs,
        )

    async def videos_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        safe_search: str = "moderate",
        duration: str = "any",
        time_filter: str = "any",
        page: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Asynchronously performs a video search.

        Delegates to the synchronous `videos_search` method.

        Args:
            query: The search query string for videos.
            language: The language for the search.
            region: The region for the search.
            safe_search: The safe search level.
            duration: Filter by video duration ("any", "short", "medium", "long").
            time_filter: Time filter for results.
            page: The page number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the video search results.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.videos_search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            duration=duration,
            time_filter=time_filter,
            page=page,
            **kwargs,
        )

    async def news_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        time_filter: str = "any",
        page: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Asynchronously performs a news search.

        Delegates to the synchronous `news_search` method.

        Args:
            query: The search query string for news.
            language: The language for the search.
            region: The region for the search.
            time_filter: Time filter for news results.
            page: The page number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the news search results.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.news_search,
            query=query,
            language=language,
            region=region,
            time_filter=time_filter,
            page=page,
            **kwargs,
        )

    async def places_search(
        self,
        query: str,
        language: str = "en",
        region: str = "all",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        page: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Asynchronously performs a places (maps) search.

        Delegates to the synchronous `places_search` method.

        Args:
            query: The search query for places.
            language: The language for the search.
            region: The region for the search.
            latitude: Optional latitude for location-specific search.
            longitude: Optional longitude for location-specific search.
            radius: Optional radius (in meters) for location search.
            page: The page number of results.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the places search results.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.places_search,
            query=query,
            language=language,
            region=region,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            page=page,
            **kwargs,
        )

    async def suggestions(
        self, query_part: str, language: str = "en"
    ) -> List[str]:
        """
        Asynchronously fetches search suggestions.

        Delegates to the synchronous `suggestions` method.

        Args:
            query_part: The partial query string to get suggestions for.
            language: The language for the suggestions.

        Returns:
            A list of suggestion strings.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.suggestions,
            query_part=query_part,
            language=language,
        )

    async def instant_answers(
        self, query: str, language: str = "en", **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Asynchronously fetches instant answers.

        Delegates to the synchronous `instant_answers` method.

        Args:
            query: The query string for instant answers.
            language: The language for the answer.
            **kwargs: Additional parameters for the API.

        Returns:
            A dictionary containing the instant answer data.

        Raises:
            Propagates exceptions from the synchronous client.
        """
        return await asyncio.to_thread(
            self.sync_client.instant_answers,
            query=query,
            language=language,
            **kwargs,
        )
