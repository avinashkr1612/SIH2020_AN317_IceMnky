from lambda_function import lambda_handler
import json




event = json.load(open('lambda-payloads.json', 'r'))

lambda_handler(event, {})