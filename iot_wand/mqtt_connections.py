import iot_wand.helpers as _h
import paho.mqtt.client as mqtt
from enum import Enum
import paho.mqtt.publish as publish
import uuid
import json
import os
import posixpath
import timeit
import time
import asyncio


class TOPICS(Enum):
    SYS = 'iot_wand/+/$SYS/+'
    SPELLS = 'iot_wand/+/spells/+'
    QUATERNIONS = 'iot_wand/+/quaternions/+'


class SYS_LEVELS(Enum):
    SYN = "SYN"
    SYN_ACK = "SYN-ACK"
    ACK = "ACK"
    PINGREQ = "PINGREQ"
    PINGRESP = "PINGRESP"
    UP = "UP"
    DOWN = "DOWN"
    STATUS = "STATUS"


class CONN_STATUS(Enum):
    CONNECTED = 1
    DISCONNECTED = 0


class Topic():
    def __init__(self, topic):
        self.top = ClientConnection.topic_level(topic)
        self.sig = ClientConnection.topic_level(topic, 1)
        self.pattern = ClientConnection.topic_pattern(topic)


class Profile():
    def __init__(self, data):
        self._profile = data['profile']
        led = self._profile['led']
        vibrate = self._profile['vibrate']
        self.uuid = data['uuid']
        self.led_on = led['on']
        self.led_color = led['color']
        self.vibrate_on = vibrate['on']
        self.vibrate_pattern = vibrate['pattern']


