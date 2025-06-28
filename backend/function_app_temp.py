import azure.functions as func
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the main Function App
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health endpoint accessed successfully')
    
    response_data = {
        "status": "healthy",
        "message": "IG-Shop-Agent API is running",
        "test": "minimal deployment working"
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    ) 