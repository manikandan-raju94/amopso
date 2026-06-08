import xml.etree.ElementTree as ET
import tempfile
import os


class MultiSignalBuilder:

    def __init__(self, template_file=None, net_file=None):
        self.net_file = net_file if net_file else template_file

        if self.net_file is None:
            raise ValueError("Provide net_file/template_file")

        self.tls_templates = {}
        self._load_templates()

    def _load_templates(self):
        tree = ET.parse(self.net_file)
        root = tree.getroot()

        for tl in root.findall(".//tlLogic"):
            jid = tl.get("id")
            phases = []

            for p in tl.findall("phase"):
                state = p.get("state")

                # ✅ SAFETY FIX
                state = state.replace("g", "G")

                phases.append({
                    "duration": int(p.get("duration")),
                    "state": state
                })

            if phases:
                self.tls_templates[jid] = phases

        print("✅ Loaded SAFE TLS templates")

    # ================= MAIN BUILD =================
    def build(self, cycle_dict, ratio_dict, *args, **kwargs):
        xml_string = self.build_string(cycle_dict, ratio_dict)

        # 🔥 WRITE TO TEMP FILE (CRITICAL FIX)
        fd, path = tempfile.mkstemp(suffix=".xml")

        with os.fdopen(fd, 'w') as f:
            f.write(xml_string)

        return path   # ✅ RETURN FILE PATH

    # ================= BUILD STRING =================
    def build_string(self, cycle_dict, ratio_dict):

        root = ET.Element("additional")

        for jid in cycle_dict:

            if jid not in self.tls_templates:
                continue

            template = self.tls_templates[jid]

            cycle = max(40, int(cycle_dict[jid]))  # 🔥 increase min cycle

            ratios = ratio_dict[jid]
            total = sum(ratios)

            # Normalize ratios
            if total == 0:
                ratios = [1.0 / len(ratios)] * len(ratios)
            else:
                ratios = [r / total for r in ratios]

            # Find green phases
            green_idx = [i for i, p in enumerate(template) if "G" in p["state"]]

            if not green_idx:
                continue

            num_green = len(green_idx)

            # 🔥 DISTRIBUTE GREEN TIME PROPERLY
            min_green = 10

            remaining_cycle = cycle - (len(template) - num_green) * 3  # yellow/all-red = 3 sec

            green_times = []

            for i in range(num_green):
                g = max(min_green, int(ratios[i % len(ratios)] * remaining_cycle))
                green_times.append(g)

            # 🔥 NORMALIZE to exact cycle
            total_green = sum(green_times)

            if total_green > 0:
                scale = remaining_cycle / total_green
                green_times = [max(min_green, int(g * scale)) for g in green_times]

            # ================= BUILD XML =================
            tl = ET.SubElement(root, "tlLogic", {
                "id": str(jid),
                "type": "static",
                "programID": "1",
                "offset": "0"
            })

            g_counter = 0

            for i, p in enumerate(template):

                if i in green_idx:
                    duration = str(green_times[g_counter])
                    g_counter += 1
                else:
                    duration = "3"

                ET.SubElement(tl, "phase", {
                    "duration": duration,
                    "state": p["state"]
                })

        return ET.tostring(root, encoding="unicode")