class ClientConnection():
    def __init__(self, config, debug=False):
        self._debug = debug
        self._client_id = str(uuid.uuid4())
        self._mqttc = mqtt.Client(client_id=self._client_id)

        self.config = config

        broker_config = config['broker']

        self.hostname = broker_config['hostname']
        self.port = broker_config['port']
        self.keepalive = broker_config['keepalive']
        self.bind_address = broker_config['bind_address']

        self._mqttc.on_connect = self.__on_connect
        self._mqttc.on_message = self.__on_message
        self._mqttc.on_publish = self.__on_publish
        self._mqttc.on_subscribe = self.__on_subscribe
        self._mqttc.on_disconnect = self.__on_disconnect
        self._mqttc.on_log = self.__on_log

        self._t_conn_last = None
        self._t_msg_last = None
        self._async = False
        self.status_broker_conn = CONN_STATUS.DISCONNECTED.value

    def __on_connect(self, client, userdata, flags, rc):
        self.status_broker_conn = CONN_STATUS.CONNECTED.value
        self._t_conn_last = _h.now()
        self.debug('broker connection established @ %s:%s' % (self.hostname, self.port))
        self._mqttc.subscribe(TOPICS.SYS.value, 0)
        self._mqttc.subscribe(TOPICS.SPELLS.value, 0)
        self._mqttc.subscribe(TOPICS.QUATERNIONS.value, 0)

        self.on_connect(client, userdata, flags, rc)

    def on_connect(self, client, userdata, flags, rc):
        pass

    def __on_message(self, client, obj, msg):
        topic = Topic(msg.topic)

        identity = self.identity(topic.sig)

        #self.debug(topic.pattern, topic.top, msg.payload, identity)

        self.on_message(client, obj, msg, topic, identity)

    def on_message(self, client, obj, msg, topic, identity):
        pass

    def __on_publish(self, client, obj, mid):
        #self.debug('published', mid)
        self.on_publish(client, obj, mid)

    def on_publish(self, client, obj, mid):
        pass

    def __on_subscribe(self, client, obj, mid, granted_qos):
        self.debug('subscribed', mid, granted_qos)
        self.on_subscribe(client, obj, mid, granted_qos)

    def on_subscribe(self, client, obj, mid, granted_qos):
        pass

    def __on_disconnect(self, userdata, rc):
        self.status = CONN_STATUS.DISCONNECTED.value
        self.debug('disconnected', rc)
        self.on_disconnect(userdata, rc)

    def on_disconnect(self, userdata, rc):
        pass

    def __on_log(self, client, obj, level, string):
        #self.debug('log', level, string)
        self.on_log(client, obj, level, string)

    def on_log(self, client, obj, level, string):
        pass

    def get_client(self):
        return self._mqttc

    def connect(self):
        self._mqttc.connect(self.hostname, self.port, self.keepalive, self.bind_address)

    def disconnect(self):
        self._mqttc.disconnect()
        if self._async:
            self._mqttc.loop_stop()

    def start(self, async=True, async_callback=None):
        self.connect()
        self.loop(async, async_callback)

    def stop(self):
        self.disconnect()

    def loop(self, async=True, async_callback=None):
        if async:
            self._mqttc.loop_start()
            self._async = True
            if callable(async_callback):
                async_callback(self)
            else:
                self.async_callback()
        else:
            self._mqttc.loop_forever()

    def async_callback(self):
        pass

    def publish(self, topic, payload):
        self._mqttc.publish(topic, payload)

    def signed_publish(self, topic, payload):
        signed_topic = self.sign_topic(topic)
        self._mqttc.publish(signed_topic, payload)

    def _publish_sys(self, level, payload=""):
        topic = ClientConnection.level_sys_topic(level)
        signed_topic = self.sign_topic(topic)
        self.publish(signed_topic, payload)

    def sign_topic(self, topic):
        parts = topic.split('+')
        parts.insert(1, self._client_id)
        return ''.join(parts)

    def identity(self, _id):
        if type(_id) == bytes:
            _id = _h.b_decode(_id)
        return _id == self._client_id

    def elapsed_up_time(self, minutes=False):
        if self._t_conn_last:
            t_up = _h.elapsed(self._t_conn_last)
            if minutes:
                return t_up / 60
            return t_up
        return 0

    def elapsed_last_msg(self, minutes=False):
        if self._t_msg_last:
            t_up = _h.elapsed(self._t_msg_last)
            if minutes:
                return t_up / 60
            return t_up
        return 0

    def debug(self, *args, sep=' ', end='\n'):
        if self._debug:
            _args = ("%s:" % self._client_id,) + args
            print(_args, sep, end, file=None)

    @staticmethod
    def data_decode(data, is_json=False):
        if type(data) == bytes:
            data = _h.b_decode(data)
        if is_json:
            return json.loads(data)
        return data

    @staticmethod
    def data_encode(data):
        if type(data) == bytes:
            data = ClientConnection.data_decode(data)
        return json.dumps(data)

    @staticmethod
    def topic_sig(topic):
        return ClientConnection.topic_level(topic, level=1)

    @staticmethod
    def topic_pattern(topic):
        type = topic.split('/')[2]
        for _topic in TOPICS:
            if _topic.value.split('/')[2] == type:
                return _topic.value
        return None

    @staticmethod
    def topic_level(topic, level=-1):
        return topic.split('/')[level]

    @staticmethod
    def level_topic(topic, level):
        return posixpath.join(posixpath.dirname(topic), level)

    @staticmethod
    def level_sys_topic(level):
        return ClientConnection.level_topic(TOPICS.SYS.value, level)


