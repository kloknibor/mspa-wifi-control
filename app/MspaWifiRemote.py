import select
from .UartHelper import UartConnection
from .WebComponent import WebComponent
from .MqttComp import MqttClass, config
import uasyncio as asyncio


class Main():
    def __init__(self):
        self.uart_status = {}
        self.uart_interface = UartConnection()
        self.web = WebComponent()
        self.mqtt = MqttClass()

    async def loop(self):
        await self.mqtt.start_connection()
        print("connected")
        # get UART data
        while True:
            uart_connection_task = asyncio.create_task(self.uart_interface.check_uart())
            current_uart_state = await uart_connection_task
            asyncio.create_task(self.mqtt.publish_states(states=current_uart_state))

            await asyncio.sleep(1)




        # self.uart_interface.check_uart()
        # self.uart_status = self.uart_interface.return_status()
        # print(self.uart_status)

        # Create MQTT component
        # mqtt = MqttClass()
        #
        # try:
        #     asyncio.run(mqtt.main())
        # finally:
        #     mqtt.close_connection()  # Prevent LmacRxBlk:1 errors
