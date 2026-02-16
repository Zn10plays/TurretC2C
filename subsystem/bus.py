import asyncio
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, topic, callback):
        self.subscribers[topic].append(callback)

    async def publish(self, topic, data):
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                asyncio.create_task(callback(data))
