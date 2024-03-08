import json
from typing import Optional, Awaitable
from tornado.web import RequestHandler
from utils.logger import logger


class BaseHandler(RequestHandler):
    json_args = {}

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def options(self):
        self.set_status(204)
        self.finish()