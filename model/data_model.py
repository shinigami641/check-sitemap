from thirdparty.external_service import call_external_service
from utils.response_helper import format_response

def process_data(data):
    """
    Process data with business logic
    
    Args:
        data (dict): Input data to process
        
    Returns:
        dict: Processed data result
    """
    try:
        # Call external service if needed
        external_result = call_external_service(data)
        
        # Process the data
        processed_data = {
            "input": data,
            "processed": True,
            "external_data": external_result,
            "timestamp": "2023-01-01T00:00:00Z"  # In real app, use actual timestamp
        }
        
        # Format the response
        return format_response(processed_data, success=True)
    except Exception as e:
        return format_response({"error": str(e)}, success=False)