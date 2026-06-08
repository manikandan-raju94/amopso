import subprocess
import xml.etree.ElementTree as ET
import os


class SumoRunnerFinal:

    def __init__(self, sumo_binary, config):
        self.sumo_binary = sumo_binary
        self.config = config

    def run(self, signal_file, seed=42, route_file=None):

        tripinfo = "temp_tripinfo.xml"

        cmd = [
            self.sumo_binary,
            "-c", self.config,
            "--additional-files", signal_file,
            "--tripinfo-output", tripinfo,
            "--seed", str(seed)
        ]

        if route_file:
            cmd.extend(["--route-files", route_file])

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return self.evaluate(tripinfo)

    def evaluate(self, file):

        # 🚨 SAFETY: file missing
        if not os.path.exists(file):
            return 9999.0, 9999.0, 9999.0

        tree = ET.parse(file)
        root = tree.getroot()

        total_wait = 0
        total_queue = 0
        total_co2 = 0   # (dummy for now)
        n = 0

        for t in root.findall("tripinfo"):
            wait = float(t.get("waitingTime", 0))
            total_wait += wait

            # 🚨 Approx queue proxy (you can refine later)
            total_queue += float(t.get("waitingCount", 0))

            # 🚨 CO2 not available in tripinfo → keep 0 or extend later
            total_co2 += 0

            n += 1

        if n == 0:
            return 9999.0, 9999.0, 9999.0

        avg_wait = total_wait / n
        avg_queue = total_queue / n
        avg_co2 = total_co2 / n

        return float(avg_wait), float(avg_co2), float(avg_queue)