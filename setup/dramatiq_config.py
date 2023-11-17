import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import AsyncIO


def configure_dramatiq(host):
    rabbitmq_broker = RabbitmqBroker(host=host, middleware=[AsyncIO()])
    dramatiq.set_broker(rabbitmq_broker)
