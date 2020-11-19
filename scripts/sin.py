import traci
from sumolib import checkBinary

from scripts.controller import Controller


def run():
    """execute the TraCI control loop"""
    step = 0

    c = Controller(['2'])

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        c.run()

        # check 3 route junction detectors
        for jun in ['14', '2']:
            # detector id, phase to run, for simplification detector 1 executes phase 2 and d2 - p4
            for det, phase in [(1, 2), (2, 4)]:
                if traci.inductionloop.getLastStepVehicleNumber(f'd{jun}_{det}') > 0:
                    # TODO planuju jen kdyz neni zelena a next phase je za vic nez N sekund
                    c.queue(jun, phase)


        step += 1
    traci.close()


if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "sin.sumocfg"])
    run()
