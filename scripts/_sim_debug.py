#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim-hab-balance.py
Mô phỏng game để đo xem bộ số cân bằng có hợp lý không.

Không cần giao diện, chỉ chạy toán. Ba chiến thuật người chơi khác
nhau, mỗi cái chạy nhiều lần với yếu tố ngẫu nhiên, xem ai sống được
tới đâu. Nếu chiến thuật ẩu cũng sống ngon thì game không có thử thách.
Nếu chiến thuật giỏi cũng chết sạch thì game ức chế, không ai muốn chơi.

Chạy: python scripts/sim-hab-balance.py
"""

import random
import statistics

# ---------------------------------------------------------------- hằng số

HOURS_PER_DAY = 24
WATER_DRAIN = 3.5
CAL_DRAIN = 2.5
STAM_DRAIN = 3.5
SANITY_DRAIN = 1.5
STAM_SLEEP_GAIN = 10.0

# Hệ thống thu hồi nước của trạm. Trên ISS thật là 93 phần trăm.
# Không có số này thì ai cũng chết ở Sol 8, không bao giờ tới Sol 35.
WATER_RECYCLER = 0.70

WATER_EMPTY_STAM_PENALTY = 5.0
WATER_DEATH_HOURS = 12
CAL_DEATH_HOURS = 24
CAL_STAM_CAP = 50

POWER_SOLAR_DAY = 8.0
POWER_SOLAR_STORM = 3.2
POWER_DRAIN = 3.0
OXY_DRAIN_NO_POWER = 6.0

RATION_CAL = 45
POTATO_CAL = 45          # một củ khoai lớn, ngang một gói khẩu phần
FARM_PLOTS = 12          # số ô đất
FARM_CYCLE_SOL = 5       # số Sol từ gieo tới thu hoạch
FARM_YIELD_PER_PLOT = 1.5  # củ mỗi ô mỗi vụ (có yếu tố ngẫu nhiên)
FARM_UNLOCK_SOL = 9      # Sol mở được nông trại nếu chơi giỏi
BOTTLE_WATER = 40
MEDIA_SANITY = 25

START = dict(stamina=80, calories=75, water=70, sanity=65, power=60, oxygen=100, seal=100)
START_INV = dict(ration=12, water_bottle=14, tape=4, electronics=3, hydrazine=2, media=2)

# Tỉ lệ một ngày có bão bụi. Bão làm pin chỉ sạc còn 40 phần trăm.
STORM_CHANCE = 0.28


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def run_one(strategy, max_sol=35, seed=None, verbose=False, kind='balanced'):
    """Chạy một ván. Trả (số sol sống được, nguyên nhân chết)."""
    if seed is not None:
        random.seed(seed)

    s = dict(START)
    inv = dict(START_INV)
    zero_water_hours = 0
    zero_cal_hours = 0

    # mỗi ngày có thể có bão
    storm_today = random.random() < STORM_CHANCE

    for sol in range(1, max_sol + 1):
        storm_today = random.random() < STORM_CHANCE

        for hour in range(24):
            is_day = 6 <= hour < 18

            # ---- tiêu hao ----
            s["water"] -= WATER_DRAIN * (1 - WATER_RECYCLER)
            s["calories"] -= CAL_DRAIN

            sleeping = 22 <= hour or hour < 6
            if sleeping:
                s["stamina"] += STAM_SLEEP_GAIN
            else:
                s["stamina"] -= STAM_DRAIN
                s["sanity"] -= SANITY_DRAIN

            if s["water"] <= 0:
                s["stamina"] -= WATER_EMPTY_STAM_PENALTY
                zero_water_hours += 1
            else:
                zero_water_hours = 0

            if s["calories"] <= 0:
                zero_cal_hours += 1
            else:
                zero_cal_hours = 0

            # ---- điện ----
            if is_day:
                s["power"] += POWER_SOLAR_STORM if storm_today else POWER_SOLAR_DAY
            # người chơi khéo biết tắt bớt thiết bị ban đêm để dành điện
            drain = POWER_DRAIN
            if kind in ("planner", "balanced") and not is_day:
                drain = POWER_DRAIN * 0.6
            s["power"] -= drain

            if s["power"] <= 0:
                s["oxygen"] -= OXY_DRAIN_NO_POWER

            # ---- kẹp ----
            stam_cap = CAL_STAM_CAP if s["calories"] <= 0 else 100
            s["stamina"] = clamp(s["stamina"], 0, stam_cap)
            for k in ("calories", "water", "sanity", "oxygen"):
                s[k] = clamp(s[k], 0, 100)
            s["power"] = clamp(s["power"], 0, 100)

            # ---- thám hiểm: tìm lương thực ở các bãi đáp cũ ----
            # Cần bước này vì lương khởi điểm chỉ đủ tới Sol 9, còn vụ
            # khoai đầu tiên phải tới Sol 14. Thiếu nó là khoảng trống
            # 5 ngày không có gì ăn, ai cũng chết dù chơi giỏi.
            if kind != "careless" and hour == 15:
                # mỗi ngày đi một chuyến, tìm được gói khẩu phần
                found = 0
                for _ in range(3):
                    if random.random() < 0.55:
                        found += 1
                inv["ration"] = inv.get("ration", 0) + found
                s["stamina"] = clamp(s["stamina"] - 18, 0, 100)

            # ---- nông trại: mỗi vụ 5 Sol, thu hoạch vào buổi trưa ----
            farm_open = (kind == "planner" and sol >= FARM_UNLOCK_SOL) or (kind == "balanced" and sol >= FARM_UNLOCK_SOL + 4)
            if farm_open and hour == 12 and sol % FARM_CYCLE_SOL == 0:
                harvest = 0
                for _ in range(FARM_PLOTS):
                    if random.random() < FARM_YIELD_PER_PLOT:
                        harvest += 1
                inv["potato"] = inv.get("potato", 0) + harvest

            # ---- người chơi hành động theo chiến thuật ----
            s, inv = strategy(s, inv, hour, sleep_hour_this_turn=None)

            # ---- kiểm tra chết ----
            if s["oxygen"] <= 0:
                return sol, "ngạt thở"
            if zero_water_hours >= WATER_DEATH_HOURS:
                return sol, "khát nước"
            if zero_cal_hours >= CAL_DEATH_HOURS:
                return sol, "đói"

            if verbose and hour % 6 == 0:
                print(f"    sol {sol} h{hour}: "
                      f"stam={s['stamina']:.0f} cal={s['calories']:.0f} "
                      f"water={s['water']:.0f} san={s['sanity']:.0f} "
                      f"pow={s['power']:.0f} oxy={s['oxygen']:.0f}")

    return max_sol, None


def make_strategy(kind):
    """Trả hàm hành động theo kiểu người chơi."""

    def act(s, inv, hour, sleep_hour_this_turn, sol=0):
        # ---- uống nước ----
        threshold = {"careless": 10, "balanced": 40, "planner": 50}[kind]
        if s["water"] < threshold and inv["water_bottle"] > 0:
            inv["water_bottle"] -= 1
            s["water"] = clamp(s["water"] + BOTTLE_WATER, 0, 100)

        # ---- ăn: ưu tiên khoai tự trồng vì không mất gì ----
        if s["calories"] < threshold:
            if inv.get("potato", 0) > 0:
                inv["potato"] -= 1
                s["calories"] = clamp(s["calories"] + POTATO_CAL, 0, 100)
            elif inv["ration"] > 0:
                inv["ration"] -= 1
                s["calories"] = clamp(s["calories"] + RATION_CAL, 0, 100)

        # ---- tinh thần ----
        if kind != "careless" and s["sanity"] < 35 and inv["media"] > 0:
            inv["media"] -= 1
            s["sanity"] = clamp(s["sanity"] + MEDIA_SANITY, 0, 100)

        # ---- chế tạo nước ----
        # Planner đốt đều đặn vào buổi trưa. Balanced chỉ đốt khi nước
        # đã xuống thấp, do dự lâu hơn nên có thể trễ.
        if kind == "planner" and hour == 12:
            if inv["hydrazine"] > 0 and s["sanity"] >= 40:
                inv["hydrazine"] -= 1
                inv["water_bottle"] += 5
                if random.random() < 0.08:
                    s["seal"] = clamp(s["seal"] - 15, 0, 100)
        elif kind == "balanced" and hour == 12 and inv["water_bottle"] < 8:
            if inv["hydrazine"] > 0 and s["sanity"] >= 40:
                inv["hydrazine"] -= 1
                inv["water_bottle"] += 5
                if random.random() < 0.15:
                    s["seal"] = clamp(s["seal"] - 15, 0, 100)

        return s, inv

    return act


def run_batch(kind, runs=5000):
    results = []
    deaths = {}
    for i in range(runs):
        sol, cause = run_one(make_strategy(kind), kind=kind)
        results.append(sol)
        if cause:
            deaths[cause] = deaths.get(cause, 0) + 1
    return results, deaths


def main():
    print("Mô phỏng cân bằng trạm Hab")
    print("Thông số: nước -3.5/giờ, calo -2.5/giờ, thể lực -3.5/giờ thức")
    print(f"Tỉ lệ ngày có bão bụi: {STORM_CHANCE*100:.0f} phần trăm")
    print("Mỗi chiến thuật chạy 5000 ván, mục tiêu sống tới Sol 35")
    print("=" * 74)
    print(f"{'chiến thuật':12} {'Sol 15':>8} {'Sol 25':>8} {'Sol 35':>8} "
          f"{'TB sống':>9}  nguyên nhân chết")
    print("-" * 74)

    for kind in ("careless", "balanced", "planner"):
        results, deaths = run_batch(kind, 5000)
        p15 = sum(1 for r in results if r >= 15) / len(results) * 100
        p25 = sum(1 for r in results if r >= 25) / len(results) * 100
        p35 = sum(1 for r in results if r >= 35) / len(results) * 100
        avg = statistics.mean(results)
        top = sorted(deaths.items(), key=lambda x: -x[1])[:2]
        top_str = ", ".join(f"{c} {n}" for c, n in top) if top else "không chết"
        print(f"{kind:12} {p15:7.1f}% {p25:7.1f}% {p35:7.1f}% {avg:8.1f}  {top_str}")

    print("=" * 74)
    print("")
    print("Tiêu chí đánh giá:")
    print("  careless tới Sol 15 phải dưới 40 phần trăm")
    print("  planner tới Sol 35 phải trên 60 phần trăm")
    print("  balanced nằm giữa hai bên")


if __name__ == "__main__":
    import sys
    if "--debug" in sys.argv:
        sol, cause = run_one(make_strategy("balanced"), kind="balanced", verbose=True)
        print(f"ket qua: sol {sol}, chet vi {cause}")
    else:
        main()
