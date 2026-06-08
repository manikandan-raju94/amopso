import subprocess
import xml.etree.ElementTree as ET
import os
import tempfile
import hashlib


class SumoRunner:

    CACHE = {}   # 🔥 global cache

    def __init__(self, sumo_binary, config, mode="fast"):
        """
        fast  → training (very fast)
        smart → evaluation (balanced)
        full  → final (paper)
        """
        self.sumo_binary = sumo_binary
        self.config = config
        self.mode = mode

    def _get_sim_time(self):
        if self.mode == "fast":
            return "900"
        elif self.mode == "smart":
            return "1800"   # 🔥 balanced
        else:
            return "3600"

    def run(self, signal_path, seed, route_file=None, port=None):

        # ================= VALIDATION =================
        if not isinstance(signal_path, str):
            return 9999.0, 9999.0, 9999.0

        if not os.path.exists(signal_path):
            return 9999.0, 9999.0, 9999.0

        if route_file and not os.path.exists(route_file):
            return 9999.0, 9999.0, 9999.0

        # ================= CACHE KEY =================
        key_str = f"{signal_path}_{seed}_{self.mode}"
        key = hashlib.md5(key_str.encode()).hexdigest()

        if key in SumoRunner.CACHE:
            return SumoRunner.CACHE[key]

        # ================= TEMP FILE =================
        trip_fd, tripinfo_file = tempfile.mkstemp(suffix=".xml")
        os.close(trip_fd)

        sim_time = self._get_sim_time()

        # ================= COMMAND =================
        cmd = [
            self.sumo_binary,
            "-c", self.config,
            "--seed", str(seed),
            "--random", "true",

            "--route-files", route_file if route_file else "",
            "--additional-files", signal_path,
            "--tripinfo-output", tripinfo_file,

            "--no-step-log", "true",
            "--no-warnings", "true",
            "--duration-log.disable", "true",
            "--time-to-teleport", "-1",

            "--end", sim_time,
            "--quit-on-end", "true"
        ]

        if port is not None:
            cmd += ["--remote-port", str(port)]

        # ================= RUN =================
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60 if self.mode == "fast" else 120
            )

            if result.returncode != 0:
                return 9999.0, 9999.0, 9999.0

            if not os.path.exists(tripinfo_file):
                return 9999.0, 9999.0, 9999.0

            # ================= PARSE =================
            tree = ET.parse(tripinfo_file)
            trips = tree.findall("tripinfo")

            if not trips:
                return 9999.0, 9999.0, 9999.0

            # ================= WAIT =================
            waits = [float(t.get("waitingTime", 0)) for t in trips]
            avg_wait = sum(waits) / len(waits)

            # ================= FAST MODE =================
            if self.mode == "fast":
                result = (avg_wait, 0.0, 0.0)
                SumoRunner.CACHE[key] = result
                return result

            # ================= IMPROVED QUEUE =================
            # 🔥 better approximation
            queue = sum(1 for w in waits if w > 2)

            # normalize queue
            queue_norm = queue / len(waits)

            result = (avg_wait, 0.0, queue_norm)
            SumoRunner.CACHE[key] = result
            return result

        except subprocess.TimeoutExpired:
            return 9999.0, 9999.0, 9999.0

        except Exception:
            return 9999.0, 9999.0, 9999.0

        finally:
            if os.path.exists(tripinfo_file):
                try:
                    os.remove(tripinfo_file)
                except:
                    pass