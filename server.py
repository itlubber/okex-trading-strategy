import config
import logging
import tornado.log
import tornado.web
import tornado.ioloop
import tornado.httpserver
from utils.urls import urls
from utils.logger import logger
from api.redis_client import redis_client, eth_lstm_model
from api.r_task_client import r_task_client
from tornado.options import options, parse_command_line


tornado.options.define("port", default=config.port, type=int, help="run server on the given port")


def main():
    formatter = tornado.log.LogFormatter(fmt=config.log_format, datefmt=config.log_date_format, color=True)
    parse_command_line()
    [i.setFormatter(formatter) for i in logging.getLogger().handlers]

    app = tornado.web.Application(urls, **config.settings)

    logger.info(f"tornado httpserver runing, interface address is http://127.0.0.1:{options.port}/")
    http_server = tornado.httpserver.HTTPServer(app)

    # http_server.listen(options.port)

    http_server.bind(options.port)
    http_server.start(config.max_workers)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    r_task_client.start()
    redis_client.start()
    eth_lstm_model.start()
    main()
