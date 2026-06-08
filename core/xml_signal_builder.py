import xml.etree.ElementTree as ET
import numpy as np


class SignalBuilder:

    def __init__(self):

        self.default_states = {
            "J1": [
                "GGgGgrrrrrGGGgrrrrr",
                "yyyyyrrrrryyyyrrrrr",
                "rrrrrGGgGgrrrrGGgGg",
                "rrrrryyyyyrrrryyyyy"
            ],
            "J2": [
                "rrrGGgGGgGg",
                "rrrGygyyyyy",
                "GGGGrGrrrrr",
                "yyyGryrrrrr"
            ],
            "J3": [
                "GGggrrrrGGG",
                "yyyyrrrrGyy",
                "rrrrGGgGGrr",
                "rrrryyyyGrr"
            ],
            "J4": [
                "rrrGGgGGGg",
                "rrrGygyyyy",
                "GGGGrGrrrr",
                "yyyGryrrrr"
            ],
            "J6": [
                "GgGgrrrrGGG",
                "yyyyrrrrGyy",
                "rrrrGGgGGrr",
                "rrrryyyyGrr"
            ]
        }

    def build_string(self, cycle_dict, ratio_dict, *args):
        return self.build(cycle_dict, ratio_dict)

    def build(self, cycle_dict, ratio_dict):

        root = ET.Element("additional")

        for jid in cycle_dict:

            states = self.default_states.get(jid)

            if states is None:
                raise ValueError(f"❌ No signal states for {jid}")

            tl = ET.SubElement(root, "tlLogic", {
                "id": str(jid),
                "type": "static",
                "programID": "1",
                "offset": "0"
            })

            # ================= SAFE CYCLE =================
            cycle_time = int(np.clip(cycle_dict[jid], 40, 180))

            # ================= RATIOS =================
            ratios = ratio_dict.get(jid, [1.0] * len(states))
            ratios = np.array(ratios, dtype=float).flatten()

            if len(ratios) != len(states):
                ratios = np.resize(ratios, len(states))

            ratios = np.nan_to_num(ratios, nan=1.0)

            # 🔥 Normalize safely
            ratios = np.clip(ratios, 0.05, 1.0)
            ratios = ratios / np.sum(ratios)

            # ================= IDENTIFY GREEN PHASES =================
            is_green = [("G" in s or "g" in s) for s in states]

            # Fixed yellow time
            YELLOW_TIME = 5

            num_yellow = len(states) - sum(is_green)
            total_yellow = num_yellow * YELLOW_TIME

            # Remaining for green
            green_budget = cycle_time - total_yellow

            if green_budget <= 0:
                # ❌ Invalid → fallback safe plan
                green_budget = cycle_time * 0.7

            # ================= ASSIGN DURATIONS =================
            durations = []

            green_ratios = ratios[is_green]
            green_ratios = green_ratios / np.sum(green_ratios)

            g_idx = 0

            for i, state in enumerate(states):

                if is_green[i]:
                    dur = max(5, int(green_ratios[g_idx] * green_budget))
                    g_idx += 1
                else:
                    dur = YELLOW_TIME

                durations.append(dur)

            # ================= FINAL CORRECTION =================
            diff = cycle_time - sum(durations)

            # distribute diff safely
            i = 0
            while diff != 0:
                if diff > 0:
                    durations[i % len(durations)] += 1
                    diff -= 1
                else:
                    if durations[i % len(durations)] > 5:
                        durations[i % len(durations)] -= 1
                        diff += 1
                i += 1

            # ================= BUILD XML =================
            for i in range(len(states)):
                ET.SubElement(tl, "phase", {
                    "duration": str(int(durations[i])),
                    "state": states[i]
                })

        return ET.tostring(root, encoding="unicode")