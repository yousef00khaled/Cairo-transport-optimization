"""
Cairo Transportation Network Data
All data from the CSE112 Project Provided Data document.
"""

# ─── Neighborhoods & Districts ───────────────────────────────────────────────
# (ID, Name, Population, Type, X-coordinate (lon), Y-coordinate (lat))
NEIGHBORHOODS = {
    1:  {"name": "Maadi",                     "population": 250000, "type": "Residential",  "x": 31.25, "y": 29.96},
    2:  {"name": "Nasr City",                 "population": 500000, "type": "Mixed",         "x": 31.34, "y": 30.06},
    3:  {"name": "Downtown Cairo",            "population": 100000, "type": "Business",      "x": 31.24, "y": 30.04},
    4:  {"name": "New Cairo",                 "population": 300000, "type": "Residential",   "x": 31.47, "y": 30.03},
    5:  {"name": "Heliopolis",                "population": 200000, "type": "Mixed",          "x": 31.32, "y": 30.09},
    6:  {"name": "Zamalek",                   "population":  50000, "type": "Residential",   "x": 31.22, "y": 30.06},
    7:  {"name": "6th October City",          "population": 400000, "type": "Mixed",          "x": 30.98, "y": 29.93},
    8:  {"name": "Giza",                      "population": 550000, "type": "Mixed",          "x": 31.21, "y": 29.99},
    9:  {"name": "Mohandessin",               "population": 180000, "type": "Business",      "x": 31.20, "y": 30.05},
    10: {"name": "Dokki",                     "population": 220000, "type": "Mixed",          "x": 31.21, "y": 30.03},
    11: {"name": "Shubra",                    "population": 450000, "type": "Residential",   "x": 31.24, "y": 30.11},
    12: {"name": "Helwan",                    "population": 350000, "type": "Industrial",    "x": 31.33, "y": 29.85},
    13: {"name": "New Administrative Capital","population":  50000, "type": "Government",    "x": 31.80, "y": 30.02},
    14: {"name": "Al Rehab",                  "population": 120000, "type": "Residential",   "x": 31.49, "y": 30.06},
    15: {"name": "Sheikh Zayed",              "population": 150000, "type": "Residential",   "x": 30.94, "y": 30.01},
}

# ─── Important Facilities ────────────────────────────────────────────────────
FACILITIES = {
    "F1":  {"name": "Cairo International Airport",  "type": "Airport",    "x": 31.41, "y": 30.11},
    "F2":  {"name": "Ramses Railway Station",        "type": "Transit Hub","x": 31.25, "y": 30.06},
    "F3":  {"name": "Cairo University",              "type": "Education",  "x": 31.21, "y": 30.03},
    "F4":  {"name": "Al-Azhar University",           "type": "Education",  "x": 31.26, "y": 30.05},
    "F5":  {"name": "Egyptian Museum",               "type": "Tourism",    "x": 31.23, "y": 30.05},
    "F6":  {"name": "Cairo International Stadium",   "type": "Sports",     "x": 31.30, "y": 30.07},
    "F7":  {"name": "Smart Village",                 "type": "Business",   "x": 30.97, "y": 30.07},
    "F8":  {"name": "Cairo Festival City",           "type": "Commercial", "x": 31.40, "y": 30.03},
    "F9":  {"name": "Qasr El Aini Hospital",         "type": "Medical",    "x": 31.23, "y": 30.03},
    "F10": {"name": "Maadi Military Hospital",       "type": "Medical",    "x": 31.25, "y": 29.95},
}

# ─── All Nodes (combined) ────────────────────────────────────────────────────
ALL_NODES = {}
for nid, data in NEIGHBORHOODS.items():
    ALL_NODES[str(nid)] = data
for fid, data in FACILITIES.items():
    ALL_NODES[fid] = data

