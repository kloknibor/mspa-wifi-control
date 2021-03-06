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

        # current jacuzzi states
        self.jacuzzi_current_temp = 0
        self.jacuzzi_filter_state_str = ""

        # Current remote states
        self.remote_bubbel_state_on = False
        self.remote_heater_state_on = False
        self.remote_filter_state_on = False
        self.remote_temp = 0

        # States to send to jacuzzi
        self.send_bubble_state_on = False
        self.send_heater_state_on = False
        self.send_filter_state_on = False
        self.send_set_temp = 0

        # init UART
        self.uart1_jacuzzi = UART(1, baudrate=9600, tx=23, rx=19, bits=8, stop=1, parity=None)
        self.uart2_remote = UART(2, baudrate=9600, tx=18, rx=5, bits=8, stop=1, parity=None)

    async def check_uart(self):
        if self.uart2_remote.any():
            remote_buffer = self.uart2_remote.readline()
            self.process_message(remote_buffer, "remote")
            #print(remote_buffer)
            #self.uart1_jacuzzi.write(bytearray(remote_buffer))

        if self.uart1_jacuzzi.any():
            jacuzzi_buffer = self.uart1_jacuzzi.readline()
            self.process_message(jacuzzi_buffer, "jacuzzi")
            self.uart2_remote.write(bytearray(jacuzzi_buffer))
            #print(jacuzzi_buffer)
        
        status = self.return_status()
        return status

    async def write_uart(self, command, state):
        if command == "bubble":
            if state == "on":
                await self.set_bubbel_on()
            elif state == "off":
                await self.set_bubbel_off()
        elif command == "heater":
            if state == "on":
                await self.set_heather_on()
            elif state == "off":
                await self.set_heather_off()
        elif command == "filter":
            if state == "on":
                await self.set_filter_on()
            elif state == "off":
                await self.set_filter_off()
        elif command == "set_temp":
            await self.set_heating_temp(state)

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

    async def set_bubbel_on(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x03\x01\xa9'))

    async def set_filter_on(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x01\xa8'))

    async def set_heather_on(self):
        pass

    async def set_heather_off(self):
        pass

    async def set_bubbel_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x03\x00\xa8'))

    async def set_filter_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x00\xa7'))


    async def set_heating_temp(self, temp):
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
                  'x0b_message': self.last_message_x0b
                  }
        return status

    def split_message_to_array(self, message):
        message_str = str(message)
        print("message is" + message_str)
        fix_msg = message_str.replace(" ", "\x00")
        print("fix_message is" + fix_msg)
        msg = fix_msg.split("\'")
        main_msg = msg[1]
        bitjes = main_msg.split("\\")
        single_message = []
        messages = []

        i = 1
        x = 0
        while i < len(bitjes):

            single_message.append(bitjes[i])
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
                    hex_val2 = 'r'
                else:
                    hex_val1 = message[0][1:3]
                    hex_val2 = message[1][1:3]
                    #print(hex_val2)
                    hex_val3 = message[2][1:3]
                    hex_val4 = message[3][1:3]
                    try:
                        sum_msg = int(hex_val1, 16) + int(hex_val2, 16) + int(hex_val3, 16)
                        check_msg = int(hex_val4, 16)
                    except ValueError:
                        #fixing missing vars for temp on certain temps
                        if message[1] == 'x06':
                            print("calculating temp from control nr")
                            temp = int(hex_val4, 16) - int(hex_val2, 16) - int(hex_val1, 16)
                            hex_val3 = hex(temp)
                        else:
                            print("failed to process message, message was : " + str(message))
                        sum_msg=1
                        check_msg=1

                # verify if message is complete
                if sum_msg == check_msg or hex_val2 == "06":
                    if hex_val2 == "01":
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
                    elif hex_val2 == "02":
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
                    elif hex_val2 == "03":
                        #if self.last_message_x03 != message:
                            self.last_message_x03 = message
                            if message[2] == "x00":
                                print(" Bubbels zijn uit " + str(message) + str(sender))
                                self.remote_bubbel_state_on = False
                            elif message[2] == "x01":
                                self.remote_bubbel_state_on = True
                                print(" Bubbels zijn aan " + str(message) + str(sender))
                            else:
                                print(" unkown bubbel state " + str(message) + str(sender))
                    elif hex_val2 == "04":
                        #if self.last_message_x04 != message:
                            self.last_message_x04 = message
                            temp_val = message[2].replace('x', '')
                            # maximum setting seems to be 31! Bug in Remote? Lie in specs?
                            print(
                                "The temprature on remote is set to : " + str(int(temp_val, 16)) + "   " + str(
                                    message) + str(sender))
                            self.remote_temp = int(temp_val, 16)
                    elif hex_val2 == "05":
                        #if self.last_message_x05 != message:
                            self.last_message_x05 = message
                            print("still unkown message : " + str(message) + str(sender))
                    # temp van jacuzzi x06
                    elif hex_val2 == "06":
                        #if self.last_message_x06 != message:
                            self.last_message_x06 = message
                            temp_jac = ((int(hex_val3, 16)) * 10) / 2
                            print(str(message))
                            print("The jacuzzi temp is : " + str(temp_jac) + " devide by 10 " + str(sender))
                            self.jacuzzi_current_temp = temp_jac
                    elif hex_val2 == "07":
                        #if self.last_message_x07 != message:
                            self.last_message_x07 = message
                            print("still unkown message (bit = x07): " + str(message) + str(sender))
                    elif hex_val2 == "08":
                        #if self.last_message_x08 != message:
                            self.last_message_x08 = message
                            if message[2] == "x00":
                                print(" Filter is uit vanaf jacuzzi " + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filtering off in jacuzzi"
                            elif message[2] == "x03":
                                print(" Filter is zonder error aan vanaf jacuzzi " + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filtering on, no errors"
                            else:
                                print(" unkown filter state " + str(message) + str(sender))
                                self.jacuzzi_filter_state_str = "Filter in unkown state"
                    elif message[1] == "r":
                        #if self.last_message_r != message:
                            self.last_message_r = message
                            print("still unkown message (bit = r): " + str(message) + str(sender))

                    elif hex_val2 == "0b":
                        #if self.last_message_x0b != message:
                            self.last_message_x0b = message
                            print("still unkown message (bit = x0b): " + str(message) + str(sender))

                    else:
                        print("still unkown message : " + str(message) + str(sender))
                        print("bit 2 was:" + message[1])
                else:
                    print("verify failed, mesages wrong " + str(message) + str(sender))

