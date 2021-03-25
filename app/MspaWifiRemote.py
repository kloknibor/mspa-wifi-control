import select
from .UartHelper import UartConnection
from .WebComponent import WebComponent
from .MqttComp import MqttClass
import uasyncio as asyncio


class Main():
    def __init__(self):
        self.uart_status = {}
        self.uart_interface = UartConnection()
        self.web = WebComponent()
        self.mqtt = MqttClass()

    async def loop(self):
        n = 0
        self.mqtt.start_connection()
        # get UART data
        while True:
            uart_connection_task = asyncio.create_task(self.uart_interface.check_uart())
            mqtt_publish_task = asyncio.create_task(self.mqtt.main(n))
            #mqtt_result = await mqtt_publish_task
            current_uart_state = await uart_connection_task
            print(current_uart_state)
            #print(mqtt_result)
            n += 1
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
