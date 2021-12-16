# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import Session
# import SearchRequest
#
#
# class PostgreSQLClient:
#
#     def __init__(self, host, port, user, password, database):
#         Base = declarative_base()
#         port = int(port)
#         uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
#         self.engine = create_engine(uri, echo=False)
#         # Base.metadata.drop_all(self.engine)
#         # Base.metadata.create_all(self.engine)
#         self.session = Session(bind=self.engine)
#
#     def find_search_request_by_chat_id(self, chat_id: int):
#         return self.session.query(SearchRequest).filter(SearchRequest.chat_id == chat_id).one()
#
#     def store_search_request(self, search_request: SearchRequest):
#         if not search_request.id:
#             self.session.add(search_request)
#         self.session.commit()
