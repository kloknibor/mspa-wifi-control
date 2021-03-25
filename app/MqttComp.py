from .mqtt_as import MQTTClient, config
import uasyncio as asyncio
import app.secrets as secrets

class MqttClass():
    def __init__(self):
        self.config = config
        self.config['subs_cb'] =  self.set_state
        self.config['connect_coro'] = self.conn_han
        self.config['server'] = secrets.MQTT_SERVER
        self.config['user'] = secrets.MQTT_USERNAME
        self.config['password'] = secrets.MQTT_PASSWORD
        self.config['ssid'] = secrets.WIFI_SSID
        self.config['wifi_pw'] = secrets.WIFI_PASSWORD

        # retaining old value to not overflood mqtt
        self.mspajacuzzi_state_old = ""
        self.mspajacuzzi_jacuzzi_current_temp_old = 0
        self.mspajacuzzi_x05_message_old = ""
        self.mspajacuzzi_x0b_message_old = ""
        self.remote_heater_state_on_old = ""
        self.mspajacuzzi_x07_message_old = ""
        self.remote_filter_state_on_old = ""
        self.remote_bubbel_state_on_old = ""
        self.mspajacuzzi_r_message_old = ""
        self.mspajacuzzi_remote_temp_old = 0

        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self.client = MQTTClient(self.config)

    @staticmethod
    async def conn_han(client):
        await client.subscribe('foo_topic', 1)

    def set_state(self, topic, msg, retained):
        print("topic1 : " + str(topic) + " message ; " + str(msg) + " retained : " + str(retained))

    async def publish_states(self, states):
        if not states == self.mspajacuzzi_state_old:
            await self.client.publish('mspajacuzzi/state', '{}'.format(states), qos=1)
            self.mspajacuzzi_state_old = states
        if not states['remote_temp'] == self.mspajacuzzi_remote_temp_old:
            await self.client.publish('mspajacuzzi/remote_temp','{}'.format(states['remote_temp']), qos=1)
            self.mspajacuzzi_remote_temp_old = states['remote_temp']
        if not states['jacuzzi_current_temp'] == self.mspajacuzzi_jacuzzi_current_temp_old:
            await self.client.publish('mspajacuzzi/jacuzzi_current_temp','{}'.format(states['jacuzzi_current_temp']), qos=1)
            self.mspajacuzzi_jacuzzi_current_temp_old = states['jacuzzi_current_temp']
        if not states['x05_message'] == self.mspajacuzzi_x05_message_old:
            await self.client.publish('mspajacuzzi/x05_message', '{}'.format(states['x05_message']), qos = 1)
            self.mspajacuzzi_x05_message_old = states['x05_message']
        if not states['x0b_message'] == self.mspajacuzzi_x0b_message_old:
            await self.client.publish('mspajacuzzi/x0b_message', '{}'.format(states['x0b_message']), qos=1)
            self.mspajacuzzi_x0b_message_old = states['x0b_message']
        if not states['remote_heater_state_on'] == self.remote_heater_state_on_old:
            await self.client.publish('mspajacuzzi/remote_heater_state_on', '{}'.format(states['remote_heater_state_on']), qos=1)
            self.remote_heater_state_on_old = states['remote_heater_state_on']
        if not states['x07_message'] == self.mspajacuzzi_x07_message_old:
            await self.client.publish('mspajacuzzi/x07_message', '{}'.format(states['x07_message']), qos=1)
            self.mspajacuzzi_x07_message_old = states['x07_message']
        if not states['remote_filter_state_on'] == self.remote_filter_state_on_old:
            await self.client.publish('mspajacuzzi/remote_filter_state_on', '{}'.format(states['remote_filter_state_on']), qos=1)
            self.remote_filter_state_on_old = states['remote_filter_state_on']
        if not states['remote_bubbel_state_on'] == self.remote_bubbel_state_on_old:
            await self.client.publish('mspajacuzzi/remote_bubbel_state_on', '{}'.format(states['remote_bubbel_state_on']), qos=1)
            self.remote_bubbel_state_on_old = states['remote_bubbel_state_on']
        if not states['r_message'] == self.mspajacuzzi_r_message_old:
            await self.client.publish('mspajacuzzi/r_message', '{}'.format(states['r_message']), qos=1)
            self.mspajacuzzi_r_message_old = states['r_message']

    def close_connection(self):
        self.client.close()

    async def start_connection(self):
        await self.client.connect()



