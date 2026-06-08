import xml.etree.ElementTree as ET

# =====================================================================
#  metrics_extractor.py
#  FINAL VERSION — Computes average emissions per vehicle (g/veh)
#  SUMO emission-output format: timestep-based <timestep><vehicle .../>
# =====================================================================

def extract_emission_and_queue(emission_file, queue_file):

    metrics = {
        "CO2": 0.0, 
        "fuel": 0.0, 
        "NOx": 0.0,
        "PMx": 0.0, 
        "CO": 0.0, 
        "queue": 0.0
    }

    # -----------------------------------------------------------------
    # 1️⃣ EMISSION EXTRACTION (mg per timestep → g per vehicle)
    # -----------------------------------------------------------------
    try:
        tree = ET.parse(emission_file)
        root = tree.getroot()

        CO2 = fuel = NOx = PMx = CO = 0.0
        vehicle_ids = set()

        # Read all emissions for all vehicles across timesteps
        for ts in root.findall(".//timestep/vehicle"):

            # Collect unique vehicle IDs
            vid = ts.get("id")
            if vid:
                vehicle_ids.add(vid)

            # SUMO gives mg/s → we accumulate mg
            CO2  += float(ts.get("CO2", 0))
            fuel += float(ts.get("fuel", 0))
            NOx  += float(ts.get("NOx", 0))
            PMx  += float(ts.get("PMx", 0))
            CO   += float(ts.get("CO", 0))

        num_vehicles = max(1, len(vehicle_ids))

        # mg → g, then divide by number of vehicles
        metrics["CO2"]  = (CO2  / 1000) / num_vehicles
        metrics["fuel"] = (fuel / 1000) / num_vehicles
        metrics["NOx"]  = (NOx  / 1000) / num_vehicles
        metrics["PMx"]  = (PMx  / 1000) / num_vehicles
        metrics["CO"]   = (CO   / 1000) / num_vehicles

    except Exception as e:
        print("❌ Emission file read error:", e)


    # -----------------------------------------------------------------
    # 2️⃣ QUEUE EXTRACTION — average queueing_time
    # -----------------------------------------------------------------
        # -----------------------------------------------------------------
    # 2️⃣ QUEUE EXTRACTION — average queueing_time (from <lane>)
    # -----------------------------------------------------------------
    try:
        qtree = ET.parse(queue_file)
        qroot = qtree.getroot()

        qsum = 0.0
        count = 0

        # SUMO queue-output structure:
        # <data timestep="..."><lanes><lane queueing_time="..."/></lanes></data>
        for lane in qroot.findall(".//lane"):
            qt = lane.get("queueing_time")
            if qt is not None:
                qsum += float(qt)
                count += 1

        metrics["queue"] = qsum / count if count > 0 else 0.0

    except Exception as e:
        print("❌ Queue file read error:", e)


    return metrics
