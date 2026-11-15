
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const { createNegotiation, pickNextEvent, applyChoice } = await import('file://' + join(root,'src','negotiation.js').replace(/\\/g,'/'));
const data = JSON.parse(readFileSync(join(root,'src','data','events','role_negotiations.json'),'utf8'));
const phases=['cruise','approach','descent','surface'];
for (const startC of [70, 85, 100]) {
  // greedy max cohesion over a fixed order
  const s = createNegotiation({events:data, startCohesion:startC, seed:3});
  let turns=0, minC=100;
  for (const ph of phases) {
    for (;;) {
      const ev = pickNextEvent(s, ph);
      if (!ev) break;
      let best=null;
      for (const o of ev.options) {
        const c=(o.effects&&o.effects.cohesion_pct)||0;
        if (!best || c>best.c) best={o,c};
      }
      const r=applyChoice(s,best.o.id); turns++;
      minC=Math.min(minC, r.cohesionAfter);
      if (s.mutiny) break;
    }
    if (s.mutiny) break;
  }
  console.log('start',startC,'turns',turns,'final',s.cohesion,'min',minC,'mutiny',s.mutiny, 'order', s.order.length);
}
