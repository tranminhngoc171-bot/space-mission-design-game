/**
 * Smoke test — runs the engine on the three reference designs documented in
 * docs/02-BALANCE-DATA.md and on the objectives of each scenario.
 *
 * Usage: node scripts/smoke_engine.mjs
 * Exit 0 = engine agrees with the documented balance.
 */
import { computeMission } from '../src/engine.js';

const CASES = [
  {
    name: 'climate_watch / budget-constrained (expect o4 lifetime FAIL is documented)',
    scenarioId: 'climate_watch',
    design: {
      scenarioId: 'climate_watch',
      bus: 'bus_medium', power: 'solar_large', battery: 'bat_medium',
      orbit: 'leo_sso_400', launcher: 'falcon9_rideshare', duration_months: 36,
      instruments: ['cam_hires', 'cam_stereo', 'spec_tir', 'transponder_ka'],
    },
  },
  {
    name: 'disaster_response / 9h revisit design',
    scenarioId: 'disaster_response',
    design: {
      scenarioId: 'disaster_response',
      bus: 'bus_small', power: 'solar_large', battery: 'bat_medium',
      orbit: 'leo_550', launcher: 'falcon9_rideshare', duration_months: 24,
      instruments: ['radar_sar', 'transponder_ka'],
    },
  },
  {
    name: 'space_weather / MEO science design',
    scenarioId: 'space_weather',
    design: {
      scenarioId: 'space_weather',
      bus: 'bus_small', power: 'solar_small', battery: 'bat_medium',
      orbit: 'meo_20200', launcher: 'falcon9_dedicated', duration_months: 60,
      instruments: ['plasma', 'magnetometer'],
    },
  },
];

let failures = 0;

for (const c of CASES) {
  const r = computeMission(c.design, c.scenarioId, { seed: 7 });
  console.log(`\n=== ${c.name} ===`);
  console.log(`  mass ${r.derived.massWithMargin.toFixed(0)} kg | power ${r.derived.draw.toFixed(0)}/${r.derived.generation.toFixed(0)} W | budget $${r.derived.cost.toFixed(1)}M`);
  console.log(`  data ${r.derived.generatedGbDay} GB/d -> ${r.derived.deliveredPct.toFixed(0)}% delivered | life ${r.derived.lifetime.toFixed(2)} y`);
  for (const k of r.checks) console.log(`  [${k.pass ? 'PASS' : 'FAIL'}] ${k.label}: ${k.detail}`);
  for (const o of r.objectives) {
    console.log(`  [${o.pass ? 'PASS' : 'FAIL'}] ${o.id} ${o.label}: actual ${o.actual === null ? 'n/a' : o.actual.toFixed(1)} want ${o.operator} ${o.target}`);
  }
  console.log(`  score ${r.score.total} (ms ${r.score.mission_success} / sci ${r.score.science_value} / eff ${r.score.resource_efficiency} / rob ${r.score.robustness}) band=${r.score.band}`);

  if (!Number.isFinite(r.score.total)) { console.log('  !! score is not finite'); failures++; }
  if (r.resources.mass.status === 'fail') { console.log('  !! mass gate should not fail on a reference design'); failures++; }
  if (r.resources.budget.status === 'fail') { console.log('  !! budget should not fail on a reference design'); failures++; }
}

/* Determinism check: same seed must give the same score. */
const a = computeMission(CASES[2].design, CASES[2].scenarioId, { seed: 42 });
const b = computeMission(CASES[2].design, CASES[2].scenarioId, { seed: 42 });
if (a.score.total !== b.score.total) { console.log('\n!! engine is not deterministic for a fixed seed'); failures++; }
else console.log(`\nDeterminism: seed 42 -> ${a.score.total} twice. OK`);

/* Clean-run check: with no events, the reference designs must pass the
 * objectives that docs/02-BALANCE-DATA.md says they pass. Events are allowed to
 * knock a marginal design below target — that is the game — but a clean run must
 * reproduce the documented balance. */
const CLEAN = {
  climate_watch: ['o1', 'o2', 'o3', 'o5'],       // o4 lifetime is documented as the on-purpose failure
  disaster_response: ['o1', 'o2', 'o3', 'o4'],
  space_weather: ['o1', 'o2', 'o3', 'o4'],
};
console.log('\n--- clean run (no events) ---');
for (const c of CASES) {
  const r = computeMission(c.design, c.scenarioId, { noEvents: true });
  const passing = r.objectives.filter((o) => o.pass).map((o) => o.id).sort();
  const expected = [...CLEAN[c.scenarioId]].sort();
  const ok = JSON.stringify(passing) === JSON.stringify(expected);
  console.log(`${ok ? 'OK  ' : 'BAD '} ${c.scenarioId}: passes ${passing.join(',')} (expected ${expected.join(',')})`);
  if (!ok) failures++;
}

console.log(failures ? `\n${failures} problem(s)` : '\nAll engine checks passed.');
process.exit(failures ? 1 : 0);
