/* ============================================================
   sim-water-farm.mjs
   Mô phỏng 35 Sol trên hab-stats.js THẬT (không giả lập DOM), có
   tính cả chuyện tưới cây trừ vào nước uống của phi hành gia.

   Mục đích: chọn chi phí nước mỗi khay dựa trên số thật, và chứng
   minh người chơi chơi hợp lý thì sống tới Sol 35, chơi dở thì chết.

   Chạy: node scripts/sim-water-farm.mjs           (chi phí đã chọn)
        node scripts/sim-water-farm.mjs --sweep   (quét nhiều mức)
   ============================================================ */

const CHOSEN_COST = 12;
const WATER_COSTS = [4, 6, 8, 10, 12, 14, 16, 20];
const SOLS = 35;

/* ---------- đồng hồ giả ---------- */

function makeClock() {
  let m = 8 * 60;
  let d = 1;
  return {
    state: () => ({
      day: d,
      minutes: m,
      isNight: m >= 1080 || m < 360,
    }),
    advance(n) {
      m += n;
      while (m >= 1440) { m -= 1440; d += 1; }
    },
    get minutes() { return m; },
    get day() { return d; },
  };
}

const ITEM_POOL = ['ration', 'water_bottle', 'tape', 'electronics', 'media'];

/* ---------- một ván ---------- */

async function runOne({ cost, style, seed, farmEnabled = true }) {
  const mod = await import('../src/hab-stats.js');
  const clock = makeClock();

  const st = mod.createStats({
    clock,
    initialState: {
      stats: {
        stamina: 80, calories: 75, water: 70, sanity: 65,
        power: 60, oxygen: 100, seal: 100,
      },
      inv: {
        ration: 12, water_bottle: 14, tape: 4, electronics: 3,
        hydrazine: 2, media: 2, potato_seed: 1, potato: 0,
      },
    },
  });

  let rnd = (seed * 7919 + 13) % 2147483647;
  const rand = () => {
    rnd = (rnd * 1103515245 + 12345) & 0x7fffffff;
    return rnd / 0x7fffffff;
  };

  const good = style === 'good';
  let dead = null;
  let waterSpentOnFarm = 0;
  let harvestKg = 0;
  let planted = [];
  let seedsLeft = 20;
  let filterBought = false;
  let minWater = 100;
  let blockedSows = 0;

  while (clock.day <= SOLS && !dead) {
    const bedHour = good ? 22 : 19;
    for (let hour = 7; hour < bedHour; hour++) {
      let v = st.get();
      let inv = st.getInventory();

      /* uống: người chơi tốt uống sớm, người chơi dở để khát mới uống */
      if (v.water < (good ? 60 : 10) && inv.water_bottle > 0) st.useItem('water_bottle');

      /* ăn: ưu tiên khoai tự trồng */
      v = st.get();
      if (v.calories < (good ? 55 : 8)) {
        if ((inv.potato || 0) > 0) st.useItem('potato');
        else if ((inv.ration || 0) > 0) st.useItem('ration');
      }

      /* chế nước từ hydrazine khi tụt sâu */
      if (good && st.get().water < 30 && (st.getInventory().hydrazine || 0) > 0) {
        st.craft('make_water');
      }

      /* mua bộ lọc nước (tăng hiệu suất thu hồi thêm 30 phần trăm) */
      if (good && !filterBought) {
        inv = st.getInventory();
        if ((inv.electronics || 0) >= 2 && (inv.tape || 0) >= 1) {
          if (st.craft('water_filter').ok) filterBought = true;
        }
      }

      /* thám hiểm */
      const trips = good ? 2 : 3;
      if (hour >= 10 && hour < 10 + trips && st.get().stamina > 40) {
        st.tick(60);
        clock.advance(60);
        if (rand() < 0.45) {
          const id = ITEM_POOL[Math.floor(rand() * ITEM_POOL.length)];
          st.addItems([{ id, qty: 1 + Math.floor(rand() * 2) }]);
        }
        continue;
      }

      /* 07:00: thu hoạch vụ chín rồi gieo vụ mới */
      if (hour === 7) {
        for (const p of planted.slice()) {
          if (clock.day - p.day >= 3) {
            const kg = 2.5 + rand();
            st.addItems([{ id: 'potato', qty: Math.max(1, Math.round(kg / 0.25)) }]);
            harvestKg += kg;
            planted = planted.filter((x) => x !== p);
          }
        }
        if (farmEnabled && seedsLeft > 0) {
          /* người chơi tốt chỉ gieo một khay mỗi vụ cho chắc nước uống,
             người chơi dở dồn cả 12 khay một lượt */
          const want = good ? 1 : 12;
          for (let k = 0; k < want && seedsLeft > 0; k++) {
            const r = st.spendWater(cost);
            if (!r.ok) { blockedSows += 1; break; }
            waterSpentOnFarm += cost;
            seedsLeft -= 1;
            planted.push({ day: clock.day });
          }
        }
      }

      st.tick(60);
      clock.advance(60);
      v = st.get();
      minWater = Math.min(minWater, v.water);
      if (!v.alive) { dead = { sol: clock.day, hour, cause: 'hết chỉ số ban ngày' }; break; }
    }

    if (dead) break;

    /* ngủ tới 07:00 hôm sau */
    const nowMin = clock.minutes;
    const spanMin = (1440 - nowMin) + 7 * 60;
    st.tick(spanMin, { sleeping: true });
    clock.advance(spanMin);

    const after = st.get();
    minWater = Math.min(minWater, after.water);
    if (!after.alive) {
      dead = { sol: clock.day, cause: 'chết trong lúc ngủ', water: Math.round(after.water), cal: Math.round(after.calories) };
      break;
    }
    if (after.calories < 20) {
      if ((st.getInventory().potato || 0) > 0) st.useItem('potato');
      else if ((st.getInventory().ration || 0) > 0) st.useItem('ration');
    }
  }

  const fin = st.get();
  const inv = st.getInventory();
  return {
    cost, style, seed, farmEnabled,
    died: !!dead,
    deadAt: dead,
    solsSurvived: (dead ? dead.sol : clock.day) - 1,
    final: {
      water: Math.round(fin.water), cal: Math.round(fin.calories),
      potatoes: inv.potato || 0, bottles: inv.water_bottle || 0,
      filter: !!fin.waterFilter,
    },
    minWater: Math.round(minWater),
    farmWater: waterSpentOnFarm,
    harvestKg: Math.round(harvestKg * 10) / 10,
    blockedSows,
  };
}

