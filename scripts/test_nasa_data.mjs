/* ============================================================
   scripts/test_nasa_data.mjs
   Kiểm tra bộ dữ liệu NASA cho sứ mệnh giải cứu Sao Hỏa.
   Validates the NASA dataset behind the Mars rescue mission.

   Chạy / run:  node scripts/test_nasa_data.mjs
   Thoát mã 0 nếu mọi mục PASS, mã 1 nếu có mục FAIL.
   Exits 0 when every check passes, 1 when anything fails.
   ============================================================ */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import {
  loadRescueData,
  tsiolkovskyFuelFraction,
  signalDelayMinutes,
  marsDistanceForSol,
  validateRescueDesign,
  summarizeModules,
  NASA_CONSTANTS,
  REQUIRED_DELTA_V_MS,
} from '../src/nasa-data.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');

let passCount = 0;
let failCount = 0;
const lines = [];

function record(ok, label, detail) {
  if (ok) passCount++;
  else failCount++;
  const tag = ok ? 'PASS' : 'FAIL';
  const body = detail ? label + '  [' + detail + ']' : label;
  const line = tag.padEnd(5) + ' ' + body;
  lines.push(line);
  console.log(line);
}

function section(title) {
  const line = '\n--- ' + title + ' ---';
  lines.push(line);
  console.log(line);
}

/* ------------------------------------------------------------
   1. Nạp ba file JSON / load the three JSON files
   ------------------------------------------------------------ */
section('1. Nạp dữ liệu / Dataset loading');

const JSON_FILES = [
  'src/data/nasa/rescue_mission.json',
  'src/data/nasa/rescue_modules.json',
  'src/data/nasa/crew_roles.json',
];

for (const rel of JSON_FILES) {
  let ok = false;
  let detail = '';
  try {
    const raw = readFileSync(join(ROOT, rel), 'utf8');
    const parsed = JSON.parse(raw);
    ok = parsed && typeof parsed === 'object';
    detail = Object.keys(parsed).length + ' khoá / keys';
  } catch (err) {
    detail = String(err.message || err);
  }
  record(ok, 'Đọc được / readable: ' + rel, detail);
}

const data = loadRescueData();

record(
  data.mission && Array.isArray(data.mission.delta_v_legs) && data.mission.delta_v_legs.length === 4,
  'rescue_mission.json có 4 chặng delta-v / has 4 delta-v legs',
  data.mission.delta_v_legs.length + ' chặng / legs'
);

record(
  Array.isArray(data.modules.modules) && data.modules.modules.length >= 8 && data.modules.modules.length <= 12,
  'rescue_modules.json có 8 tới 12 module / has 8 to 12 modules',
  data.modules.modules.length + ' module'
);

record(
  Array.isArray(data.crew.roles) && data.crew.roles.length === 3,
  'crew_roles.json có đủ 3 vai trò / has all 3 roles',
  data.crew.roles.map((r) => r.id).join(', ')
);

// Mọi module phải có đủ trường bắt buộc và tradeoff song ngữ
const REQUIRED_MODULE_FIELDS = [
  'id',
  'name_vi',
  'name_en',
  'mass_kg',
  'power_w',
  'cost_musd',
  'tradeoff_vi',
  'tradeoff_en',
  'source',
];
const badModules = data.modules.modules.filter((m) =>
  REQUIRED_MODULE_FIELDS.some((f) => m[f] === undefined || m[f] === null || m[f] === '')
);
record(
  badModules.length === 0,
  'Mọi module đủ trường bắt buộc / every module has required fields',
  badModules.length ? 'thiếu / missing: ' + badModules.map((m) => m.id).join(', ') : REQUIRED_MODULE_FIELDS.length + ' trường / fields'
);

// Mọi con số chặng delta-v phải có source
const legsMissingSource = data.mission.delta_v_legs.filter((l) => !l.source || !l.source.trim());
record(
  legsMissingSource.length === 0,
  'Mọi chặng delta-v có trường source / every delta-v leg cites a source',
  legsMissingSource.length ? legsMissingSource.map((l) => l.id).join(', ') : '4/4'
);

/* ------------------------------------------------------------
   2. Tsiolkovsky
   ------------------------------------------------------------ */
section('2. Phương trình Tsiolkovsky / Rocket equation');

const fuel320 = tsiolkovskyFuelFraction(5600, 320);
record(
  Math.abs(fuel320 - 83.2) <= 2,
  'Isp 320, dv 5600 m/s cho khoảng 83 phần trăm / yields about 83 percent',
  'tính được / got ' + fuel320.toFixed(2) + ' %'
);

