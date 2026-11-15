
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const { createNegotiation, pickNextEvent, applyChoice } = await import('file://' + join(root,'src','negotiation.js').replace(/\\/g,'/'));
const data = JSON.parse(readFileSync(join(root,'src','data','events','role_negotiations.json'),'utf8'));
const phases = ['cruise','approach','descent','surface'];
const s = createNegotiation({events:data, startCohesion:70, seed:7});
let turn=0;
for (const ph of phases) {
  for (;;) {
    const ev = pickNextEvent(s, ph);
    if (!ev) break;
    let worst = null;
    for (const o of ev.options) {
      const c = (o.effects&&o.effects.cohesion_pct)||0;
      if (!worst || c < worst.c) worst = {o,c};
    }
    const r = applyChoice(s, worst.o.id);
    turn++;
    console.log(turn, ph, ev.id, worst.o.id, 'coh', r.cohesionAfter, 'mutiny', s.mutiny, 'veto', r.opposed);
    if (s.mutiny) break;
  }
  if (s.mutiny) break;
}
console.log('turns', turn, 'cohesion', s.cohesion, 'mutiny', s.mutiny);
