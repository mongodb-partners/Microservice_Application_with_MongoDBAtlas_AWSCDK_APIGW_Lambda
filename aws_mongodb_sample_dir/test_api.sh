#!/bin/bash

latest_user_pool_id=$(aws cognito-idp list-user-pools --max-results 60 | jq -r '.UserPools | sort_by(.CreationDate) | last | .Id')
echo "Latest user pool id: >>>${latest_user_pool_id}<<<"

if [ -z "$latest_user_pool_id" ]; then
    echo "No user pool found."
    exit 1
fi

app_client_id=$(aws cognito-idp list-user-pool-clients --user-pool-id "$latest_user_pool_id" | jq -r '.UserPoolClients | .[0] | .ClientId')
echo "app id for app in user pool: >>>${app_client_id}<<<"

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

curl --location --request GET "${api_url}" --header 'Content-Type: application/json' --header "Authorization: ${id_token}"


curl --location --request GET https://2p4ymsbiog.execute-api.us-east-1.amazonaws.com/dev/ --header 'Content-Type: application/json' --header "Authorization: eyJraWQiOiIwYm8ydGFaZGJhTlhLbEpIQVZTRyszQURrb1JmYVFTazlNOFwvcGx0cEpxTT0iLCJhbGciOiJSUzI1NiJ9.eyJvcmlnaW5fanRpIjoiYzk2Y2FiMjQtZTUxNy00ODE0LTk5MWUtMTE5NmY5NDA4NjJlIiwic3ViIjoiYTJkNTdmMTktMzZlZS00OGUzLWI0ZjctNjYzZDk4YmJkMTBjIiwiYXVkIjoia3RlNGM3bHN2aXZ1YmVudDlmanBzNmUwbCIsImV2ZW50X2lkIjoiMmNkNjJlZTItZDQyZi00NmIxLWIyNjEtNjIzNTJlNTc3YjVmIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MDk2MjE5MjksImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX3U4eXB2V3pqNCIsImNvZ25pdG86dXNlcm5hbWUiOiJhcGlnd3Rlc3QiLCJleHAiOjE3MDk2MjU1MjksImlhdCI6MTcwOTYyMTkyOSwianRpIjoiYWRmNzcwMWMtOTZjMS00N2ZlLWFmYWMtYTQxOTA3MDMzMmFmIn0.c6X3UR4whObzGvSmkWpdRv4jJqiqto8vqQ-COxp0JZcZ3x82nea-vegqwZPDqTXxASG3PUi1ppC1bLZNzKyl5Ts0J8E5ONHYVsggiI1njEOFGbiu-jpXHevCsVdb1qaAVa5Om0AMoe5Njp8ja9CRhIco3b8bzLdLFv2DimFaqXUiyOBnbLNearI7TSSdVAxlB1BJA3XCnrRId1L3hjpxpsCqkDAvceGiWhimeJ5omLCVZ9hPu7kyBoT81JoRv3RK05kdTiFuYhdbiZv5-rgH6JRN0wx_hhhHvjHwU-oflIco-BQBGi32Tb4PRZxG-5gT9HW26vIiwDX7gBLNkxYz8A"