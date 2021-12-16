import json
import os
import re
from dotenv import load_dotenv
from sqlalchemy import Integer, Column, Boolean, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import traceback

os.system('ls -al')
print('Load ENV file: ' + ('%s/.env' % os.path.dirname(os.path.realpath(__file__))))
load_dotenv('%s/.env' % os.path.dirname(os.path.realpath(__file__)))

COMMAND_START = '/start'
COMMAND_HELP = '/help'
COMMAND_PRICE_MAX = '/pricemax'
COMMAND_ROOMS_MIN = '/roomsmin'
COMMAND_SIZE_MIN = '/sizemin'
COMMAND_LOCATIONS = '/locations'
COMMAND_SHOW_SETTINGS = '/showsettings'

Base = declarative_base()


class SearchRequest(Base):
    __tablename__ = "search_requests"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    active = Column(Boolean)
    price_max = Column(Integer)
    rooms_min = Column(Integer)
    size_min = Column(Integer)

    # TODO: updated_at
    # TODO: locations (zip codes)

    def __repr__(self):
        return """
price max: %s;    
rooms min: %s;  
size min: %s;    
        """ % (self.price_max, self.rooms_min, self.size_min)

    def set_size_min(self, size):
        self.size_min = self._cast_to_int(size)

    def set_price_max(self, price):
        self.price_max = self._cast_to_int(price)

    def set_rooms_min(self, rooms):
        self.rooms_min = self._cast_to_int(rooms)

    @staticmethod
    def _cast_to_int(v):
        if isinstance(v, int):
            return v

        if v is None:
            raise Exception('Value is not set')

        if isinstance(v, str) and not v.isnumeric():
            raise Exception('Value should be a number')

        return int(v)


class PostgreSQLClient:

    def __init__(self, host, port, user, password, database):
        # Base = declarative_base()
        print('### PostgreSQLClient: ')
        print(host, port, user, password, database)

        port = int(port)
        uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri, echo=False)
        # Base.metadata.drop_all(self.engine)
        # Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)

    def find_search_request_by_chat_id(self, chat_id: int):
        try:
            return self \
                .session \
                .query(SearchRequest) \
                .filter(SearchRequest.chat_id == chat_id).one()
        except Exception:
            return None

    def store_search_request(self, search_request: SearchRequest):
        if not search_request.id:
            self.session.add(search_request)
        self.session.commit()


def get_help_text(name: str):
    return """
Hi {name}! 
Use next commands for setting up the bot.  
{command_price_max} int - to set max price.
{command_rooms_min} int - to set min number of rooms. 
{command_size_min} int -  to set min size.
{command_locations} comma-separated-list-of-zip-codes -  to search area.  
{command_show_settings} - to see current setting.  
            """.format(name=name,
                       command_price_max=COMMAND_PRICE_MAX,
                       command_rooms_min=COMMAND_ROOMS_MIN,
                       command_size_min=COMMAND_SIZE_MIN,
                       command_locations=COMMAND_LOCATIONS,
                       command_show_settings=COMMAND_SHOW_SETTINGS)


def extract_command_from_request_text(request_text):
    commands = [COMMAND_START, COMMAND_HELP, COMMAND_PRICE_MAX, COMMAND_ROOMS_MIN, COMMAND_SIZE_MIN, COMMAND_LOCATIONS]
    m = re.match(r"(" + "|".join(commands) + ")(.*)", request_text)

    command = m.group(1)
    args = m.group(2).strip() if len(m.group(2).strip()) else None

    if not command:
        raise Exception('Command not found')

    # args = None
    # if command == COMMAND_LOCATIONS:
    #     args = [int(x.strip()) for x in m.group(1).split(',') if len(x.strip()) > 0]
    #
    # if command in [COMMAND_PRICE_MAX, COMMAND_ROOMS_MIN, COMMAND_SIZE_MIN]:
    #     args = int(m.group(1).strip()))

    return command, args


def get_search_request(chat_id, db_client):
    search_request = db_client.find_search_request_by_chat_id(chat_id)
    if not search_request:
        search_request = SearchRequest(chat_id=chat_id)

    return search_request


def build_response(chat_id, response_text, status_code=200):
    response_body = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': response_text,
        'parse_mode': 'markdown'
    }

    r = {
        "statusCode": status_code,
        "body": json.dumps(response_body),
    }

    print('## Response: ' + str(r))

    return r


def log_parameters(event):
    print('## ENVIRONMENT VARIABLES')
    print(os.environ)
    print('## EVENT')
    print(event)


def handle_request(message):
    request_text = message['text']
    chat_id = message['chat']['id']
    name = message['chat']['first_name']
    command, args = extract_command_from_request_text(request_text)

    if request_text == COMMAND_START or request_text == COMMAND_HELP:
        return build_response(chat_id, get_help_text(name))

    db_client = PostgreSQLClient(
        os.environ.get('POSTGRES_HOST'),
        os.environ.get('POSTGRES_PORT'),
        os.environ.get('POSTGRES_USER'),
        os.environ.get('POSTGRES_PASSWORD'),
        os.environ.get('POSTGRES_DBNAME')
    )
    search_request = get_search_request(chat_id, db_client)

    if command == COMMAND_SIZE_MIN:
        search_request.set_size_min(args)
    if command == COMMAND_ROOMS_MIN:
        search_request.set_rooms_min(args)
    if command == COMMAND_PRICE_MAX:
        search_request.set_price_max(args)

    db_client.store_search_request(search_request)

    response_text = 'Search request: ' + str(search_request)

    return build_response(chat_id, response_text)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    log_parameters(event)

    request_body = json.loads(event['body'])
    message = request_body['message']
    chat_id = None

    try:
        chat_id = int(message['chat']['id'])
        return handle_request(message)
    except Exception as e:
        trace = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print('Exception message: ' + str(e))
        print('Exception trace: ' + trace)
        # TODO: figure out how to return TG correct error status code
        return build_response(chat_id, response_text='Internal error', status_code=200)
