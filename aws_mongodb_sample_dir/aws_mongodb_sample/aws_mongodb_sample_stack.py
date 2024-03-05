import random
import string

from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_lambda as _lambda,
    aws_secretsmanager as secretsmanager,
    SecretValue as SecretValue,
    aws_apigateway as apigateway
)
from constructs import Construct


class AwsMongodbSampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, atlas_uri: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = "dev"
        secretname = "ATLAS_URI3"

        secret = secretsmanager.Secret(self, "Secret", secret_name=secretname,
                                       secret_string_value=SecretValue.unsafe_plain_text(atlas_uri))
        secret_arn = secret.secret_arn
        secret_name = secret.secret_name

        user_pool = cognito.UserPool(self, "SampleUserPool",
                                     user_pool_name="mysample-userpool",
                                     sign_in_case_sensitive=False,
                                     sign_in_aliases=cognito.SignInAliases(
                                         username=True,
                                         email=True),
                                     self_sign_up_enabled=True
                                     )

        random_string = str("".join(random.choices(string.ascii_lowercase + string.digits, k=7)))
        domain_prefix = "mysample-app" + random_string
        cognito_domain = cognito.CognitoDomainOptions(domain_prefix=domain_prefix)
        user_pool.add_domain("CognitoDomain", cognito_domain=cognito_domain)

        # noinspection PyTypeChecker
        cognito_user_pools_authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "apiAuthorizer",
            cognito_user_pools=[user_pool])

        def create_lambda_function(stack, name, handler_name):
            # noinspection PyTypeChecker
            return _lambda.Function(
                stack,
                name,
                environment={
                    "PYTHONPATH": "dependencies",
                    "ENV": env_name,
                    "ATLAS_URI": secret_name
                },
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler=f"{handler_name}.lambda_handler",
                code=_lambda.Code.from_asset("aws_mongodb_sample"),
            )

        # Usage:
        lambda_handler_root = create_lambda_function(self, "ApiHandlerRoot", "lambda_function_root")
        lambda_handler_get_todos = create_lambda_function(self, "ApiHandlerGetTodos", "lambda_function_get_todos")
        lambda_handler_create_todo = create_lambda_function(self, "ApiHandlerCreateTodo", "lambda_function_create_todo")
        lambda_handler_delete_todo = create_lambda_function(self, "ApiHandlerDeleteTodo", "lambda_function_delete_todo")

        secret = secretsmanager.Secret.from_secret_attributes(self, secretname, secret_complete_arn=secret_arn)
        secret.grant_read(grantee=lambda_handler_root)
        secret.grant_read(grantee=lambda_handler_get_todos)
        secret.grant_read(grantee=lambda_handler_create_todo)
        secret.grant_read(grantee=lambda_handler_delete_todo)

        # noinspection PyTypeChecker
        lambda_rest_api = apigateway.LambdaRestApi(
            self,
            "ApiGateway",
            handler=lambda_handler_root,
            default_method_options={
                "authorizer": cognito_user_pools_authorizer,
                "authorization_type": apigateway.AuthorizationType.COGNITO
            },
            deploy_options=apigateway.StageOptions(stage_name=env_name),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            ),
            proxy=False
        )

        todos_resource = lambda_rest_api.root.add_resource("todos")

        # noinspection PyTypeChecker
        lambda_integration_get_todos = apigateway.LambdaIntegration(lambda_handler_get_todos)
        # noinspection PyTypeChecker
        lambda_integration_create_todo = apigateway.LambdaIntegration(lambda_handler_create_todo)
        # noinspection PyTypeChecker
        lambda_integration_delete_todo = apigateway.LambdaIntegration(lambda_handler_delete_todo)

        todos_resource.add_method("GET", integration=lambda_integration_get_todos)
        todos_resource.add_method("POST", integration=lambda_integration_create_todo)
        todos_resource.add_method("DELETE", integration=lambda_integration_delete_todo)

        read_only_scope = cognito.ResourceServerScope(scope_name="read", scope_description="Read-only access")
        user_server = user_pool.add_resource_server("ResourceServer", identifier="users", scopes=[read_only_scope])
        client_name = env_name + "_Test_AppClient"
        user_pool.add_client(client_name,
                             auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
                             o_auth=cognito.OAuthSettings(
                                 flows=cognito.OAuthFlows(authorization_code_grant=True),
                                 scopes=[cognito.OAuthScope.resource_server(user_server, read_only_scope)],
                                 callback_urls=[lambda_rest_api.url])
                             )