// Đối chiếu thêm các ô trong bảng của tài liệu nguồn
const TABLE = [
  { isp: 300, dv: 3600, expect: 70.6 },
  { isp: 300, dv: 5600, expect: 85.1 },
  { isp: 320, dv: 3600, expect: 68.3 },
  { isp: 320, dv: 5600, expect: 83.2 },
  { isp: 450, dv: 3600, expect: 55.8 },
  { isp: 450, dv: 5600, expect: 71.9 },
];
const tableFails = TABLE.filter((row) => Math.abs(tsiolkovskyFuelFraction(row.dv, row.isp) - row.expect) > 0.5);
record(
  tableFails.length === 0,
  'Khớp toàn bộ bảng nhiên liệu của docs mục 5.2 nhóm F / matches the full doc fuel table',
  tableFails.length ? 'lệch / off: ' + tableFails.map((r) => 'Isp ' + r.isp).join(', ') : TABLE.length + '/' + TABLE.length
);

// Isp 900 phải rẻ hơn Isp 320 rõ rệt
const fuel900 = tsiolkovskyFuelFraction(5600, 900);
record(
  fuel900 > 40 && fuel900 < 60,
  'Isp 900, dv 5600 m/s rơi vào khoảng 40 tới 60 phần trăm / lands between 40 and 60 percent',
  'tính được / got ' + fuel900.toFixed(2) + ' %'
);

record(
  tsiolkovskyFuelFraction(0, 320) === 0,
  'dv bằng 0 thì nhiên liệu bằng 0 / zero delta-v means zero propellant',
  '0 %'
);

/* ------------------------------------------------------------
   3. Trễ tín hiệu / signal delay
   ------------------------------------------------------------ */
section('3. Trễ tín hiệu / Signal delay');

const delay225 = signalDelayMinutes(225000000);
record(
  Math.abs(delay225 - 12.5) <= 0.5,
  '225 triệu km cho khoảng 12,5 phút một chiều / 225 million km gives about 12.5 one-way minutes',
  'tính được / got ' + delay225.toFixed(3) + ' phút / min'
);

const near = signalDelayMinutes(54600000);
record(
  Math.abs(near - 3.0) <= 0.3,
  '54,6 triệu km cho khoảng 3,0 phút / 54.6 million km gives about 3.0 minutes',
  'tính được / got ' + near.toFixed(3) + ' phút / min'
);

const far = signalDelayMinutes(401000000);
record(
  Math.abs(far - 22.3) <= 1.0,
  '401 triệu km cho khoảng 22,3 phút / 401 million km gives about 22.3 minutes',
  'tính được / got ' + far.toFixed(3) + ' phút / min'
);

record(
  Math.abs(NASA_CONSTANTS.speed_of_light_km_s - 299792.458) < 1e-6,
  'Hằng số tốc độ ánh sáng đúng 299 792,458 km/s / light speed constant is exact',
  String(NASA_CONSTANTS.speed_of_light_km_s)
);

/* ------------------------------------------------------------
   4. Khoảng cách theo sol / distance per sol
   ------------------------------------------------------------ */
section('4. Khoảng cách Trái Đất Sao Hỏa theo sol / Earth Mars distance per sol');

// Quét trọn một chu kỳ giao hội để tìm cận và viễn
let minKm = Infinity;
let maxKm = 0;
for (let sol = 0; sol < 780; sol += 1) {
  const d = marsDistanceForSol(sol);
  if (d < minKm) minKm = d;
  if (d > maxKm) maxKm = d;
}

record(
  minKm > 50e6 && minKm < 110e6,
  'Khoảng cách nhỏ nhất trong một chu kỳ rơi vào 50 tới 110 triệu km / perigee distance within 50 to 110 million km',
  'nhỏ nhất / min ' + (minKm / 1e6).toFixed(1) + ' triệu km / Mkm'
);

record(
  maxKm > 350e6 && maxKm < 410e6,
  'Khoảng cách lớn nhất trong một chu kỳ rơi vào 350 tới 410 triệu km / apogee distance within 350 to 410 million km',
  'lớn nhất / max ' + (maxKm / 1e6).toFixed(1) + ' triệu km / Mkm'
);

record(
  Number.isFinite(marsDistanceForSol(0)) && marsDistanceForSol(0) > 0,
  'marsDistanceForSol trả số dương ở sol 0 / returns a positive number at sol 0',
  (marsDistanceForSol(0) / 1e6).toFixed(1) + ' triệu km / Mkm'
);

/* ------------------------------------------------------------
   5. Kiểm tra thiết kế / design validation
   ------------------------------------------------------------ */
section('5. Kiểm tra thiết kế / Design validation');

