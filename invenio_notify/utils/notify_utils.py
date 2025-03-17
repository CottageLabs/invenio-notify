import regex
import urllib.parse

re_url_record_id = regex.compile(r'/records/(.*?)$')
re_url_record_id_alt = regex.compile(r'/records/([^/]+)/?')

def get_recid_by_record_url(url):
    """Extract record ID from URL.
    
    Args:
        url (str): URL containing record ID
        
    Returns:
        str: Record ID extracted from URL
    """
    if not url:
        return None
        
    # Parse URL to handle any URL encoding
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    
    # Try first regex pattern
    match = re_url_record_id.search(path)
    if match:
        return match.group(1)
    
    # Try alternate regex pattern
    match = re_url_record_id_alt.search(path)
    if match:
        return match.group(1)
    
    return None
