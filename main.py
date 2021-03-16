import time, machine, network, gc, threading, app.secrets as secrets
from machine import UART

def connectToWifiAndUpdate():
    time.sleep(1)
    print('Memory free', gc.mem_free())

    from app.ota_updater import OTAUpdater

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    otaUpdater = OTAUpdater('https://github.com/kloknibor/mspa-wifi-control', main_dir='app', secrets_file="secrets.py")
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()

def startApp():
    event = threading.Event()
    # uart1 = Jacuzzi
    uart1 = UART(1, baudrate=2400, tx=4, rx=14)
    # uart2 = remote
    uart2 = UART(2, baudrate=2400, tx=15, rx=27)
    while True:
        print("uart1")
        print(uart1.read())
        print("uart2")
        print(uart2.read())
        event.wait(0.75)
        
connectToWifiAndUpdate()
startApp()
