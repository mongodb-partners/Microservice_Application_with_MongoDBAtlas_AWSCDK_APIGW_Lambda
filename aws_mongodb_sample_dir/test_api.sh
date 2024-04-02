#!/bin/bash

latest_user_pool_id=$(aws cognito-idp list-user-pools --max-results 60 | jq -r '.UserPools | sort_by(.CreationDate) | last | .Id')
echo "Latest user pool id: >>>${latest_user_pool_id}<<<"

if [ -z "$latest_user_pool_id" ]; then
    echo "No user pool found."
    exit 1
fi

app_client_id=$(aws cognito-idp list-user-pool-clients --user-pool-id "$latest_user_pool_id" | jq -r '.UserPoolClients | .[0] | .ClientId')
echo "App id for app in user pool: >>>${app_client_id}<<<"

if [ -z "$app_client_id" ]; then
    echo "No App Client found for the user pool."
    exit 1
fi

stack_name="AwsMongodbSampleStack"
api_id=$(aws apigateway get-rest-apis | jq -r --arg stack_name "$stack_name" '.items[] | select(.tags."aws:cloudformation:stack-name" == $stack_name) | .id' | head -n 1)
echo "API id for the latest API Gateway: >>>${api_id}<<<"

if [ -z "$api_id" ]; then
    echo "No API Gateway found for stack $stack_name"
    exit 1
fi

api_url="https://${api_id}.execute-api.us-east-1.amazonaws.com/dev/"
echo "URL for the GET method in the API Gateway: ${api_url}"

if [ -z "$api_url" ]; then
    echo "API Gateway URL for 'dev' stage not found."
    exit 1
fi

aws cognito-idp admin-create-user --user-pool-id  "$latest_user_pool_id"  --username apigwtest

aws cognito-idp admin-set-user-password --user-pool-id "$latest_user_pool_id"  --username apigwtest  --password SuperSafePassword42! --permanent

auth_response=$(aws cognito-idp admin-initiate-auth --user-pool-id "$latest_user_pool_id" --client-id "$app_client_id" --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME=apigwtest,PASSWORD=SuperSafePassword42!)
id_token=$(echo "$auth_response" | jq -r '.AuthenticationResult.IdToken')
echo "Id token: >>>${id_token}<<<"

# Create a todo
create_todo_response=$(curl --location --request POST "${api_url}todos" \
--header 'Content-Type: application/json' \
--header "Authorization: ${id_token}" \
--data-raw '{
    "text": "TODO text"
}'):x
echo "Create todo response: >>>${create_todo_response}<<<"

# Get todos
get_todos_response=$(curl --location --request GET "${api_url}todos" \
--header 'Content-Type: application/json' \
--header "Authorization: ${id_token}")
echo "Get todos response: >>>${get_todos_response}<<<"

# Extract the todo id from the create todo response
todo_id=$(echo "$create_todo_response" | jq -r '.id')

# Delete the todo
delete_todo_response=$(curl --location --request DELETE "${api_url}todos" \
--header 'Content-Type: application/json' \
--header "Authorization: ${id_token}" \
--data-raw '{
    "id": "'"${todo_id}"'"
}')
echo "Delete todo response: >>>${delete_todo_response}<<<"
