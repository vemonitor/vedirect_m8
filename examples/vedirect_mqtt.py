#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import paho.mqtt.client as mqtt
from vedirect_m8.vedirect import Vedirect


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    parser.add_argument('--mqttbroker', help='MQTT broker address', type=str, default='test.mosquitto.org')
    parser.add_argument('--mqttbrokerport', help='MQTT broker port', type=int, default='1883')
    parser.add_argument('--topicprefix', help='MQTT topic prefix', type=str, default='vedirect/')
    args = parser.parse_args()

    conf = {
        "serial_port": args.port,
        "timeout": args.timeout
    }

    ve = Vedirect(serial_conf=conf)

    client = mqtt.Client()
    client.connect(args.mqttbroker, args.mqttbrokerport, 60)
    client.loop_start()

    def mqtt_send_callback(packet):
        for key, value in packet.items():
            if key != 'SER#':  # topic cannot contain MQTT wildcards
                client.publish(args.topicprefix + key, value)

    ve.read_data_callback(mqtt_send_callback)
