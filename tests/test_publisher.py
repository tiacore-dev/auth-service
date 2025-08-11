class NullPublisher:
    async def connect(self) -> None:
        pass

    async def publish(self, *args, **kwargs) -> None:
        pass

    async def close(self) -> None:
        pass

    async def publish_event(self, *args, **kwargs) -> None:
        pass
