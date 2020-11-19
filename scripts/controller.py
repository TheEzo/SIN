import traci
from typing import Optional


YELLOW_LEN = 3


class Controller:
    def __init__(self, all_tl):
        self.step = 0
        self.q = {id_: {} for id_ in range(10000)}
        self.tls = set(all_tl)

    def inc_step(self):
        self.step += 1

    def queue(self, tl_id: str, phase: int):
        """
        queue phase for traffic light
        - skip if already queued
        - sets another possible queue for current parameters (skipped if not registered later)
        - register yellow phase before this queue
        """

        # handle placeholder
        queued = self._get_queued(tl_id)
        available_time = self._get_available_time(tl_id, phase, queued)
        if available_time is not None:
            # set yellow for phase before
            self.q[available_time - 3].update({tl_id: {'yellow': True}})
            # set phase start
            self.q[available_time].update({tl_id: {'tl': tl_id, 'phase': phase}})
            # set next available placeholder
            cycle_len = sum(p.duration for p in traci.trafficlight.getAllProgramLogics(tl_id)[0].phases)
            self.q[available_time + cycle_len].update({tl_id: {'tl': tl_id, 'phase': phase, 'placeholder': True}})

    def run(self):
        """Run all queued items for current step"""
        processed = []
        for tl, val in self.q[self.step].items():
            processed.append(tl)
            if val.get('yellow'):
                current_phase = traci.trafficlight.getPhase(tl)
                traci.trafficlight.setPhase(tl, current_phase + 1)
            elif val.get('placeholder'):
                if traci.trafficlight.getPhase(tl) == 0:
                    processed.remove(tl)
            else:
                traci.trafficlight.setPhase(val['tl'], val['phase'])
            # TODO pokud zluta, tak naplanovat fazi 0?
        del self.q[self.step]

        # Keep phase 1 running if nothing queued
        for tl in self.tls.difference(processed):
            if traci.trafficlight.getPhase(tl) == 0:
                traci.trafficlight.setPhase(tl, 0)
        # TODO traci.trafficlight.getNextSwitch(tl) == 1? check and plan 0

        self.inc_step()

    def _get_queued(self, tl):
        """
        Get queue records for traffic light
        """
        i = 0
        ret = {}
        for step, data in self.q.items():
            if data:
                if tl in data:
                    ret[step] = data[tl]

            # no need to iterate all future steps
            i += 1
            if i > 150:
                break

        return ret

    def _get_available_time(self, tl, phase, tl_queue) -> Optional[int]:
        """
        Retrieve step where requested cycle can be planned
        Remove placeholders from queue if any
        Return time with +3 for yellow phase or None if current params already planned
        """

        def plan_with_another_phases(tl, phase, tl_queue, start, placeholder=False):
            phase_len = traci.trafficlight.getAllProgramLogics(tl)[0].phases[phase].duration + YELLOW_LEN

            # plan phase after last planned phase
            last_time_to_check = None
            for time, val in tl_queue.items():
                if 'tl' in val and 'phase' in val and 'placeholder' not in val:
                    last_time_to_check = time

            if last_time_to_check is None:
                return start
            else:
                check_val = tl_queue[last_time_to_check]
                check_phase_len = self._get_tl_phase_duration(tl, check_val['phase']) + YELLOW_LEN

                # check if proposed end of current phase fits else plan after this phase
                if traci.trafficlight.getPhase(tl) == 0:
                    if not placeholder:
                        return last_time_to_check + check_phase_len
                    return 0
                else:
                    if placeholder:
                        check_time = last_time_to_check + check_phase_len
                        # plan after already planned phase
                        if check_time >= start:
                            return check_time
                        # else phase 0 must be executed first
                        # todo test faze 0 se spusti
                        return check_time + self._get_tl_phase_duration(tl, 0)
                    return 0  # TODO naplanovat za posledni fazi (cas faze + zluta)

        # params already planned
        if next((v for v in tl_queue.values()
                 if v.get('tl', -1) == tl and v.get('phase', -1) == phase and 'placeholder' not in v), False):
            return None

        # placeholder
        placeholder = next(({k: v} for k, v in tl_queue.items()
                            if v.get('tl', -1) == tl and v.get('phase', -1) == phase and 'placeholder' in v), False)
        if placeholder:
            return plan_with_another_phases(tl, phase, tl_queue, next(k for k in placeholder), True)

        # future plan available - try to plan right after current phase
        return plan_with_another_phases(tl, phase, tl_queue, int(traci.trafficlight.getNextSwitch(tl)) + YELLOW_LEN)

    @staticmethod
    def _get_tl_phase_duration(tl, phase) -> int:
        return int(traci.trafficlight.getAllProgramLogics(tl)[0].phases[phase].duration)
