from mqtt_as import MQTTClient
import uasyncio as asyncio
import secrets

class MqttClass():
    def __init__(self):
        self.config = {'subs_cb': self.set_state(),
                       'connect_coro': self.conn_han(),
                       'server': secrets.MQTT_SERVER,
                       'user': secrets.MQTT_USERNAME,
                       'password': secrets.MQTT_PASSWORD}
        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self.client = MQTTClient(self.config)

    async def conn_han(self):
        await self.client.subscribe('foo_topic', 1)

    def set_state(self):
        pass

    def publish_states(self):
        pass

    def close_connection(self):
        self.client.close()

    async def main(self):
        await self.client.connect()
