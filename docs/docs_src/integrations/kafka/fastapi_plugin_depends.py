from fastapi import FastAPI, Depends
from propan import KafkaBroker
from propan.fastapi import KafkaRouter
from typing_extensions import Annotated

app = FastAPI()

router = KafkaRouter("localhost:9092")

def broker():
    return router.broker

@router.get("/")
async def hello_http(broker: Annotated[KafkaBroker, Depends(broker)]):
    await broker.publish("Hello, Kafka!", "test")
    return "Hello, HTTP!"

app.include_router(router)