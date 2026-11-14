/* ============================================================
   data.js — loads ../data/*.json
   Owner: shared. Read-only for @bersious; @tranminhngoc171-bot
   owns the numbers inside those JSON files.
   ------------------------------------------------------------
   RULE (from src/README.md): no numbers live in code.
   If you find a hard-coded mass, cost, watt or day anywhere in
   src/*.js, it is a bug — it belongs in data/*.json.
   ============================================================ */

const FILES = ['scenarios', 'instruments', 'orbits', 'launch_vehicles', 'events'];

export const DB = {
  scenarios: null,
  instruments: null,
  orbits: null,
  launch_vehicles: null,
  events: null,
};

// Flat lookup tables built once so the UI never searches by string.
export const INDEX = {
  instrument: {},
  orbit: {},
  launcher: {},
  event: {},
};

let loaded = false;

export async function loadData() {
  if (loaded) return DB;

  const results = await Promise.all(
    FILES.map(async (name) => {
      const res = await fetch(`../data/${name}.json`, { cache: 'no-store' });
      if (!res.ok) throw new Error(`Cannot load data/${name}.json (HTTP ${res.status})`);
      return [name, await res.json()];
    })
  );

  for (const [name, json] of results) {
    DB[name] = json;
  }

  for (const it of DB.instruments.instruments) INDEX.instrument[it.id] = it;
  for (const it of DB.orbits.orbits) INDEX.orbit[it.id] = it;
  for (const it of DB.launch_vehicles.launchers) INDEX.launcher[it.id] = it;
  for (const it of DB.events.events ?? []) INDEX.event[it.id] = it;

  loaded = true;
  return DB;
}

/* Buses and power sources are NOT defined here.
   They contain numbers (mass, cost, watts) and therefore belong in
   data/buses.json and data/power.json — see docs/08-FRAMEWORK-AND-STRUCTURE.md §5.
   Until those files exist, the UI cannot offer bus/power selection.
   Do not re-add them to this file. */
