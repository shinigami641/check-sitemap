from model.data_model import process_data

def process_request(payload):
    """
    Process incoming request payload
    
    Args:
        payload (dict): The request payload
        
    Returns:
        dict: Processed response
    """
    # Validate payload
    if not payload:
        return {"error": "Empty payload"}
    
    # Process data using model
    result = process_data(payload)
    
    return result