/* ---------- chạy ---------- */

function summarize(runs) {
  const died = runs.filter((r) => r.died);
  const avg = runs.reduce((a, r) => a + r.solsSurvived, 0) / runs.length;
  return {
    alive: runs.length - died.length,
    total: runs.length,
    avgSol: avg,
    minWater: Math.min(...runs.map((r) => r.minWater)),
    farmWater: Math.round(runs.reduce((a, r) => a + r.farmWater, 0) / runs.length),
    harvest: Math.round(runs.reduce((a, r) => a + r.harvestKg, 0) / runs.length),
    firstDeath: died[0] ? died[0].deadAt : null,
  };
}

const sweep = process.argv.includes('--sweep');
const N = 16;

if (sweep) {
  console.log('Chi phi | Tot: song 35 | TB Sol | nuoc thap nhat | Do: song 35 | TB Sol | nuoc tuoi TB');
  for (const cost of WATER_COSTS) {
    const good = [];
    for (let s = 0; s < N; s++) good.push(await runOne({ cost, style: 'good', seed: s }));
    const bad = [];
    for (let s = 0; s < N; s++) bad.push(await runOne({ cost, style: 'bad', seed: s + 100 }));
    const g = summarize(good);
    const b = summarize(bad);
    console.log(
      `${String(cost).padStart(6)} | ${String(g.alive).padStart(2)}/${g.total}`.padEnd(24) +
      `| ${g.avgSol.toFixed(1).padStart(6)} | ${String(g.minWater).padStart(15)}` +
      ` | ${String(b.alive).padStart(2)}/${b.total}`.padEnd(15) +
      `| ${b.avgSol.toFixed(1).padStart(6)} | ${String(g.farmWater).padStart(12)}`,
    );
  }
} else {
  const cost = CHOSEN_COST;
  const good = [];
  for (let s = 0; s < N; s++) good.push(await runOne({ cost, style: 'good', seed: s }));
  const bad = [];
  for (let s = 0; s < N; s++) bad.push(await runOne({ cost, style: 'bad', seed: s + 100 }));
  const noFarm = [];
  for (let s = 0; s < N; s++) noFarm.push(await runOne({ cost, style: 'good', seed: s, farmEnabled: false }));

  const g = summarize(good);
  const b = summarize(bad);
  const n = summarize(noFarm);

  console.log(`=== Chi phi nuoc moi khay: ${cost} don vi ===`);
  console.log('');
  console.log('CHOI HOP LY (uong som, an du, ngu 22:00, 2 chuyen tham hiem/ngay,');
  console.log('             gieo 1 khay moi vu, che bo loc nuoc, dot hydrazine):');
  console.log(`  Song du ${SOLS} Sol: ${g.alive}/${g.total} van`);
  console.log(`  Trung binh song: ${g.avgSol.toFixed(1)} Sol`);
  console.log(`  Nuoc thap nhat tung cham: ${g.minWater}/100`);
  console.log(`  Nuoc do vao tuoi ca van: ${g.farmWater} don vi`);
  console.log(`  Khoai thu duoc: ${g.harvest} kg`);
  console.log('');
  console.log('CHOI DO (uong khi can, an khi doi, ngu 19:00, 3 chuyen/ngay,');
  console.log('        don ca 12 khay mot luot, khong che gi):');
  console.log(`  Song du ${SOLS} Sol: ${b.alive}/${b.total} van`);
  console.log(`  Trung binh song: ${b.avgSol.toFixed(1)} Sol`);
  if (b.firstDeath) {
    console.log(`  Van chet dau tien: Sol ${b.firstDeath.sol}, ${b.firstDeath.cause}` +
      (b.firstDeath.water !== undefined ? ` (nuoc ${b.firstDeath.water}, calo ${b.firstDeath.cal})` : ''));
  }
  console.log('');
  console.log('DOI CHUNG: choi hop ly nhung KHONG trong gi:');
  console.log(`  Song du ${SOLS} Sol: ${n.alive}/${n.total} van, trung binh ${n.avgSol.toFixed(1)} Sol`);
  if (n.firstDeath) console.log(`  Van chet dau tien: Sol ${n.firstDeath.sol}, ${n.firstDeath.cause}`);
  console.log('');
  const goodZero = good.filter((r) => r.blockedSows > 0).length;
  console.log(`  So van choi tot bi chan gieo vi thieu nuoc: ${goodZero}/${g.total}`);
}