# ─── Existing Roads ──────────────────────────────────────────────────────────
# (from, to, distance_km, capacity_veh_per_hour, condition_1_10)
EXISTING_ROADS = [
    ("1",  "3",  8.5,  3000, 7),
    ("1",  "8",  6.2,  2500, 6),
    ("2",  "3",  5.9,  2800, 8),
    ("2",  "5",  4.0,  3200, 9),
    ("3",  "5",  6.1,  3500, 7),
    ("3",  "6",  3.2,  2000, 8),
    ("3",  "9",  4.5,  2600, 6),
    ("3",  "10", 3.8,  2400, 7),
    ("4",  "2",  15.2, 3800, 9),
    ("4",  "14", 5.3,  3000, 10),
    ("5",  "11", 7.9,  3100, 7),
    ("6",  "9",  2.2,  1800, 8),
    ("7",  "8",  24.5, 3500, 8),
    ("7",  "15", 9.8,  3000, 9),
    ("8",  "10", 3.3,  2200, 7),
    ("8",  "12", 14.8, 2600, 5),
    ("9",  "10", 2.1,  1900, 7),
    ("10", "11", 8.7,  2400, 6),
    ("11", "F2", 3.6,  2200, 7),
    ("12", "1",  12.7, 2800, 6),
    ("13", "4",  45.0, 4000, 10),
    ("14", "13", 35.5, 3800, 9),
    ("15", "7",  9.8,  3000, 9),
    ("F1", "5",  7.5,  3500, 9),
    ("F1", "2",  9.2,  3200, 8),
    ("F2", "3",  2.5,  2000, 7),
    ("F7", "15", 8.3,  2800, 8),
    ("F8", "4",  6.1,  3000, 9),
    # ── Facility access roads (connecting facilities to nearest neighborhoods) ──
    ("F3", "10", 0.5,  2000, 8),   # Cairo University ↔ Dokki (same area)
    ("F3", "8",  2.5,  1800, 7),   # Cairo University ↔ Giza
    ("F4", "3",  1.8,  1500, 7),   # Al-Azhar University ↔ Downtown
    ("F5", "3",  1.2,  1800, 8),   # Egyptian Museum ↔ Downtown
    ("F5", "6",  1.5,  1500, 8),   # Egyptian Museum ↔ Zamalek
    ("F6", "2",  3.5,  2500, 8),   # Cairo Stadium ↔ Nasr City
    ("F6", "5",  2.8,  2200, 8),   # Cairo Stadium ↔ Heliopolis
    ("F9", "3",  1.0,  2000, 8),   # Qasr El Aini Hospital ↔ Downtown
    ("F9", "10", 1.5,  1800, 7),   # Qasr El Aini Hospital ↔ Dokki
    ("F9", "1",  5.0,  2200, 7),   # Qasr El Aini Hospital ↔ Maadi
    ("F10","1",  1.2,  2000, 8),   # Maadi Military Hospital ↔ Maadi
    ("F10","12", 10.5, 2400, 6),   # Maadi Military Hospital ↔ Helwan
]

# ─── Potential New Roads ─────────────────────────────────────────────────────
# (from, to, distance_km, estimated_capacity, construction_cost_million_EGP)
POTENTIAL_ROADS = [
    ("1",  "4",  22.8, 4000, 450),
    ("1",  "14", 25.3, 3800, 500),
    ("2",  "13", 48.2, 4500, 950),
    ("3",  "13", 56.7, 4500, 1100),
    ("5",  "4",  16.8, 3500, 320),
    ("6",  "8",  7.5,  2500, 150),
    ("7",  "13", 82.3, 4000, 1600),
    ("9",  "11", 6.9,  2800, 140),
    ("10", "F7", 27.4, 3200, 550),
    ("11", "13", 62.1, 4200, 1250),
    ("12", "14", 30.5, 3600, 610),
    ("14", "5",  18.2, 3300, 360),
    ("15", "9",  22.7, 3000, 450),
    ("F1", "13", 40.2, 4000, 800),
    ("F7", "9",  26.8, 3200, 540),
]

