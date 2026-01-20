import sys
from typing import Dict, List
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

sys.path.append('..')

from ..state import Phase2State



def get_wikipedia_tool(top_k: int = 3, max_chars: int = 4000):
    """
    Initialize LangChain Wikipedia tool.
    
    Args:
        top_k: Number of results per query
        max_chars: Max characters per document
    
    Returns:
        WikipediaQueryRun tool
    """
    api_wrapper = WikipediaAPIWrapper(
        top_k_results=top_k,
        doc_content_chars_max=max_chars,
        load_all_available_meta=True
    )
    return WikipediaQueryRun(api_wrapper=api_wrapper)



def fetch_wikipedia_articles(query: str, tool: WikipediaQueryRun) -> Dict:
    """
    Fetch Wikipedia articles for a query using LangChain.
    
    Args:
        query: Search query
        tool: Wikipedia tool instance
    
    Returns:
        Results dict with articles
    """
    try:
        result = tool.run(query)
        
        if not result or result.startswith("No good Wikipedia Search Result"):
            return {
                "query": query,
                "success": False,
                "error": "No results found"
            }
        
        articles = []
        
        parts = result.split("\nPage: ")
        
        for i, part in enumerate(parts):
            if not part.strip():
                continue
            
            if i == 0 and part.startswith("Page: "):
                part = part[6:]  # Remove "Page: "
            
            lines = part.split("\n", 1)
            if len(lines) >= 2:
                title = lines[0].strip()
                summary = lines[1].replace("Summary: ", "").strip()
                
                articles.append({
                    "title": title,
                    "summary": summary,
                    "source": "wikipedia"
                })
        
        return {
            "query": query,
            "articles": articles,
            "raw_result": result,
            "success": True,
            "articles_found": len(articles)
        }
        
    except Exception as e:
        return {
            "query": query,
            "success": False,
            "error": str(e)
        }


def fetch_all_articles(queries: List[Dict], top_k: int = 3) -> tuple:
    """
    Fetch Wikipedia articles for all queries.
    
    Args:
        queries: List of query dicts
        top_k: Number of results per query
    
    Returns:
        (successful_results, failed_queries)
    """
    wiki_tool = get_wikipedia_tool(top_k=top_k, max_chars=4000)
    
    successful = []
    failed = []
    
    print(f"\n🔍 Fetching Wikipedia articles ({top_k} results per query)...\n")
    
    for i, query_obj in enumerate(queries, 1):
        query = query_obj["query"]
        priority = query_obj.get("priority", "medium")
        
        print(f"   [{i}/{len(queries)}] Searching: {query}...")
        
        result = fetch_wikipedia_articles(query, wiki_tool)
        
        if result.get("success"):
            articles_count = result.get("articles_found", 0)
            successful.append(result)
            print(f"   ✓ Found {articles_count} article(s)")
            
            for article in result.get("articles", [])[:2]:
                print(f"      • {article['title']}")
        else:
            failed.append(query)
            error_msg = result.get("error", "Unknown error")
            print(f"   ✗ Failed: {error_msg}")
    
    return successful, failed



def wikipedia_fetch_node(state: Phase2State) -> Dict:
    """
    WIKIPEDIA_FETCH_NODE: Fetches Wikipedia articles using LangChain.
    
    Args:
        state: Current Phase2State
    
    Returns:
        Dictionary of state updates
    """
    print("\n" + "="*70)
    print("📚 WIKIPEDIA_FETCH_NODE: Fetching articles (LangChain)...")
    print("="*70)
    
    queries = state.get("research_queries", [])
    
    if not queries:
        print("\n⚠️  No queries to fetch!")
        return {
            "current_step": "wikipedia_fetch_skipped",
            "errors": ["No research queries available"]
        }
    
    print(f"\n📊 Total queries: {len(queries)}")
    print(f"📄 Results per query: 3 (top Wikipedia matches)")
    
    try:
        successful, failed = fetch_all_articles(queries, top_k=3)
        
        all_articles = []
        for result in successful:
            for article in result.get("articles", []):
                article["source_query"] = result["query"]
                all_articles.append(article)
        
        print("\n" + "─"*70)
        print("FETCH RESULTS:")
        print("─"*70)
        print(f"✅ Successful queries: {len(successful)}/{len(queries)}")
        print(f"❌ Failed queries: {len(failed)}/{len(queries)}")
        print(f"📚 Total articles retrieved: {len(all_articles)}")
        
        if failed:
            print(f"\n⚠️  Failed queries:")
            for query in failed[:5]:
                print(f"   • {query}")
            if len(failed) > 5:
                print(f"   ... and {len(failed) - 5} more")
        
        if all_articles:
            print(f"\n✓ Sample articles:")
            for article in all_articles[:5]:
                print(f"   • {article['title']}")
            if len(all_articles) > 5:
                print(f"   ... and {len(all_articles) - 5} more")
        
        total_chars = sum(len(a.get("summary", "")) for a in all_articles)
        print(f"\n📊 Total content: {total_chars:,} characters")
        
        updates = {
            "wikipedia_articles": all_articles,
            "fetch_success_count": len(all_articles),
            "fetch_failed_queries": failed,
            "current_step": "wikipedia_fetch_complete"
        }
        
        print(f"\n✅ Wikipedia fetch complete")
        print("="*70 + "\n")
        
        return updates
        
    except Exception as e:
        print(f"\n❌ WIKIPEDIA_FETCH_NODE failed: {str(e)}\n")
        
        return {
            "current_step": "wikipedia_fetch_failed",
            "errors": [f"Wikipedia fetch failed: {str(e)}"]
        }