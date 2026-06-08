import xml.etree.ElementTree as ET

def detect_phases(signal_template):
    tree = ET.parse(signal_template)
    root = tree.getroot()
    phases = root.findall(".//phase")

    if not phases:
        raise Exception("No <phase> tags found")

    print(f"✔ Detected {len(phases)} signal phases automatically")
    return len(phases)
