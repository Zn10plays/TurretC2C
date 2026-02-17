import asyncio
from subsystem.bus import EventBus
from subsystem.motors import MotorsSubsystem
from subsystem.vision import VisionSubsystem
from subsystem.ai import AiAnnotateSubsystem
from subsystem.logger import LoggerSubsystem
from concurrent.futures import ProcessPoolExecutor

async def main():
    bus = EventBus()

    # for CPU heavy tasks    
    process_pool = ProcessPoolExecutor(max_workers=2)


    subsystems = [
        MotorsSubsystem(bus),
        VisionSubsystem(bus),
        AiAnnotateSubsystem(bus, process_pool),
        LoggerSubsystem(bus)
    ]

    tasks = [asyncio.create_task(s.start()) for s in subsystems]

    await asyncio.gather(*tasks)
    
if __name__ == '__main__':
    asyncio.run(main())