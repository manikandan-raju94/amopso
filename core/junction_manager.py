import numpy as np
import sys
import os

# SUMO tools
SUMO_HOME = "/usr/share/sumo"
tools = os.path.join(SUMO_HOME, "tools")

if tools not in sys.path:
    sys.path.append(tools)

import sumolib


class JunctionManager:

    def __init__(self, net_file):
        self.net_file = net_file

        net = sumolib.net.readNet(net_file)

        # ✅ GET ONLY TRAFFIC LIGHT IDS
        self.junction_ids = sorted([tls.getID() for tls in net.getTrafficLights()])

        print("✅ USING TLS IDS:", self.junction_ids)

        # ✅ REQUIRED (THIS FIXES YOUR ERROR)
        self.phases_per_junction = 4

        self.num_junctions = len(self.junction_ids)

    # =====================================================
    def get_junction_ids(self):
        return self.junction_ids

    def get_genome_length(self):
        return self.num_junctions * (1 + self.phases_per_junction)

    def get_all_phase_counts(self):
        return {jid: self.phases_per_junction for jid in self.junction_ids}

    # =====================================================
    def decode_genome(self, genome):

        cycle_dict = {}
        ratio_dict = {}
        offset_dict = {}

        idx = 0

        for jid in self.junction_ids:

            # -------- cycle --------
            cycle_raw = genome[idx]
            idx += 1

            cycle_time = int(60 + cycle_raw * 60)
            cycle_time = max(40, min(180, cycle_time))

            cycle_dict[jid] = cycle_time

            # -------- ratios --------
            ratios = genome[idx:idx+4]
            idx += 4

            ratios = np.array(ratios)
            ratios = np.clip(ratios, 0.1, 1.0)
            ratios = ratios / np.sum(ratios)

            ratio_dict[jid] = ratios.tolist()

            # -------- offset --------
            offset_dict[jid] = 0

        return cycle_dict, ratio_dict, offset_dict