class GestureServer(ClientConnection):
    def __init__(self, config, debug=False):
        super(GestureServer, self).__init__(config, debug)

        self._client_managers = []
        self._selected_manager_index = -1

    def on_message(self, client, obj, msg, topic, identity):
        if topic.pattern == TOPICS.SYS.value:

            if topic.top == SYS_LEVELS.PINGREQ.value and not identity:
                self._publish_sys(SYS_LEVELS.PINGRESP.value)

            if topic.top == SYS_LEVELS.SYN.value and not identity:
                self._publish_sys(SYS_LEVELS.SYN_ACK.value, topic.sig)

            if topic.top == SYS_LEVELS.ACK.value and not identity:
                profile_data = ClientConnection.data_decode(msg.payload, is_json=True)
                profile = Profile(profile_data)
                self.add_manager_profile(profile)

            if topic.top == SYS_LEVELS.STATUS.value and not identity:
                status = ClientConnection.data_decode(msg)
                if status == CONN_STATUS.DISCONNECTED.value:
                    self.sub_manager_profile(topic.sig)


    def on_connect(self, client, userdata, flags, rc):
        self._publish_sys(SYS_LEVELS.PINGRESP.value)

    def on_disconnect(self, userdata, rc):
        pass

    def _manager_exists(self, uuid):
        return _h.check_key(dict(self._client_managers), uuid)

    def add_manager_profile(self, profile):
        if not self._manager_exists(profile.uuid):
            self._client_managers.append(tuple([profile.uuid, profile]))
            return True
        return False

    def sub_manager_profile(self, uuid):
        if self._manager_exists(uuid):
            self._client_managers.remove(uuid)
            return True
        return False

    def manager_profile(self, uuid):
        return dict(self._client_managers).pop(uuid)

    def on_client_manager_connect(self, profile):
        self.add_manager_profile(profile)

    def _mov_manager_index(self, dir):
        min = 0
        max = len(self._client_managers)
        self._selected_manager_index += dir
        if self._selected_manager_index >= max:
            self._selected_manager_index = max
        if self._selected_manager_index <= min:
            self._selected_manager_index = min
        return self._selected_manager_index

    def profiles(self):
        return list(dict(self._client_managers).values())

    def next_profile(self):
        index = self._mov_manager_index(+1)
        return self.profiles()[index]

    def prev_profile(self):
        index = self._mov_manager_index(-1)
        return self.profiles()[index]

    def async_callback(self):
        pass


class GestureClient(ClientConnection):
    def __init__(self, config, debug=True):
        super(GestureClient, self).__init__(config, debug)

        self.profile_data = config['profile']

        self._t_up_start = None
        self.status_server_conn = CONN_STATUS.DISCONNECTED.value
        self.pingresp = 1
        self.poll_delay = 5

        self.on_spell = lambda gesture, spell: None
        self.on_quaternion = lambda x, y, z, w: None

    def on_connect(self, client, userdata, flags, rc):
        self._publish_sys(SYS_LEVELS.SYN.value)

    def on_disconnect(self, userdata, rc):
        self._publish_sys(SYS_LEVELS.STATUS.value, ClientConnection.data_encode(CONN_STATUS.DISCONNECTED.value))

    def on_message(self, client, obj, msg, topic, identity):
        if topic.pattern == TOPICS.SYS.value:
            addressed = self.identity(msg.payload)

            if topic.top == SYS_LEVELS.SYN_ACK.value and addressed:
                self._publish_sys(
                    SYS_LEVELS.ACK.value,
                    ClientConnection.data_encode({
                        'uuid': self._client_id,
                        'profile': self.profile_data
                    })
                )

                self.status_server_conn = CONN_STATUS.CONNECTED.value

            if topic.top == SYS_LEVELS.PINGRESP.value:
                self.pingresp = True

            if topic.top == SYS_LEVELS.UP.value and addressed:
                pass

            if topic.top == SYS_LEVELS.DOWN.value and addressed:
                pass

        if topic.pattern == TOPICS.SPELLS.value and not identity:
            if callable(self.on_spell):
                data = ClientConnection.data_decode(msg.payload, is_json=True)
                self.on_spell(
                    data['gesture'], data['spell']
                )

        if topic.pattern == TOPICS.QUATERNIONS.value and not identity:
            if callable(self.on_quaternion):
                data = ClientConnection.data_decode(msg.payload, is_json=True).split(" ")
                self.on_quaternion(
                    data[0], data[1], data[2], data[3]
                )

    def elapsed_up_start(self, minutes=False):
        if self._t_up_start:
            t_up = _h.elapsed(self._t_up_start)
            if minutes:
                return t_up / 60
            return t_up
        return 0

    def async_callback(self):
        run = True
        try:
            while run:
                time.sleep(self.poll_delay)

                if self.status_server_conn == CONN_STATUS.DISCONNECTED.value:
                    self._publish_sys(SYS_LEVELS.SYN.value)

                elif self.status_server_conn == CONN_STATUS.CONNECTED.value:
                    if self.pingresp:
                        self.pingresp = False
                        self._publish_sys(SYS_LEVELS.PINGREQ.value)
                    else:
                        self.status_server_conn = CONN_STATUS.DISCONNECTED.value

        except (KeyboardInterrupt, Exception) as e:
            self.disconnect()
