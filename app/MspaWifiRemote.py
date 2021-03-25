import select
from .UartHelper import UartConnection
from .WebComponent import WebComponent
from MqttComponent import MqttClass
import uasyncio as asyncio
import secrets


class Main():
    def __init__(self):
        self.uart_status = {}
        self.uart_interface = UartConnection()
        self.web = WebComponent()
        self.mqtt = MqttClass

        self.config = {'subs_cb': self.mqtt.set_state,
                       'connect_coro': self.mqtt.conn_han,
                       'server': secrets.MQTT_SERVER,
                       'user': secrets.MQTT_USERNAME,
                       'password': secrets.MQTT_PASSWORD}

    async def loop(self):

        # get UART data
        while True:
            uart_connection_task = asyncio.create_task(self.uart_interface.check_uart())
            current_uart_state = await uart_connection_task
            print(current_uart_state)
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
