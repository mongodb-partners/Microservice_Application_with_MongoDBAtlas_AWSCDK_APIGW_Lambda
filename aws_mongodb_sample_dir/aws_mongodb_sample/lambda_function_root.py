def lambda_handler(event, context):
    response = {
        "statusCode": 200,
        "body": "Welcome to the API! This is the root endpoint.",
        "headers": {"Content-Type": "text/plain"}
    }
    return response
