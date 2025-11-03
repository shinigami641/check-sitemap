def call_external_service(data):
    """
    Call external service or API
    
    Args:
        data (dict): Data to send to external service
        
    Returns:
        dict: Response from external service
    """
    # In a real application, this would make an actual API call
    # For now, we'll just simulate a response
    
    return {
        "external_id": "ext-12345",
        "status": "success",
        "processed_at": "2023-01-01T00:00:00Z"
    }