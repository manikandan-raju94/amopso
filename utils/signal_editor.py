import xml.etree.ElementTree as ET
from config.config import SIGNAL_TEMPLATE, TEMP_SIGNAL, CYCLE_TIME

def update_signal(phase_ratios):
    tree = ET.parse(SIGNAL_TEMPLATE)
    root = tree.getroot()
    phases = root.findall(".//phase")

    ratios = phase_ratios / phase_ratios.sum()
    durations = [max(1, int(r * CYCLE_TIME)) for r in ratios]

    for p, d in zip(phases, durations):
        p.set("duration", str(d))

    tree.write(TEMP_SIGNAL)
    return TEMP_SIGNAL
