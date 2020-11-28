import traci
from sumolib import checkBinary
from paho.mqtt.client import Client
from time import sleep

STEPS = 3600


def get_bitmap():
    def detector_status(det):
        return traci.inductionloop.getLastStepVehicleNumber(det) > 0

    result = 0b0000

    if detector_status('01') or detector_status('02'):
        result |= 0b0001

    if detector_status('11') or detector_status('12'):
        result |= 0b0010

    if detector_status('21') or detector_status('22'):
        result |= 0b0100

    if detector_status('31') or detector_status('32'):
        result |= 0b1000

    return result


def run(client):
    for _ in range(STEPS):
        bitmap = get_bitmap()
        client.publish('input', str(bitmap))
        sleep(0.01)
        client.loop(timeout=5)
        traci.simulationStep()
    traci.close()


def on_connect(client, userdata, flags, rc):
    client.subscribe('output')


def on_message(client, userdata, msg):
    traci.trafficlight.setPhase('1', msg.payload)


if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')
    traci.start([sumoBinary, "-c", "sin.sumocfg"])

    mqtt = Client()
    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.connect('localhost', port=1883)
    run(mqtt)
