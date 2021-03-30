import select
from .UartHelper import UartConnection
from .MqttComp import MqttClass
import uasyncio as asyncio

class Main():
    def __init__(self):
        self.uart_interface = UartConnection()
        self.mqtt = MqttClass()

        # Remote states
        self.last_heater_state_on_remote = False
        self.last_filter_state_on_remote = False
        self.last_bubble_state_on_remote = False
        self.last_set_heater_temp_remote = 0

        # Web states
        self.last_heater_state_on_web = False
        self.last_filter_state_on_web = False
        self.last_bubble_state_on_web = False
        self.last_set_heater_temp_web = 0

        # Mqtt states
        self.last_heater_state_on_mqtt = False
        self.last_filter_state_on_mqtt = False
        self.last_bubble_state_on_mqtt = False
        self.last_set_heater_temp_mqtt = 0

        # Current send state
        self.last_heater_state_on_current = False
        self.last_filter_state_on_current = False
        self.last_bubble_state_on_current = False
        self.last_set_heater_temp_current = 0
        self.current_states = {}

    async def loop(self):
        await self.mqtt.start_connection()
        # get UART data
        while True:
            # gather all info from classes
            uart_connection_task = asyncio.create_task(self.uart_interface.check_uart())
            current_uart_state = await uart_connection_task
            current_states = current_uart_state.copy()
            current_states['current_heater_state_on'] = self.last_heater_state_on_current
            current_states['current_filter_state_on'] = self.last_filter_state_on_current
            current_states['current_bubbel_state_on'] = self.last_bubble_state_on_current
            current_states['current_remote_temp'] = self.last_set_heater_temp_current
            asyncio.create_task(self.mqtt.publish_states(states=current_states))

            # Check remote
            if self.last_heater_state_on_remote != current_uart_state['remote_heater_state_on']:
                self.last_heater_state_on_current = current_uart_state['remote_heater_state_on']
                self.last_heater_state_on_remote = current_uart_state['remote_heater_state_on']
                if current_uart_state['remote_heater_state_on']:
                    await self.uart_interface.set_heather_on()
                else:
                    await self.uart_interface.set_heather_off()

            if self.last_filter_state_on_remote != current_uart_state['remote_filter_state_on']:
                self.last_filter_state_on_current = current_uart_state['remote_filter_state_on']
                self.last_filter_state_on_remote = current_uart_state['remote_filter_state_on']
                if current_uart_state['remote_filter_state_on']:
                    await self.uart_interface.set_filter_on()
                else:
                    await self.uart_interface.set_filter_off()

            if self.last_bubble_state_on_remote != current_uart_state['remote_bubbel_state_on']:
                self.last_bubble_state_on_current = current_uart_state['remote_bubbel_state_on']
                self.last_bubble_state_on_remote = current_uart_state['remote_bubbel_state_on']
                if current_uart_state['remote_bubbel_state_on']:
                    await self.uart_interface.set_bubbel_on()
                else:
                    await self.uart_interface.set_bubbel_off()

            # Check Mqtt
            if self.last_heater_state_on_mqtt != self.mqtt.set_state_heater_on:
                self.last_heater_state_on_current = self.mqtt.set_state_heater_on
                self.last_heater_state_on_remote = self.mqtt.set_state_heater_on
                if self.mqtt.set_state_heater_on:
                    await self.uart_interface.set_heather_on()
                else:
                    await self.uart_interface.set_heather_off()

            if self.last_filter_state_on_mqtt != self.mqtt.set_state_filter_on:
                self.last_filter_state_on_current = self.mqtt.set_state_filter_on
                self.last_filter_state_on_mqtt = self.mqtt.set_state_filter_on
                if self.mqtt.set_state_filter_on:
                    await self.uart_interface.set_filter_on()
                else:
                    await self.uart_interface.set_filter_off()

            if self.last_bubble_state_on_mqtt != self.mqtt.set_state_bubble_on:
                self.last_bubble_state_on_current = self.mqtt.set_state_bubble_on
                self.last_bubble_state_on_mqtt = self.mqtt.set_state_bubble_on
                if self.last_bubble_state_on_mqtt:
                    await self.uart_interface.set_bubbel_on()
                else:
                    await self.uart_interface.set_bubbel_off()


            print(self.last_heater_state_on_current)
            print(self.last_filter_state_on_current)
            print(self.last_bubble_state_on_current)
            print(self.last_set_heater_temp_current)
            await asyncio.sleep(1)


