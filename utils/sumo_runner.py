import os
import traci
import random
import xml.etree.ElementTree as ET
from config.config import *

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_wait(tripinfo):
    tree = ET.parse(tripinfo)
    root = tree.getroot()
    waits = [float(t.get("waitingTime")) for t in root.findall("tripinfo")]
    return sum(waits) / len(waits) if waits else 9999

def run_sumo(signal_file, tag):
    # Ensure output directory exists
    output_dir = f"results/{tag}/"
    ensure_dir(output_dir)

    tripinfo = os.path.join(output_dir, "tripinfo.xml")

    cmd = [
        SUMO_BINARY,
        "-c", CONFIG_FILE,
        "--additional-files", signal_file,
        "--tripinfo-output", tripinfo,
        "--no-step-log", "true",
        "--seed", str(random.randint(0, 99999))
    ]

    try:
        traci.start(cmd)
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

        teleports = traci.simulation.getEndingTeleportNumber()
        traci.close()

        return extract_wait(tripinfo) + teleports * TELEPORT_PENALTY

    except Exception as e:
        print("\n❌ SUMO RUNTIME ERROR:", e)
        try:
            traci.close()
        except:
            pass
        return 9999
