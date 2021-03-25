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
        self.config['ssid'] = secrets.WIFI_SSID
        self.config['wifi_pw'] = secrets.WIFI_PASSWORD

        print(" connect coro : ")
        print(self.config['connect_coro'])

        print(self.config)

        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self.client = MQTTClient(self.config)

    @staticmethod
    async def conn_han(client):
        await client.subscribe('foo_topic', 1)

    def set_state(self, topic, msg, retained):
        print("topic : " + str(topic) + " message ; " + str(msg) + " retained : " + str(retained))

    def publish_states(self, states):
        await self.client.publish('x05_message', '{}'.format(states['x05_message']), qos = 1)
        await self.client.publish('x0b_message', '{}'.format(states['x0b_message']), qos=1)
        await self.client.publish('heater_state_on', '{}'.format(states['heater_state_on']), qos=1)
        await self.client.publish('x07_message', '{}'.format(states['x07_message']), qos=1)
        await self.client.publish('remote_temp', '{}'.format(states['remote_temp']), qos=1)
        await self.client.publish('filter_state_on', '{}'.format(states['filter_state_on']), qos=1)
        await self.client.publish('bubbel_state_on', '{}'.format(states['bubbel_state_on']), qos=1)
        await self.client.publish('jacuzzi_current_temp', '{}'.format(states['jacuzzi_current_temp']), qos=1)
        await self.client.publish('r_message', '{}'.format(states['r_message']), qos=1)


    def close_connection(self):
        self.client.close()

    async def start_connection(self):
        await self.client.connect()



