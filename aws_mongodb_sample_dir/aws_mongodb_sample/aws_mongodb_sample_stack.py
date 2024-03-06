import random
import string
from typing import Final

from aws_cdk import SecretValue, Stack
from aws_cdk.aws_apigateway import LambdaRestApi, LambdaIntegration, ResourceBase, \
    AuthorizationType, StageOptions, CorsOptions, Cors
from aws_cdk.aws_cognito import UserPool, CognitoDomainOptions, ResourceServerScope, UserPoolResourceServer, AuthFlow, \
    OAuthSettings, OAuthFlows, SignInAliases, OAuthScope
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_secretsmanager import Secret, ISecret
from constructs import Construct


class AwsMongodbSampleStack(Stack):
    ENV_NAME: Final[str] = "dev"
    SECRET_NAME: Final[str] = "ATLAS_URI3"

    def __init__(self, scope: Construct, construct_id: str, atlas_uri: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        secret: Secret = Secret(self,
                                id="Secret",
                                secret_name=self.SECRET_NAME,
                                secret_string_value=SecretValue.unsafe_plain_text(atlas_uri))
        secret_arn: str = secret.secret_arn
        secret_name: str = secret.secret_name

        user_pool: UserPool = UserPool(self, "SampleUserPool",
                                       user_pool_name="mysample-userpool",
                                       sign_in_case_sensitive=False,
                                       sign_in_aliases=SignInAliases(
                                           username=True,
                                           email=True),
                                       self_sign_up_enabled=True)

        random_string: str = str("".join(random.choices(string.ascii_lowercase + string.digits, k=7)))
        domain_prefix: str = "mysample-app" + random_string
        cognito_domain: CognitoDomainOptions = CognitoDomainOptions(domain_prefix=domain_prefix)
        user_pool.add_domain("CognitoDomain", cognito_domain=cognito_domain)

        # noinspection PyTypeChecker
        # cognito_user_pools_authorizer: CognitoUserPoolsAuthorizer = (
        #     CognitoUserPoolsAuthorizer(self,
        #                                id="apiAuthorizer",
        #                                cognito_user_pools=[
        #                                    user_pool]))

        lambda_handler_root: Function = self._create_lambda_function(self,
                                                                     name="ApiHandlerRoot",
                                                                     handler_name="lambda_function_root",
                                                                     secret_name=secret_name)
        lambda_handler_get_todos: Function = self._create_lambda_function(self,
                                                                          name="ApiHandlerGetTodos",
                                                                          handler_name="lambda_function_get_todos",
                                                                          secret_name=secret_name)
        lambda_handler_create_todo: Function = self._create_lambda_function(self,
                                                                            name="ApiHandlerCreateTodo",
                                                                            handler_name="lambda_function_create_todo",
                                                                            secret_name=secret_name)
        lambda_handler_delete_todo: Function = self._create_lambda_function(self,
                                                                            name="ApiHandlerDeleteTodo",
                                                                            handler_name="lambda_function_delete_todo",
                                                                            secret_name=secret_name)

        secret: ISecret = Secret.from_secret_attributes(self, self.SECRET_NAME,
                                                        secret_complete_arn=secret_arn)
        secret.grant_read(grantee=lambda_handler_root)
        secret.grant_read(grantee=lambda_handler_get_todos)
        secret.grant_read(grantee=lambda_handler_create_todo)
        secret.grant_read(grantee=lambda_handler_delete_todo)

        # noinspection PyTypeChecker
        lambda_rest_api: LambdaRestApi = LambdaRestApi(
            self,
            id="ApiGateway",
            handler=lambda_handler_root,
            default_method_options={
                "authorization_type": AuthorizationType.NONE
                # If you want to use the Cognito authorizer:
                # "authorizer": cognito_user_pools_authorizer,
                # "authorization_type": AuthorizationType.COGNITO
            }, proxy=False,
            deploy_options=StageOptions(stage_name=self.ENV_NAME),
            default_cors_preflight_options=CorsOptions(allow_origins=["*"],
                                                       allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH",
                                                                      "DELETE"],
                                                       allow_headers=Cors.DEFAULT_HEADERS)
        )

        # noinspection PyTypeChecker
        lambda_integration_root: LambdaIntegration = LambdaIntegration(lambda_handler_root)
        lambda_rest_api.root.add_method("GET", lambda_integration_root)

        # noinspection PyTypeChecker
        lambda_integration_get_todos: LambdaIntegration = LambdaIntegration(lambda_handler_get_todos)
        # noinspection PyTypeChecker
        lambda_integration_create_todo: LambdaIntegration = LambdaIntegration(lambda_handler_create_todo)
        # noinspection PyTypeChecker
        lambda_integration_delete_todo: LambdaIntegration = LambdaIntegration(lambda_handler_delete_todo)
        todos_resource: ResourceBase = lambda_rest_api.root.add_resource("todos")
        todos_resource.add_method(http_method="GET", integration=lambda_integration_get_todos)
        todos_resource.add_method(http_method="POST", integration=lambda_integration_create_todo)
        todos_resource.add_method(http_method="DELETE", integration=lambda_integration_delete_todo)

        read_only_scope: ResourceServerScope = ResourceServerScope(scope_name="read",
                                                                   scope_description="Read-only access")
        user_server: UserPoolResourceServer = user_pool.add_resource_server(
            id="ResourceServer",
            identifier="users",
            scopes=[read_only_scope])
        client_name: str = self.ENV_NAME + "_Test_AppClient"
        user_pool.add_client(id=client_name,
                             auth_flows=AuthFlow(
                                 user_password=True,
                                 user_srp=True,
                                 admin_user_password=True),
                             o_auth=OAuthSettings(
                                 flows=OAuthFlows(authorization_code_grant=True),
                                 scopes=[OAuthScope.resource_server(user_server, read_only_scope)],
                                 callback_urls=[lambda_rest_api.url])
                             )

    def _create_lambda_function(self, stack, name, handler_name, secret_name) -> Function:
        # noinspection PyTypeChecker
        return Function(
            stack,
            name,
            environment={
                "PYTHONPATH": "dependencies",
                "ENV": self.ENV_NAME,
                "ATLAS_URI": secret_name
            },
            runtime=Runtime.PYTHON_3_11,
            handler=f"{handler_name}.lambda_handler",
            code=Code.from_asset("aws_mongodb_sample"),
        )
