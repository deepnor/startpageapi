import asyncio
from typing import Dict, List, Any, Optional

class AsyncStartpageClient:
    
    def __init__(self, sync_client):
        self.sync_client = sync_client
    
    async def search(self, 
                    query: str,
                    language: str = "en",
                    region: str = "all",
                    safe_search: str = "moderate", 
                    time_filter: str = "any",
                    page: int = 1,
                    results_per_page: int = 10,
                    **kwargs) -> Dict[str, Any]:
        
        return await asyncio.to_thread(
            self.sync_client.search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            time_filter=time_filter,
            page=page,
            results_per_page=results_per_page,
            **kwargs
        )
    
    async def images_search(self,
                           query: str,
                           language: str = "en",
                           region: str = "all",
                           safe_search: str = "moderate",
                           size: str = "any", 
                           page: int = 1,
                           **kwargs) -> Dict[str, Any]:
        
        return await asyncio.to_thread(
            self.sync_client.images_search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            size=size,
            page=page,
            **kwargs
        )
    
    async def videos_search(self,
                           query: str,
                           language: str = "en",
                           region: str = "all",
                           safe_search: str = "moderate",
                           duration: str = "any",
                           time_filter: str = "any",
                           page: int = 1,
                           **kwargs) -> Dict[str, Any]:
        
        return await asyncio.to_thread(
            self.sync_client.videos_search,
            query=query,
            language=language,
            region=region,
            safe_search=safe_search,
            duration=duration,
            time_filter=time_filter,
            page=page,
            **kwargs
        )
    
    async def news_search(self,
                         query: str,
                         language: str = "en",
                         region: str = "all",
                         time_filter: str = "any",
                         page: int = 1,
                         **kwargs) -> Dict[str, Any]:
        
        return await asyncio.to_thread(
            self.sync_client.news_search,
            query=query,
            language=language,
            region=region,
            time_filter=time_filter,
            page=page,
            **kwargs
        )
    
    async def places_search(self,
                           query: str,
                           language: str = "en", 
                           region: str = "all",
                           latitude: Optional[float] = None,
                           longitude: Optional[float] = None,
                           radius: Optional[int] = None,
                           page: int = 1,
                           **kwargs) -> Dict[str, Any]:
        
        return await asyncio.to_thread(
            self.sync_client.places_search,
            query=query,
            language=language,
            region=region,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            page=page,
            **kwargs
        )
    
    async def suggestions(self, query_part: str, language: str = "en") -> List[str]:
        return await asyncio.to_thread(
            self.sync_client.suggestions,
            query_part=query_part,
            language=language
        )
    
    async def instant_answers(self, query: str, language: str = "en", **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(
            self.sync_client.instant_answers,
            query=query,
            language=language,
            **kwargs
        )
