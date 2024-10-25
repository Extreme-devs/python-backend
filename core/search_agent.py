from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from typing import List, Dict, Any, Tuple
from .config import settings
from .langchain_init import chatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import PromptTemplate
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse
import asyncio
from functools import partial

class WebFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.skip_domains = {'twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com'}
        self.timeout = 5

    def is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in {'http', 'https'} and parsed.netloc not in self.skip_domains
        except:
            return False

    async def fetch_content(self, url: str) -> Dict[str, Any]:
        if not self.is_valid_url(url):
            return {"error": "Invalid URL", "content": "", "url": url}
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(requests.get, url, headers=self.headers, timeout=self.timeout)
            )
            
            content = trafilatura.extract(
                response.text,
                include_links=True,
                include_tables=True,
                no_fallback=False
            )
            
            if not content:
                soup = BeautifulSoup(response.text, 'html.parser')
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                content = soup.get_text(separator=' ', strip=True)
            
            content = ' '.join(content.split())[:2000]
            
            return {
                "url": url,
                "content": content,
                "error": None
            }
            
        except Exception as e:
            return {"url": url, "content": "", "error": str(e)}

class ParallelSearchProcessor:
    def __init__(self, llm, chunk_size=1000):
        self.llm = llm
        self.chunk_size = chunk_size

    async def process_search_result(self, result: Dict[str, Any], web_content: Dict[str, Any]) -> str:
        try:
            context = f"""
            Title: {result.get('title', 'N/A')}
            Source: {result.get('source', 'N/A')}
            URL: {result.get('link', 'N/A')}
            Summary: {result.get('snippet', 'N/A')}
            
            Content: {web_content.get('content', 'No content available')}
            """
            
            prompt = f"""
            Analyze the following information and extract key points and insights:
            
            {context}
            
            Provide a concise summary of the most important information.
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.llm.predict(prompt)
            )
            
            return response.strip()
            
        except Exception as e:
            return f"Error processing result: {str(e)}"

class EnhancedGoogleSearch:
    def __init__(self, google_api_key: str, google_cse_id: str):
        self.search_instance = GoogleSearchAPIWrapper(
            google_api_key=google_api_key,
            google_cse_id=google_cse_id,
            k=5  # Number of results to return
        )
        self.web_fetcher = WebFetcher()

    async def async_run(self, query: str) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        try:
            # Get search results using the wrapper's search method
            results = self.search_instance.results(query, num_results=5)
            
            # Fetch web content in parallel
            tasks = [
                self.web_fetcher.fetch_content(result.get('link'))
                for result in results
                if result.get('link')
            ]
            
            web_contents = await asyncio.gather(*tasks)
            return list(zip(results, web_contents))
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def run(self, query: str) -> str:
        """Synchronous run method for compatibility with Langchain Tool"""
        try:
            results = self.search_instance.results(query, num_results=5)
            formatted_results = []
            
            for result in results:
                formatted_result = (
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Link: {result.get('link', 'N/A')}\n"
                    f"Snippet: {result.get('snippet', 'N/A')}\n"
                )
                formatted_results.append(formatted_result)
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"Search error: {str(e)}"

class SearchAgent:
    def __init__(self):
        self.llm = chatOpenAI
        self.search = EnhancedGoogleSearch(
            google_api_key=settings.GOOGLE_API_KEY,
            google_cse_id=settings.GOOGLE_CSE_ID,
        )
        self.processor = ParallelSearchProcessor(self.llm)
        
        search_prompt = """
        Search for detailed information about: {query}
        
        Instructions for processing the search results:
        1. Analyze all search results thoroughly
        2. Compare information across different sources
        3. Look for recent and authoritative sources
        4. Synthesize a comprehensive answer
        
        Current date: {current_date}
        Search query: {query}
        """
        
        self.tools = [
            Tool(
                name="google_search",
                description="""Use this tool to search Google and fetch webpage content.
                This tool provides comprehensive information from multiple sources.""",
                func=lambda q: self.search.run(
                    PromptTemplate(
                        template=search_prompt,
                        input_variables=["query", "current_date"]
                    ).format(
                        query=q,
                        current_date=datetime.now().strftime("%Y-%m-%d")
                    )
                )
            )
        ]
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate",
            callback_manager=CallbackManager([])
        )

    async def process_query(self, query: str) -> str:
        try:
            results_with_content = await self.search.async_run(query)
            
            if not results_with_content:
                return "No results found or error occurred during search."
            
            tasks = [
                self.processor.process_search_result(result, web_content)
                for result, web_content in results_with_content
            ]
            
            processed_results = await asyncio.gather(*tasks)
            
            combined_prompt = f"""
            Synthesize the following information into a comprehensive answer:

            {(chr(0x0a) * 2).join(processed_results)}
            
            Query: {query}
            """
            
            loop = asyncio.get_event_loop()
            final_response = await loop.run_in_executor(
                None,
                lambda: self.llm.predict(combined_prompt)
            )
            
            return self._format_response(final_response)
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def ask(self, query: str) -> str:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_query(query))

    def _format_response(self, response: str) -> str:
        response = response.replace("Based on the search results, ", "")
        response = response.replace("According to the search results, ", "")
        return response.strip()