# ─── Traffic Flow Patterns ───────────────────────────────────────────────────
# road_key: (morning_peak, afternoon, evening_peak, night)
TRAFFIC_FLOW = {
    "1-3":   (2800, 1500, 2600, 800),
    "1-8":   (2200, 1200, 2100, 600),
    "2-3":   (2700, 1400, 2500, 700),
    "2-5":   (3000, 1600, 2800, 650),
    "3-5":   (3200, 1700, 3100, 800),
    "3-6":   (1800, 1400, 1900, 500),
    "3-9":   (2400, 1300, 2200, 550),
    "3-10":  (2300, 1200, 2100, 500),
    "4-2":   (3600, 1800, 3300, 750),
    "4-14":  (2800, 1600, 2600, 600),
    "5-11":  (2900, 1500, 2700, 650),
    "6-9":   (1700, 1300, 1800, 450),
    "7-8":   (3200, 1700, 3000, 700),
    "7-15":  (2800, 1500, 2600, 600),
    "8-10":  (2000, 1100, 1900, 450),
    "8-12":  (2400, 1300, 2200, 500),
    "9-10":  (1800, 1200, 1700, 400),
    "10-11": (2200, 1300, 2100, 500),
    "11-F2": (2100, 1200, 2000, 450),
    "12-1":  (2600, 1400, 2400, 550),
    "13-4":  (3800, 2000, 3500, 800),
    "14-13": (3600, 1900, 3300, 750),
    "15-7":  (2800, 1500, 2600, 600),
    "F1-5":  (3300, 2200, 3100, 1200),
    "F1-2":  (3000, 2000, 2800, 1100),
    "F2-3":  (1900, 1600, 1800, 900),
    "F7-15": (2600, 1500, 2400, 550),
    "F8-4":  (2800, 1600, 2600, 600),
    # Facility access roads traffic
    "F3-10": (1500, 800,  1400, 300),
    "F3-8":  (1200, 700,  1100, 250),
    "F4-3":  (1000, 600,  900,  200),
    "F5-3":  (1800, 1200, 1600, 500),
    "F5-6":  (1200, 800,  1100, 350),
    "F6-2":  (2000, 1000, 2500, 400),
    "F6-5":  (1800, 900,  2200, 350),
    "F9-3":  (1600, 1000, 1500, 600),
    "F9-10": (1400, 900,  1300, 500),
    "F9-1":  (1200, 700,  1100, 400),
    "F10-1": (1000, 600,  900,  300),
    "F10-12":(800,  500,  700,  200),
}

TIME_PERIODS = ["morning", "afternoon", "evening", "night"]
TIME_PERIOD_INDEX = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}

# ─── Metro Lines ─────────────────────────────────────────────────────────────
METRO_LINES = {
    "M1": {"name": "Line 1 (Helwan-New Marg)", "stations": ["12", "1", "3", "F2", "11"], "daily_passengers": 1500000},
    "M2": {"name": "Line 2 (Shubra-Giza)",     "stations": ["11", "F2", "3", "10", "8"], "daily_passengers": 1200000},
    "M3": {"name": "Line 3 (Airport-Imbaba)",   "stations": ["F1", "5", "2", "3", "9"],  "daily_passengers":  800000},
}

# ─── Bus Routes ──────────────────────────────────────────────────────────────
BUS_ROUTES = {
    "B1":  {"stops": ["1", "3", "6", "9"],          "buses": 25, "daily_passengers": 35000},
    "B2":  {"stops": ["7", "15", "8", "10", "3"],   "buses": 30, "daily_passengers": 42000},
    "B3":  {"stops": ["2", "5", "F1"],               "buses": 20, "daily_passengers": 28000},
    "B4":  {"stops": ["4", "14", "2", "3"],          "buses": 22, "daily_passengers": 31000},
    "B5":  {"stops": ["8", "12", "1"],               "buses": 18, "daily_passengers": 25000},
    "B6":  {"stops": ["11", "5", "2"],               "buses": 24, "daily_passengers": 33000},
    "B7":  {"stops": ["13", "4", "14"],              "buses": 15, "daily_passengers": 21000},
    "B8":  {"stops": ["F7", "15", "7"],              "buses": 12, "daily_passengers": 17000},
    "B9":  {"stops": ["1", "8", "10", "9", "6"],     "buses": 28, "daily_passengers": 39000},
    "B10": {"stops": ["F8", "4", "2", "5"],          "buses": 20, "daily_passengers": 28000},
}

# ─── Public Transportation Demand ────────────────────────────────────────────
# (from, to, daily_passengers)
TRANSIT_DEMAND = [
    ("3",  "5",  15000),
    ("1",  "3",  12000),
    ("2",  "3",  18000),
    ("F2", "11", 25000),
    ("F1", "3",  20000),
    ("7",  "3",  14000),
    ("4",  "3",  16000),
    ("8",  "3",  22000),
    ("3",  "9",  13000),
    ("5",  "2",  17000),
    ("11", "3",  24000),
    ("12", "3",  11000),
    ("1",  "8",   9000),
    ("7",  "F7", 18000),
    ("4",  "F8", 12000),
    ("13", "3",   8000),
    ("14", "4",   7000),
]

# ─── Medical Facilities (for emergency routing) ─────────────────────────────
MEDICAL_FACILITIES = ["F9", "F10"]

# ─── Critical Facilities (must have good connectivity in MST) ────────────────
CRITICAL_FACILITIES = ["F9", "F10", "13"]  # Hospitals + Government
