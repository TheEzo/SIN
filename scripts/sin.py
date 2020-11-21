import traci
from sumolib import checkBinary

from scripts.controller import Controller

STEPS = 3600


def run():
    """execute the TraCI control loop"""

    def queue(junction, phase):
        """add record to queue if phase is not already running and have more than 5 steps until end"""
        if traci.trafficlight.getPhase(junction) == phase and traci.trafficlight.getNextSwitch(junction) > 5:
            return

        c.queue(jun, phase)

    step = 0

    jun_3_route = ['14', '2',  '63']
    jun_4_route = ['12', '591']
    all_junctions = jun_3_route + jun_4_route
    c = Controller(all_junctions)

    while step < STEPS:
        traci.simulationStep()
        c.run()

        # check 3 route junction detectors
        for jun in jun_3_route:
            # (detector id, phase to run), for simplification detector 1 executes phase 2 and d2 - p4
            for det, phase in [(1, 2), (2, 4)]:
                if traci.inductionloop.getLastStepVehicleNumber(f'd{jun}_{det}') > 0:
                    queue(jun, phase)

        # check 4 route junction detectors
        for jun in jun_4_route:
            # (detector id, phase to run), similar as in first loop
            for det, phase in [(1, 2), (2, 4), (3, 6), (4, 2), (5, 4), (6, 6)]:
                if traci.inductionloop.getLastStepVehicleNumber(f'd{jun}_{det}') > 0:
                    queue(jun, phase)

        step += 1
    traci.close()


if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "sin.sumocfg"])
    run()
