
const MIN_PER_TICK = 2;

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

async function oneRun(seed) {
  const m = await import('../src/hab-stats.js');
  // clock giả lập phải có state() như game-time.js thật
  let minutes = (7 - 1) * 60;  // Sol 7, 07:00
  const clock = {
    state: () => ({ minutes, day: 7 + Math.floor(minutes / 1440), isNight: (minutes % 1440) >= 1080 || (minutes % 1440) < 360 }),
    advance: (n) => { minutes += n; },
  };

  // tạo stats sạch, không đọc localStorage
  const st = m.createStats({ clock, initialState: {
    stats: { stamina: 80, calories: 75, water: 70, sanity: 65, power: 60, oxygen: 100, seal: 100 },
    inv: { ration: 12, water_bottle: 14, tape: 4, electronics: 3, hydrazine: 2, media: 2, potato_seed: 1 },
  }});

  const log = [];
  let sol = 7;
  let exploredToday = 0;
  let farmReady = false;
  let farmPlantedDays = 0;
  let farmHarvestCount = 0;
  let dead = null;
  let minW = 100, minC = 100, minS = 100, minP = 100;

  while (sol <= 41 && !dead) {
    // --- ban ngày: 07:00 tới 18:00 ---
    for (let hour = 7; hour < 18 && !dead; hour++) {
      const inv = st.getInventory();
      const v = st.get();

      // uống nước khi dưới 45
      if (v.water < 45 && inv.water_bottle > 0) {
        st.useItem('water_bottle');
      }
      // ăn khi calo dưới 50: ưu tiên khoai tây tự trồng
      if (v.calories < 50) {
        if ((inv.potato || 0) > 0) st.useItem('potato');
        else if ((inv.ration || 0) > 0) st.useItem('ration');
      }
      // thám hiểm tối đa 2 lượt/ngày, khi thể lực trên 45
      if (exploredToday < 2 && v.stamina > 45) {
        st.tick(60);
        clock.advance(60);
        exploredToday++;
        // rơi đồ theo bảng FIND_ITEMS của explore.js
        const roll = Math.random();
        if (roll < 0.45) {
          const pool = ['ration', 'water_bottle', 'tape', 'electronics'];
          st.addItems([{ id: pool[Math.floor(Math.random() * pool.length)], qty: 1 + Math.floor(Math.random() * 2) }]);
        } else if (roll < 0.65) {
          // không có gì
        } else if (roll < 0.80) {
          // tốn pin: trừ điện
          // tốn pin: bỏ qua trong sim, không ảnh hưởng sống còn
        }
        continue;
      }

      // cuối ngày: tưới và chăm vườn nếu đã mở khoá
      if (hour === 17 && farmReady) {
        const u = st.getUnlocks();
        if (u.farm && st.getInventory().water_bottle > 0) {
          st.tick(30);
        }
        if (farmPlantedDays > 0) { farmPlantedDays--; }
      }

      st.tick(60);
      clock.advance(60);
      const n = st.get();
      minW = Math.min(minW, n.water); minC = Math.min(minC, n.calories);
      minS = Math.min(minS, n.stamina); minP = Math.min(minP, n.power);
      if (!n.alive) dead = { sol, hour, cause: 'het chi so' };
    }

    if (dead) break;

    // --- dự báo trước khi ngủ ---
    const fc = st.forecastUntil(7 * 60);
    if (fc && fc.deathRisk) {
      log.push(`Sol ${sol}: canh bao dự báo ${fc.deathRisk}`);
    }

    // --- ngủ tới 07:00 hôm sau: từ 18:00 là 13 tiếng ---
    const before = st.get();
    st.sleepOver(13);
    clock.advance(13 * 60);
    sol++;

    const after = st.get();
    if (!after.alive) { dead = { sol, cause: 'het chi so qua dem' }; break; }

    // đánh giá chất lượng đêm
    if (after.water <= 0) log.push(`Sol ${sol}: thuc day khat nuoc`);
    if (after.calories <= 0) log.push(`Sol ${sol}: thuc day doi`);
    if (after.stamina < 40) log.push(`Sol ${sol}: thuc day met (the luc ${after.stamina})`);

    // mô phỏng nông trại: gieo Sol 8, chín sau 3 đêm, thu rồi gieo lại
    if (sol >= 8) {
      if (farmPlantedDays === 0) {
        farmPlantedDays = 4;
      } else if (farmPlantedDays === 1) {
        const qty = 12 * (2 + Math.floor(Math.random() * 2));
        st.addItems([{ id: 'potato', qty }]);
        farmHarvestCount += qty;
        farmPlantedDays = 4;
      } else {
        farmPlantedDays--;
      }
    }

    exploredToday = 0;
  }

  const fin = st.get();
  return {
    seed,
    died: !!dead,
    deadAt: dead,
    solsSurvived: sol - 7,
    final: {
      stamina: Math.round(fin.stamina), calories: Math.round(fin.calories),
      water: Math.round(fin.water), sanity: Math.round(fin.sanity),
      power: Math.round(fin.power), oxygen: Math.round(fin.oxygen), seal: Math.round(fin.seal),
    },
    min: { water: Math.round(minW), cal: Math.round(minC), stam: Math.round(minS), power: Math.round(minP) },
    farmHarvest: farmHarvestCount,
    warnings: log.slice(0, 6),
  };
}

(async () => {
  const runs = [];
  for (let i = 0; i < 40; i++) runs.push(await oneRun(i));
  console.log(JSON.stringify(runs));
})();
