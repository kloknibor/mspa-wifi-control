import select
from .UartHelper import UartConnection
from .MqttComp import MqttClass, config
import uasyncio as asyncio


class Main():
    def __init__(self):
        self.uart_interface = UartConnection()
        self.mqtt = MqttClass()

    async def loop(self):
        await self.mqtt.start_connection()
        # get UART data
        while True:
            uart_connection_task = asyncio.create_task(self.uart_interface.check_uart())
            current_uart_state = await uart_connection_task
            asyncio.create_task(self.mqtt.publish_states(states=current_uart_state))

            await asyncio.sleep(1)


