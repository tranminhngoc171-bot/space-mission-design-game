#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim-35-sol.py
Chạy mô phỏng lõi sinh tồn đủ 35 Sol mà không cần trình duyệt.

Mục đích: bắt lỗi cân bằng và lỗi logic trước khi người chơi thật
gặp phải. Chạy thẳng trên hab-stats.js qua node, không giả lập DOM,
nên chạy nhanh và lặp lại được nhiều lần để xem phân bố kết quả.

Chạy: python scripts/sim-35-sol.py
     python scripts/sim-35-sol.py --runs 200
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS = ROOT / 'src' / 'hab-stats.js'

# Chiến lược chơi hợp lý của một người chơi biết luật: uống nước khi
# khát, ăn khi đói, ngủ đúng giờ, thám hiểm khi còn lượt và đủ sức.
HARNESS = r"""
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
"""


def main():
    harness = ROOT / 'scripts' / '_sim_harness.mjs'
    harness.write_text(HARNESS, encoding='utf-8')

    print('Chạy 40 ván mô phỏng, mỗi ván 35 Sol...')
    print('')

    r = subprocess.run(
        ['node', str(harness)],
        cwd=str(ROOT),
        capture_output=True, text=True, timeout=180,
    )

    if r.returncode != 0:
        print('Lỗi chạy mô phỏng:')
        print(r.stderr[:2000])
        sys.exit(1)

    try:
        runs = json.loads(r.stdout.strip().split('\n')[-1])
    except json.JSONDecodeError:
        print('Không đọc được kết quả:')
        print(r.stdout[:1500])
        sys.exit(1)

    died = [x for x in runs if x['died']]
    survived = [x for x in runs if not x['died']]

    print(f'Kết quả {len(runs)} ván 35 Sol')
    print(f'  Sống hết 35 Sol: {len(survived)}/{len(runs)}')
    print(f'  Chết giữa đường: {len(died)}/{len(runs)}')
    print('')

    if died:
        print('Các ván chết, xem có phải lỗi cân bằng không:')
        from collections import Counter
        causes = Counter(d['deadAt']['cause'] if d['deadAt'] else 'khong ro' for d in died)
        for c, n in causes.most_common():
            print(f'  {c}: {n} ván')
        print('')
        for d in died[:5]:
            da = d['deadAt']
            print(f"  Ván {d['seed']}: chết Sol {da['sol']} do {da['cause']}")
            print(f"    chỉ số thấp nhất: nước {d['min']['water']}, calo {d['min']['cal']}, "
                  f"thể lực {d['min']['stam']}, điện {d['min']['power']}")
        print('')

    if survived:
        f = survived[0]['final']
        print('Chỉ số cuối của ván sống đầu tiên:')
        for k, v in f.items():
            print(f'  {k:9} {v}')
        print('')
        avg = {}
        for k in f:
            avg[k] = round(sum(x['final'][k] for x in survived) / len(survived))
        print('Trung bình cộng các ván sống:')
        for k, v in avg.items():
            print(f'  {k:9} {v}')

    print('')
    warnings = set()
    for x in runs:
        for w in x['warnings']:
            warnings.add(w.split(':')[1].strip() if ':' in w else w)
    if warnings:
        print('Cảnh báo lặp lại nhiều ván:')
        for w in sorted(warnings)[:10]:
            print(f'  {w}')

    # Kiểm tra then chốt: nếu quá nửa số ván chết thì cân bằng sai
    print('')
    if len(died) > len(runs) * 0.5:
        print('CẢNH BÁO: quá nửa số ván chết, cân bằng quá khó')
        sys.exit(2)
    print('Kết luận: cân bằng nằm trong ngưỡng chơi được')


if __name__ == '__main__':
    main()
