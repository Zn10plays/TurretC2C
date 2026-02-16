import asyncio
import moteus
import cv2
from ultralytics import YOLO

model = None
def load_model():
    return model if model else model := YOLO('yolo26n.pt')

async def main():
    c1 = moteus.Controller(id=1)
    c2 = moteus.Controller(id=2)

    model = load_model()

    cam = cv2.VideoCapture(0)

    
    # ...

if __name__ == '__main__':
    asyncio.run(main())