// Thiết kế hợp lệ: động cơ hạt nhân Isp 900, đủ nhiên liệu, đủ điện, đủ nhu yếu phẩm,
// phóng bằng SLS Block 1 (70 000 kg lên LEO).
// Valid design: nuclear engine at Isp 900, enough propellant, power, consumables,
// launched on SLS Block 1 with its 70 000 kg LEO capacity.
const VALID = {
  moduleIds: [
    'prop_nuclear_ntp_900',
    'tank_propellant_main',
    'power_solar_rosa',
    'comms_high_gain',
    'life_moxie_filter',
    'life_eclss_recycler',
    'shield_radiation',
    'supplies_crew_three',
    'sensor_edl_suite',
  ],
  launcherId: 'sls_block1',
  crewCount: 3,
};

const validResult = validateRescueDesign(VALID);
record(
  validResult.pass === true,
  'Thiết kế hợp lệ vượt qua kiểm tra / valid design passes every check',
  validResult.pass
    ? 'wet ' +
        Math.round(validResult.summary.wetMass_kg) +
        ' kg, dv ' +
        validResult.summary.delta_v_available_ms +
        ' m/s'
    : 'lỗi / failures: ' + validResult.failures.map((f) => f.code).join(', ')
);

record(
  validResult.failures.length === 0,
  'Thiết kế hợp lệ không có mục failures / no failures on the valid design',
  String(validResult.failures.length)
);

record(
  validResult.warnings.length === 0,
  'Thiết kế hợp lệ không có cảnh báo / no warnings on the valid design',
  validResult.warnings.length
    ? validResult.warnings.map((w) => w.code).join(', ')
    : '0'
);

record(
  validResult.summary.delta_v_available_ms >= REQUIRED_DELTA_V_MS,
  'Delta-v khả dụng phủ ngân sách 6 650 m/s / available delta-v covers the 6650 m/s budget',
  validResult.summary.delta_v_available_ms + ' m/s so với / vs ' + REQUIRED_DELTA_V_MS + ' m/s'
);

// Thiết kế quá nặng: cùng tàu nhưng phóng bằng Falcon 9 Dedicated (10 000 kg).
// Overweight design: same ship but on a Falcon 9 Dedicated with 10 000 kg capacity.
const OVERWEIGHT = {
  moduleIds: VALID.moduleIds.slice(),
  launcherId: 'falcon9_dedicated',
  crewCount: 3,
};

const heavyResult = validateRescueDesign(OVERWEIGHT);
const heavyCodes = heavyResult.failures.map((f) => f.code);
record(
  heavyResult.pass === false,
  'Thiết kế quá nặng bị chặn / overweight design is rejected',
  'khối lượng ướt / wet ' + Math.round(heavyResult.summary.wetMass_kg) + ' kg'
);

record(
  heavyCodes.includes('overweight_launch'),
  'Lỗi nêu đúng mã overweight_launch / reports the overweight_launch code',
  heavyCodes.join(', ') || 'không có / none'
);

// Thiết kế thiếu động cơ và thiếu ăng-ten phải bị chặn, để chắc bộ kiểm tra không rỗng.
// A design with no engine and no antenna must be rejected, proving the checker is not a no-op.
const EMPTY = { moduleIds: ['supplies_crew_three'], launcherId: 'sls_block1' };
const emptyResult = validateRescueDesign(EMPTY);
const emptyCodes = emptyResult.failures.map((f) => f.code);
record(
  emptyResult.pass === false && emptyCodes.includes('no_engine') && emptyCodes.includes('no_comms'),
  'Thiết kế thiếu động cơ và ăng-ten bị chặn / design without engine or antenna is rejected',
  emptyCodes.join(', ')
);

/* ------------------------------------------------------------
   6. Tổng kết / summary
   ------------------------------------------------------------ */
section('6. Tổng kết / Summary');

const total = passCount + failCount;
console.log('\n' + passCount + '/' + total + ' PASS, ' + failCount + ' FAIL');

// Ba con số quan trọng nhất cho báo cáo cuối.
// The three headline numbers for the final report.
console.log('');
console.log('Ba con số then chốt / three headline numbers:');
console.log(
  '  Nhiên liệu cho Isp 320 và 5 600 m/s: ' +
    fuel320.toFixed(1) +
    ' % khối lượng / propellant share of mass'
);
console.log(
  '  Trễ tín hiệu một chiều ở 225 triệu km: ' +
    delay225.toFixed(1) +
    ' phút / one-way minutes at 225 million km'
);
console.log(
  '  Delta-v cộng dồn cả hành trình: ' +
    REQUIRED_DELTA_V_MS +
    ' m/s, khả dụng của thiết kế mẫu: ' +
    validResult.summary.delta_v_available_ms +
    ' m/s'
);

if (failCount > 0) {
  console.log('\nCó mục FAIL, sửa công thức chứ không nới ngưỡng. / Failures above: fix the formula, not the threshold.');
  process.exit(1);
}
console.log('\nToàn bộ PASS. / All checks passed.');
process.exit(0);
