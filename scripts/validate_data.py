#!/usr/bin/env python3
"""Validate data/*.json and check the three reference designs are still feasible.

Usage:  python scripts/validate_data.py
Exit code 0 = data coherent and all reference designs behave as documented.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

OPS_COST_PER_YEAR = 6.5
MASS_MARGIN = 1.15


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


def index(items):
    return {i["id"]: i for i in items}


instruments = index(load("instruments.json")["instruments"])
orbits = index(load("orbits.json")["orbits"])
launchers = index(load("launch_vehicles.json")["launchers"])
events = load("events.json")["events"]
scenarios = index(load("scenarios.json")["scenarios"])
bus_cfg = load("instruments.json")["bus_options"]
buses = index(bus_cfg["bus"])
powers = index(bus_cfg["power"])
batteries = index(bus_cfg["battery"])


def compute(design):
    bus, power, battery = buses[design["bus"]], powers[design["power"]], batteries[design["battery"]]
    orbit, launcher = orbits[design["orbit"]], launchers[design["launcher"]]
    payload = [instruments[i] for i in design["instruments"]]
    dur_years = design["duration_months"] / 12

    mass = bus["dry_mass_kg"] + power["mass_kg"] + battery["mass_kg"] + sum(i["mass_kg"] for i in payload)
    mass_margin = mass * MASS_MARGIN

    gen = power["power_gen_w"]
    draw = bus["power_overhead_w"] + sum(i["power_w"] for i in payload)
    battery_need = draw * (35 / 60)

    cost = (bus["cost_musd"] * orbit["cost_multiplier"] + power["cost_musd"] + battery["cost_musd"]
            + sum(i["cost_musd"] for i in payload) + launcher["cost_musd"]
            + OPS_COST_PER_YEAR * dur_years)

    downlink = (orbit["comm_window_pct"] / 100 * orbit["downlink_mbps"] * 86400 / 8 / 1000
                + sum(i.get("downlink_gb_day", 0) for i in payload))
    generated = sum(i["data_gb_day"] for i in payload)
    delivered = min(100.0, 100 * downlink / max(generated, 0.001))

    lifetime = orbit["base_lifetime_years"] * (1 - 0.1 * orbit["radiation_index"])
    science = sum(i["science_value"] for i in payload)
    capacity = launcher["capacity_kg"].get(design["orbit"], 0)

    def sc(cat):
        return sum(i["science_value"] for i in payload if i["category"] == cat)

    return {
        "mass_kg": mass, "mass_with_margin": mass_margin, "capacity_kg": capacity,
        "power_gen_w": gen, "power_draw_w": draw, "battery_need_wh": battery_need,
        "battery_wh": battery["capacity_wh"],
        "cost_musd": cost,
        "downlink_gb_day": downlink, "data_gb_day": generated, "data_delivered_pct": delivered,
        "lifetime_years": lifetime, "science_total": science,
        "science_imaging": sc("imaging"), "science_thermal": sc("spectroscopy") + sc("sensing"),
        "science_radar": sc("imaging") if any(i["id"] == "radar_sar" for i in payload) else 0,
        "science_plasma": sc("space_physics"),
        "science_magnetometry": (instruments["magnetometer"]["science_value"]
                                 if "magnetometer" in design["instruments"] else 0),
        "comm_window_pct": orbit["comm_window_pct"],
        "revisit_hours": orbit["revisit_hours"],
        "instrument_count": len(payload),
    }


def checks(m, design):
    orbit, launcher = orbits[design["orbit"]], launchers[design["launcher"]]
    bus = buses[design["bus"]]
    return [
        ("mass", m["mass_with_margin"] <= m["capacity_kg"] and m["capacity_kg"] > 0,
         f"{m['mass_with_margin']:.0f} kg (15% margin) vs {m['capacity_kg']} kg capacity"),
        ("power", m["power_draw_w"] <= m["power_gen_w"],
         f"{m['power_draw_w']:.0f} W draw vs {m['power_gen_w']:.0f} W generation"),
        ("battery", m["battery_wh"] >= m["battery_need_wh"],
         f"{m['battery_wh']:.0f} Wh vs {m['battery_need_wh']:.0f} Wh needed for 35 min eclipse"),
        ("orbit_class", orbit["id"] in [k for k, v in launcher["capacity_kg"].items() if v > 0],
         f"{launcher['name']} reaches {orbit['name']}"),
        ("instrument_slots", m["instrument_count"] <= bus["max_instruments"],
         f"{m['instrument_count']} instruments vs {bus['max_instruments']} slots"),
    ]


REFERENCE = {
    "climate_watch": {
        "design": {
            "bus": "bus_medium", "power": "solar_large", "battery": "bat_medium",
            "orbit": "leo_sso_400", "launcher": "falcon9_rideshare", "duration_months": 36,
            "instruments": ["cam_hires", "cam_stereo", "spec_tir", "transponder_ka"],
        },
        # lifetime 2.955 y < 3 y -> o4 FAILS on purpose (documented lesson)
        "expect_pass": {"o1", "o2", "o3", "o5"},
    },
    "disaster_response": {
        "design": {
            "bus": "bus_small", "power": "solar_large", "battery": "bat_medium",
            "orbit": "leo_550", "launcher": "falcon9_rideshare", "duration_months": 24,
            "instruments": ["radar_sar", "transponder_ka"],
        },
        "expect_pass": {"o1", "o2", "o3", "o4"},
    },
    "space_weather": {
        "design": {
            "bus": "bus_small", "power": "solar_small", "battery": "bat_medium",
            "orbit": "meo_20200", "launcher": "falcon9_dedicated", "duration_months": 60,
            "instruments": ["plasma", "magnetometer"],
        },
        "expect_pass": {"o1", "o2", "o3", "o4"},
    },
}


def main():
    problems = []

    # 1. referential integrity
    for lid, l in launchers.items():
        for oid in l["capacity_kg"]:
            if oid not in orbits:
                problems.append(f"launcher {lid} references unknown orbit {oid}")
    for sid, s in scenarios.items():
        w = sum(o["weight"] for o in s["objectives"])
        if abs(w - 1.0) > 1e-6:
            problems.append(f"scenario {sid} objective weights sum to {w}, expected 1.0")
    for o in orbits.values():
        if not set(o["launcher_classes"]) <= {"small", "medium", "large"}:
            problems.append(f"orbit {o['id']} has unknown launcher class")
    ids = [i["id"] for i in instruments.values()]
    if len(ids) != len(set(ids)):
        problems.append("duplicate instrument ids")

    # 2. reference designs
    for sid, ref in REFERENCE.items():
        scen = scenarios[sid]
        m = compute(ref["design"])
        print(f"\n=== {sid} — {scen['name']} ===")
        print(f"  mass   {m['mass_with_margin']:8.1f} kg /{m['capacity_kg']:>7} kg")
        print(f"  power  {m['power_draw_w']:8.1f} W  /{m['power_gen_w']:>7.0f} W")
        print(f"  budget {m['cost_musd']:8.1f} M  /{scen['budget_musd']:>7.0f} M")
        print(f"  data   {m['data_gb_day']:8.1f} GB/d -> {m['downlink_gb_day']:.1f} GB/d "
              f"({m['data_delivered_pct']:.0f}% delivered)")
        print(f"  life   {m['lifetime_years']:8.2f} y")
        for name, ok, detail in checks(m, ref["design"]):
            print(f"  [{'PASS' if ok else 'FAIL'}] {name:16} {detail}")
            if not ok:
                problems.append(f"{sid}: gate '{name}' fails — {detail}")
        if m["cost_musd"] > scen["budget_musd"]:
            problems.append(f"{sid}: reference design is {m['cost_musd'] - scen['budget_musd']:.1f}M over budget")
        got = set()
        for o in scen["objectives"]:
            actual = m[o["metric"]] if o["metric"] in m else None
            if actual is None:
                problems.append(f"{sid}: unknown metric {o['metric']}")
                continue
            ok = actual >= o["target"] if o["operator"] == "min" else actual <= o["target"]
            if ok:
                got.add(o["id"])
            print(f"  [{'PASS' if ok else 'FAIL'}] {o['id']} {o['label']:34} "
                  f"want {o['operator']} {o['target']} got {actual:.2f}")
        if got != ref["expect_pass"]:
            problems.append(f"{sid}: objectives passing {sorted(got)} != expected {sorted(ref['expect_pass'])}")

    print("\n" + "=" * 60)
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK — {len(scenarios)} scenarios, {len(instruments)} instruments, "
          f"{len(orbits)} orbits, {len(launchers)} launchers, {len(events)} events coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
