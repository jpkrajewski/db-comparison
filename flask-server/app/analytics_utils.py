from datetime import datetime as dt

def create_search_data_document(keywords: str) -> dict:
   return {
        'action': 'search',
        'keywords_count': len(keywords),
        'keywords_items': keywords,
        'searched_at': dt.now()
    }