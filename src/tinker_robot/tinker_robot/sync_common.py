"""Shared robot joints and conservative software motion bounds (radians)."""
import math
from pathlib import Path
from xml.etree import ElementTree as ET

JOINTS = ('Joint_1', 'Joint_2', 'Joint_3', 'Joint_4', 'Joint_5', 'Left_Joint', 'Right_Joint')
# Conservative caps from previous tests; Joint_3 stays well clear of +/-1.3 hard stops.
CAPS = {
    'Joint_1': (0.10, 6.10),
    'Joint_2': (-0.75, 0.75),
    'Joint_3': (-1.00, 1.00),
    'Joint_4': (0.10, 6.10),
    'Joint_5': (-1.70, 2.00),
    'Left_Joint': (-0.70, -0.04),
    'Right_Joint': (0.04, 0.70),
}
URDF = Path.home() / 'Industrial_Robotics/src/URDF_FIN/urdf/URDF_FIN.urdf'


def load_limits():
    root = ET.parse(URDF).getroot()
    physical = {}
    safe = {}
    for name in JOINTS:
        elem = root.find(f"./joint[@name='{name}']/limit")
        if elem is None:
            raise ValueError(f'Missing URDF limits for {name}: {URDF}')
        lo, hi = float(elem.attrib['lower']), float(elem.attrib['upper'])
        if not math.isfinite(lo + hi) or not lo < hi:
            raise ValueError(f'Invalid URDF limits for {name}')
        physical[name] = (lo, hi)
        margin = min(0.05, 0.05 * (hi - lo))
        caplo, caphi = CAPS[name]
        slo, shi = max(lo + margin, caplo), min(hi - margin, caphi)
        if not slo < shi:
            raise ValueError(f'No safe interval for {name}: URDF {lo,hi} and cap {caplo,caphi}')
        safe[name] = (slo, shi)
    return physical, safe


def name_for(user):
    return next((j for j in JOINTS if j.lower() == user.strip().lower()), None)


def nearest(x, bounds):
    return max(bounds[0], min(bounds[1], x))


def deg_range(bounds):
    return f'{math.degrees(bounds[0]):.1f}° to {math.degrees(bounds[1]):.1f}°'
