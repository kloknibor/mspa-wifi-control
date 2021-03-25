from machine import UART
import uasyncio as asyncio

class UartConnection():
    def __init__(self):
        # keep track of messages
        self.last_message_x01 = []
        self.last_message_x02 = []
        self.last_message_x03 = []
        self.last_message_x04 = []
        self.last_message_x05 = []
        self.last_message_x06 = []
        self.last_message_x07 = []
        self.last_message_x08 = []
        self.last_message_r = []
        self.last_message_x0b = []

        # current states
        self.jacuzzi_current_temp = 0
        self.remote_bubbel_state_on = False
        self.remote_heater_state_on = False
        self.remote_filter_state_on = False
        self.remote_temp = 0
        self.jacuzzi_filter_state_str = ""

        # init UART
        self.uart1_jacuzzi = UART(1, baudrate=9600, tx=14, rx=4, bits=8, stop=1, parity=None)
        self.uart2_remote = UART(2, baudrate=9600, tx=15, rx=27, bits=8, stop=1, parity=None)

    async def check_uart(self):
        if self.uart2_remote.any():
            remote_buffer = self.uart2_remote.readline()
            self.process_message(remote_buffer, "remote")
            self.uart1_jacuzzi.write(bytearray(remote_buffer))

        if self.uart1_jacuzzi.any():
            jacuzzi_buffer = self.uart1_jacuzzi.readline()
            self.process_message(jacuzzi_buffer, "jacuzzi")
            self.uart2_remote.write(bytearray(jacuzzi_buffer))

        status = self.return_status()
        return status


    def de_init_uart(self):
        self.uart1_jacuzzi.deinit()
        self.uart2_remote.deinit()

    def get_temp(self):
        return self.jacuzzi_current_temp

    def get_heating_temp(self):
        return self.remote_temp

    def get_bubbel_state(self):
        return self.remote_bubbel_state_on

    def get_heater_state(self):
        return self.remote_heater_state_on

    def get_filter_state(self):
        return self.remote_filter_state_on

    def set_bubbel_on(self):
        self.uart2_remote.write(bytearray(b'\xa5\x03\x01\xa9'))
        self.remote_bubbel_state_on = True

    def set_filter_on(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x01\xa8'))
        self.remote_filter_state_on = True

    def set_heather_on(self):
        self.remote_heater_state_on = True

    def set_bubbel_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x03\x00\xa8'))
        self.remote_bubbel_state_on = False

    def set_filter_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x00\xa7'))
        self.remote_filter_state_on = False

    def set_heather_off(self):
        self.remote_heater_state_on = False

    def set_heating_temp(self, temp):
        # temp -> hex
        # Controle nr uitrekenen
        # bytestring van maken
        # sturen : self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x00\xa7'))
        pass

    def return_status(self):
        status = {'remote_heater_state_on': self.remote_heater_state_on,
                  'remote_filter_state_on': self.remote_filter_state_on,
                  'remote_bubbel_state_on': self.remote_bubbel_state_on,
                  'remote_temp': self.remote_temp,
                  'x05_message': self.last_message_x05,
                  'jacuzzi_current_temp': self.jacuzzi_current_temp,
                  'x07_message': self.last_message_x07,
                  'jacuzzi_filter_state_str': self.jacuzzi_filter_state_str,
                  'r_message': self.last_message_r,
                  'x0b_message': self.last_message_x0b}
        return status

    def split_message_to_array(self, message):
        message_str = str(message)
        msg = message_str.split("\'")
        main_msg = msg[1]
        bytes = main_msg.split("\\")

        # check nr of messages
        # print(len(bytes))
        single_message = []
        messages = []

        i = 1
        x = 0
        while i < len(bytes):

            single_message.append(bytes[i])
            x += 1
            i += 1

            if x == 4:
                messages.append(single_message)
                x = 0
                single_message = []

        # print(messages)
        return messages

    def process_message(self, message, sender):
        # split message to usefull array
        messages_array = self.split_message_to_array(message=message)

        for message in messages_array:
            # check message
            if message[0] == 'xa5':
                if message[1] == 'r':
                    sum_msg = 1
                    check_msg = 1
                else:
                    hex_val1 = message[0].replace('x', '')
                    hex_val2 = message[1].replace('x', '')
                    hex_val3 = message[2].replace('x', '')
                    hex_val4 = message[3].replace('x', '')
                    try:
                        sum_msg = int(hex_val1, 16) + int(hex_val2, 16) + int(hex_val3, 16)
                        check_msg = int(hex_val4, 16)
                    except ValueError:
                        print("failed to process message, message was : " + str(message))
                        sum_msg=1
                        check_msg=1

                # verify if message is complete
                if sum_msg == check_msg:
                    if message[1] == "x01":
                        if self.last_message_x01 != message:
                            self.last_message_x01 = message
                            if message[2] == "x00":
                                print(" Heater is uit " + str(message) + str(sender))
                                self.remote_filter_state_on = False
                            elif message[2] == "x01":
                                self.remote_filter_state_on = True
                                print(" Heater is aan" + str(message) + str(sender))
                            else:
                                print(" unkown Heater state " + str(message) + str(sender))
                    # filter aan x02
                    elif message[1] == "x02":
                        if self.last_message_x02 != message:
                            self.last_message_x02 = message
                            if message[2] == "x00":
                                print(" Filter is uit " + str(message) + str(sender))
                                self.remote_filter_state_on = False
                            elif message[2] == "x01":
                                self.remote_filter_state_on = True
                                print(" Filter is aan" + str(message) + str(sender))
                            else:
                                print(" unkown filter state " + str(message) + str(sender))

                    # bubbels aan x03
                    elif message[1] == "x03":
                        if self.last_message_x03 != message:
                            self.last_message_x03 = message
                            if message[2] == "x00":
                                print(" Bubbels zijn uit " + str(sender))
                                self.remote_bubbel_state_on = False
                            elif message[2] == "x01":
                                self.remote_bubbel_state_on = True
                                print(" Bubbels zijn aan" + str(sender))
                            else:
                                print(" unkown bubbel state " + str(message) + str(sender))
                    elif message[1] == "x04":
                        if self.last_message_x04 != message:
                            self.last_message_x04 = message
                            temp_val = message[2].replace('x', '')
                            # maximum setting seems to be 31! Bug in Remote? Lie in specs?
                            print(
                                "The temprature on remote is set to : " + str(int(temp_val, 16)) + "   " + str(
                                    message) + str(sender))
                            self.remote_temp = int(temp_val, 16)
                    elif message[1] == "x05":
                        if self.last_message_x05 != message:
                            self.last_message_x05 = message
                            print("still unkown message : " + str(message) + str(sender))
                    # temp van jacuzzi x06
                    elif message[1] == "x06":
                        if self.last_message_x06 != message:
                            self.last_message_x06 = message
                            temp_hex_jac = message[2].replace('x', '')
                            temp_jac = ((int(temp_hex_jac, 16)) * 10) / 2
                            print("The jacuzzi temp is : " + str(temp_jac) + " devide by 10 " + str(sender))
                            self.jacuzzi_current_temp = temp_jac
                    elif message[1] == "x07":
                        if self.last_message_x07 != message:
                            self.last_message_x07 = message
                            print("still unkown message (bit = x07): " + str(message) + str(sender))
                    elif message[1] == "x08":
                        if self.last_message_x08 != message:
                            self.last_message_x08 = message
                            if message[2] == "x00":
                                print(" Filter is uit vanaf jacuzzi" + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filtering off in jacuzzi"
                            elif message[2] == "x03":
                                print(" Filter is zonder error aan vanaf jacuzzi" + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filtering on, no errors"
                            else:
                                print(" unkown filter state " + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filter in unkown state"
                    elif message[1] == "r":
                        if self.last_message_r != message:
                            self.last_message_r = message
                            print("still unkown message (bit = r): " + str(message) + str(sender))

                    elif message[1] == "x0b":
                        if self.last_message_x0b != message:
                            self.last_message_x0b = message
                            print("still unkown message (bit = x0b): " + str(message) + str(sender))

                    else:
                        print("still unkown message : " + str(message) + str(sender))
                        print("bit 2 was:" + message[1])
                else:
                    print("verify failed, mesages wrong " + str(message) + str(sender))
