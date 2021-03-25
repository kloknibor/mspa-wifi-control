from .mqtt_as import MQTTClient, config
import uasyncio as asyncio
import app.secrets as secrets



class MqttClass():
    def __init__(self):
        self.config = config
        print(self.config)
        self.config['subs_cb'] =  self.set_state
        self.config['connect_coro'] = self.conn_han
        self.config['server'] = secrets.MQTT_SERVER
        self.config['user'] = secrets.MQTT_USERNAME
        self.config['password'] = secrets.MQTT_PASSWORD

        print(self.config)

        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self.client = MQTTClient(self.config)


    async def conn_han(self):
        await self.client.subscribe('foo_topic', 1)

    def set_state(self, topic, msg, retained):
        print("topic : " + topic + " message ; " + msg + " retained : " + retained)

    def publish_states(self, topic, msg, retained):
        print("topic : " + topic + " message ; " + msg + " retained : " + retained)

    def close_connection(self):
        self.client.close()

    def start_connection(self):
        await self.client.connect()

    async def main(self, n):
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await self.client.publish('result', '{}'.format(n), qos = 1)
        n += 1
        return "published info"
