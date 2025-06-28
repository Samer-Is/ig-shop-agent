import azure.functions as func

app = func.FunctionApp()

@app.function_name("test")
@app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS)
def test(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello World from Azure Functions!") 