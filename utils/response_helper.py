def format_response(data, success=True):
    """
    Format API response
    
    Args:
        data (dict): Data to include in response
        success (bool): Whether the request was successful
        
    Returns:
        dict: Formatted API response
    """
    return {
        "success": success,
        "data": data,
        "meta": {
            "version": "1.0.0"
        }
    }