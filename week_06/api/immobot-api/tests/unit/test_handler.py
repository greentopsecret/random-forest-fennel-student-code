import json

import pytest

from hello_world import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {'resource': '/hello', 'path': '/hello/', 'httpMethod': 'POST',
            'headers': {'Accept-Encoding': 'gzip, deflate', 'CloudFront-Forwarded-Proto': 'https',
                        'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false',
                        'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false',
                        'CloudFront-Viewer-Country': 'NL', 'Content-Type': 'application/json',
                        'Host': 'mcdmlrzoqe.execute-api.eu-west-1.amazonaws.com', 'User-Agent': 'Amazon CloudFront',
                        'Via': '1.1 aeb457e87760dc433cf50cdb15399112.cloudfront.net (CloudFront)',
                        'X-Amz-Cf-Id': 'degFTf8TxqWeQDrC2FJErR8l_x78bEkcYNaP3JC7okmh5YSfniKmmg==',
                        'X-Amzn-Trace-Id': 'Root=1-61bb0966-77e500c602932b0d2f8496f7',
                        'X-Forwarded-For': '91.108.6.53, 64.252.186.142', 'X-Forwarded-Port': '443',
                        'X-Forwarded-Proto': 'https'},
            'multiValueHeaders': {'Accept-Encoding': ['gzip, deflate'], 'CloudFront-Forwarded-Proto': ['https'],
                                  'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'],
                                  'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'],
                                  'CloudFront-Viewer-Country': ['NL'], 'Content-Type': ['application/json'],
                                  'Host': ['mcdmlrzoqe.execute-api.eu-west-1.amazonaws.com'],
                                  'User-Agent': ['Amazon CloudFront'],
                                  'Via': ['1.1 aeb457e87760dc433cf50cdb15399112.cloudfront.net (CloudFront)'],
                                  'X-Amz-Cf-Id': ['degFTf8TxqWeQDrC2FJErR8l_x78bEkcYNaP3JC7okmh5YSfniKmmg=='],
                                  'X-Amzn-Trace-Id': ['Root=1-61bb0966-77e500c602932b0d2f8496f7'],
                                  'X-Forwarded-For': ['91.108.6.53, 64.252.186.142'], 'X-Forwarded-Port': ['443'],
                                  'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None,
            'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None,
            'requestContext': {'resourceId': 'f56o9w', 'resourcePath': '/hello', 'httpMethod': 'POST',
                               'extendedRequestId': 'Kb5oGEgPDoEF6ig=', 'requestTime': '16/Dec/2021:09:39:50 +0000',
                               'path': '/Prod/hello/', 'accountId': '536200232045', 'protocol': 'HTTP/1.1',
                               'stage': 'Prod', 'domainPrefix': 'mcdmlrzoqe', 'requestTimeEpoch': 1639647590855,
                               'requestId': '80c0f097-a120-48b1-b3a1-951f5aaac6c3',
                               'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None,
                                            'caller': None, 'sourceIp': '91.108.6.53', 'principalOrgId': None,
                                            'accessKey': None, 'cognitoAuthenticationType': None,
                                            'cognitoAuthenticationProvider': None, 'userArn': None,
                                            'userAgent': 'Amazon CloudFront', 'user': None},
                               'domainName': 'mcdmlrzoqe.execute-api.eu-west-1.amazonaws.com', 'apiId': 'mcdmlrzoqe'},
            'body': '{"update_id":326508551,\n"message":{"message_id":3832,"from":{"id":398074162,"is_bot":false,"first_name":"Maxim","username":"greentopsecret","language_code":"en"},"chat":{"id":398074162,"first_name":"Maxim","username":"greentopsecret","type":"private"},"date":1639647590,"text":"/pricemax 5","entities":[{"offset":0,"length":9,"type":"bot_command"}]}}',
            'isBase64Encoded': False}


def test_lambda_handler(apigw_event):
    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"


def test_extract_command_from_request_text():
    assert app.extract_command_from_request_text('/start') == ('/start', None)
    assert app.extract_command_from_request_text('/help') == ('/help', None)
    assert app.extract_command_from_request_text('/size_min 65') == ('/size_min', '65')
    assert app.extract_command_from_request_text('/price_max 1500') == ('/price_max', '1500')
    assert app.extract_command_from_request_text('/rooms_min 2') == ('/rooms_min', '2')
    assert app.extract_command_from_request_text('/rooms_min') == ('/rooms_min', None)
    assert app.extract_command_from_request_text('/locations 12345,23456,34567') == ('/locations', '12345,23456,34567')
