# "Borrrowed" from https://github.com/langchain-ai/langchain/blob/master/libs/langchain_community/tools/duckduckgo_search.py
# FWIW I don't think this tool works. You get like a single result back. Maybe I'm doing something wrong, 
# but there are other more reliable search tools.
"""Util that calls DuckDuckGo Search.

No setup required. Free.
https://pypi.org/project/duckduckgo-search/
"""

from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, model_validator
from agentic.tools.utils.registry import tool_registry
from agentic.tools.base import BaseAgenticTool
from agentic.tools.utils.registry import tool_registry


@tool_registry.register(
    name="DuckDuckGoTool",
    description="Search the web using DuckDuckGo",
    dependencies=[
        tool_registry.Dependency(
            name="duckduckgo-search",
            version="7.5.5",
            type="pip",
        ),
    ],
)
class DuckDuckGoTool(BaseAgenticTool):
    """Wrapper for DuckDuckGo Search API.

    Free and does not require any setup.
    """
    model_config = ConfigDict(
        extra="forbid",
    )

    def __init__(
        self,
        region: Optional[str] = "wt-wt", # Options: see https://pypi.org/project/duckduckgo-search/#regions
        safesearch: str = "moderate", # Options: strict, moderate, off
        time: Optional[str] = "y", # Options: d, w, m, y
        max_results: int = 5,
        backend: str = "auto", # Options: auto, html, lite
        source: str = "text", # Options: text, news, images
    ):
        self.region = region
        self.safesearch = safesearch
        self.time = time
        self.max_results = max_results
        self.backend = backend
        self.source = source
        super().__init__()

    def get_tools(self):
        return [self.web_search_with_duckduckgo]
    
    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that python package exists in environment."""
        try:
            from duckduckgo_search import DDGS  # noqa: F401
        except ImportError:
            raise ImportError(
                "Could not import duckduckgo-search python package. "
                "Please install it with `pip install -U duckduckgo-search`."
            )
        return values

    def _ddgs_text(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo text search and return results."""
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(
                query,
                region=self.region,  # type: ignore[arg-type]
                safesearch=self.safesearch,
                timelimit=self.time,
                max_results=max_results or self.max_results,
                backend=self.backend,
            )
            if ddgs_gen:
                return [r for r in ddgs_gen]
        return []

    def _ddgs_news(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo news search and return results."""
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            ddgs_gen = ddgs.news(
                query,
                region=self.region,  # type: ignore[arg-type]
                safesearch=self.safesearch,
                timelimit=self.time,
                max_results=max_results or self.max_results,
            )
            if ddgs_gen:
                return [r for r in ddgs_gen]
        return []

    def _ddgs_images(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Run query through DuckDuckGo image search and return results."""
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            ddgs_gen = ddgs.images(
                query,
                region=self.region,  # type: ignore[arg-type]
                safesearch=self.safesearch,
                max_results=max_results or self.max_results,
            )
            if ddgs_gen:
                return [r for r in ddgs_gen]
        return []

    def run(self, query: str) -> str:
        """Run query through DuckDuckGo and return concatenated results."""
        if self.source == "text":
            results = self._ddgs_text(query)
        elif self.source == "news":
            results = self._ddgs_news(query)
        elif self.source == "images":
            results = self._ddgs_images(query)
        else:
            results = []

        if not results:
            return "No good DuckDuckGo Search Result was found"
        return " ".join(r["body"] for r in results)

    def web_search_with_duckduckgo(
        self, query: str, max_results: int= 10, source: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Perform web search on DuckDuckGo and return metadata.

        Args:
            query: The query to search for.
            max_results: The number of results to return.
            source: The source to look from.

        Returns:
            A list of dictionaries with the following keys:
                snippet - The description of the result.
                title - The title of the result.
                link - The link to the result.
        """
        source = source or self.source
        if source == "text":
            results = [
                {"snippet": r["body"], "title": r["title"], "link": r["href"]}
                for r in self._ddgs_text(query, max_results=max_results)
            ]
        elif source == "news":
            results = [
                {
                    "snippet": r["body"],
                    "title": r["title"],
                    "link": r["url"],
                    "date": r["date"],
                    "source": r["source"],
                }
                for r in self._ddgs_news(query, max_results=max_results)
            ]
        elif source == "images":
            results = [
                {
                    "title": r["title"],
                    "thumbnail": r["thumbnail"],
                    "image": r["image"],
                    "url": r["url"],
                    "height": r["height"],
                    "width": r["width"],
                    "source": r["source"],
                }
                for r in self._ddgs_images(query, max_results=max_results)
            ]
        else:
            results = []

        if results is None:
            results = [{"Result": "No good DuckDuckGo Search Result was found"}]

        return results