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
        led = data['led']
        vibrate = data['vibrate']
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

    def signed_addressed_publish(self, topic, addr, payload):
        signed_topic = self.sign_topic(topic)
        addressed_topic = self.address_topic(signed_topic, addr)
        self.publish(addressed_topic, payload)

    def _publish_sys(self, level, payload=""):
        topic = ClientConnection.level_sys_topic(level)
        signed_topic = self.sign_topic(topic)
        self.publish(signed_topic, payload)

    def sign_topic(self, topic):
        parts = topic.split('+')
        parts.insert(1, self._client_id)
        return ''.join(parts)

    def address_topic(self, topic, addr):
        parts = topic.split('+')
        parts.insert(-1, addr)
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

    @staticmethod
    def addressed_payload(addr, payload=None):
        if payload:
            if type(payload) == dict:
                payload['addr'] = addr
            else:
                payload = {"addr": addr, "data": payload}
        else:
            payload = {"addr": addr}

        payload = ClientConnection.data_encode(payload)

        return payload

    @staticmethod
    def payload_addressed(payload):
        payload = ClientConnection.data_decode(payload)
        if type(payload) == dict:
            if "addr" in payload.keys():
                return payload["addr"]
            return False
        return False


class GestureServer(ClientConnection):
    def __init__(self, config, debug=False):
        super(GestureServer, self).__init__(config, debug)

        self._client_profiles = []

        self._client_responders = []

        self._client_response_window = 1

        self._selected_profile_index = 0

        self._t_pingreq_start = timeit.default_timer()

    def on_message(self, client, obj, msg, topic, identity):
        self.debug(msg, topic.top, topic.sig, topic.pattern, identity)
        if topic.pattern == TOPICS.SYS.values:
            self.debug('sys message')
            if topic.top == SYS_LEVELS.PINGRESP.value and not identity:
                self.debug('ping response')
                if _h.elapsed(self._t_pingreq_start) <= self._client_response_window:
                    profile_data = ClientConnection.data_decode(msg.payload, is_json=True)
                    profile = Profile(profile_data)
                    self.debug('adding profile', profile)
                    self._client_responders.append(tuple([topic.sig, profile]))

    def on_connect(self, client, userdata, flags, rc):
        self.ping_collect_clients()

    def on_disconnect(self, userdata, rc):
        pass

    def _profile_exists(self, uuid):
        return _h.check_key(dict(self._client_profiles), uuid)

    def add_client_profile(self, uuid, profile):
        if not self._profile_exists(uuid):
            self._client_profiles.append(tuple([uuid, profile]))
            return True
        return False

    def sub_manager_profile(self, uuid):
        if self._profile_exists(uuid):
            self._client_profiles.remove(uuid)
            return True
        return False

    def client_profile(self, uuid):
        return dict(self._client_profiles).pop(uuid)

    def _mov_profile_index(self, dir):
        min = 0
        max = len(self._client_profiles)
        self._selected_profile_index += dir
        if self._selected_profile_index >= max:
            self._selected_profile_index = max
        if self._selected_profile_index <= min:
            self._selected_profile_index = min
        return self._selected_profile_index

    def profiles(self):
        return list(dict(self._client_profiles).values())

    def next_profile(self):
        index = self._mov_profile_index(+1)
        return self.profiles()[index]

    def prev_profile(self):
        index = self._mov_profile_index(-1)
        return self.profiles()[index]

    def ping_collect_clients(self):
        self._client_profiles = self._client_responders
        self._client_responders = []
        self._t_pingreq_start = timeit.default_timer()
        self._publish_sys(SYS_LEVELS.PINGREQ.value)


class GestureClient(ClientConnection):
    def __init__(self, config, debug=False):
        super(GestureClient, self).__init__(config, debug)

        self.profile_data = config['profile']

        self._t_up_start = None

        self.on_spell = lambda gesture, spell: None
        self.on_quaternion = lambda x, y, z, w: None

    def on_connect(self, client, userdata, flags, rc):
        self._t_up_start = timeit.default_timer()

        self._publish_sys(
            SYS_LEVELS.PINGRESP.value,
            ClientConnection.data_encode(self.profile_data)
        )

    def on_disconnect(self, userdata, rc):
        pass

    def on_message(self, client, obj, msg, topic, identity):
        addressed = self.identity(topic.top)

        if topic.pattern == TOPICS.SYS.value:
            if topic.top == SYS_LEVELS.PINGREQ.value and not identity:
                self._publish_sys(
                    SYS_LEVELS.PINGRESP.value,
                    ClientConnection.data_encode(self.profile_data)
                )

        if topic.pattern == TOPICS.SPELLS.value and addressed:
            if callable(self.on_spell):
                data = ClientConnection.data_decode(msg.payload, is_json=True)
                self.on_spell(
                    data['gesture'], data['spell']
                )

        if topic.pattern == TOPICS.QUATERNIONS.value and addressed:
            if callable(self.on_quaternion):
                data = ClientConnection.data_decode(msg.payload, is_json=True)['data'].split(" ")
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