#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

import urllib.parse

from invenio_notify import constants

def get_recid_by_record_url(url, app=None):
    """Extract record ID from URL.
    
    Args:
        url (str): URL containing record ID
        
    Returns:
        str: Record ID extracted from URL
    """
    if not url:
        return None

    if app is None:
        from flask import current_app
        app = current_app

    re_url_record_id = app.config.get(constants.NOTIFY_RECORD_ID_URL_REGEX)
    re_url_record_id_alt = app.config.get(constants.NOTIFY_RECORD_ID_ALT_URL_REGEX)

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
