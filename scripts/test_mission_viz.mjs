/* ============================================================
   test_mission_viz.mjs
   Kiểm tra phần tính toán của bản đồ sứ mệnh, bằng node thuần,
   không cần trình duyệt.

   Chạy: node scripts/test_mission_viz.mjs

   Chỉ import mission-math.js. File đó không đụng tới DOM, nên test
   chạy được trong môi trường không có window hay canvas.
   ============================================================ */

import {
  AU_KM,
  TRANSFER_DAYS,
  TRANSFER_ORBIT,
  EARTH_ORBIT,
  MARS_ORBIT,
  EARTH_PATH,
  MARS_PATH,
  EARTH_PERI_DEG,
  MARS_PERI_DEG,
  MARS_M0,
  PHASE_AT_LAUNCH,
  DELAY_BAND,
  TCM,
  missionState,
  earthAt,
  marsAt,
  transferAt,
  orbitState,
  separationAu,
  delayMinutes,
  auToKm,
  rangeExtremes,
  tcmPassed,
  tcmNext,
  solveKepler,
  missionClock,
  normDeg,
  meanMotionDeg,
  formatNumber,
} from '../src/mission-math.js';

/* ---------- khung test tối giản ---------- */

let pass = 0;
let fail = 0;
const failures = [];

function ok(name, cond, detail) {
  if (cond) {
    pass++;
    console.log(`  PASS  ${name}`);
  } else {
    fail++;
    failures.push(name);
    console.log(`  FAIL  ${name}${detail ? '  ' + detail : ''}`);
  }
}

function near(name, actual, expected, tol, unit) {
  const d = Math.abs(actual - expected);
  ok(
    name,
    d <= tol,
    `nhận ${fmt(actual)} dự kiến ${fmt(expected)} lệch ${fmt(d)} ${unit || ''}`.trim()
  );
}

function between(name, actual, lo, hi, unit) {
  ok(
    name,
    actual >= lo && actual <= hi,
    `nhận ${fmt(actual)}, cần trong khoảng ${fmt(lo)} tới ${fmt(hi)} ${unit || ''}`.trim()
  );
}

function fmt(v) {
  return typeof v === 'number' ? v.toFixed(4) : String(v);
}

function section(title) {
  console.log('\n' + title);
}

/* ---------- 1. hằng số ---------- */

section('1. Hằng số quỹ đạo');

near('AU dài 149 597 870,7 km', AU_KM, 149597870.7, 0.05, 'km');
near('thời gian bay 258,9 ngày', TRANSFER_DAYS, 258.9, 1e-9, 'ngày');
near('bán trục lớn Sao Hỏa', MARS_ORBIT.a, 1.523679, 1e-6, 'AU');
near('tâm sai Sao Hỏa', MARS_ORBIT.e, 0.0934, 1e-6);
near('chu kỳ Sao Hỏa', MARS_ORBIT.period, 686.971, 1e-6, 'ngày');
near('bán trục lớn Trái Đất', EARTH_ORBIT.a, 1.0, 1e-9, 'AU');
near('tâm sai Trái Đất', EARTH_ORBIT.e, 0.016708, 1e-6);

/* Bán trục lớn đường chuyển tiếp khoá theo chu kỳ 517,8 ngày, đúng
   thời gian bay 258,9 ngày. Neo theo trung bình hai bán trục lớn sẽ
   cho 259,0 ngày, xấp xỉ nhưng không khít. */
const expectedA = Math.cbrt(Math.pow((2 * TRANSFER_DAYS) / EARTH_ORBIT.period, 2));
near('bán trục lớn chuyển tiếp 1,2620 AU', TRANSFER_ORBIT.a, expectedA, 1e-9, 'AU');
near('bán trục lớn chuyển tiếp xấp xỉ 1,262 AU', TRANSFER_ORBIT.a, 1.262, 0.002, 'AU');
between('tâm sai chuyển tiếp trong khoảng hợp lý', TRANSFER_ORBIT.e, 0.15, 0.30);

/* Nửa chu kỳ của ellipse chuyển tiếp phải bằng đúng 258,9 ngày. Đây
   là phép kiểm tra quan trọng nhất của cả file: nó xác nhận hình học
   đường bay khớp con số thời gian bay của nhiệm vụ. */
const keplerHalf = 0.5 * EARTH_ORBIT.period * Math.pow(TRANSFER_ORBIT.a, 1.5);
near('nửa chu kỳ chuyển tiếp đúng 258,9 ngày', keplerHalf, TRANSFER_DAYS, 1e-6, 'ngày');

/* Viễn điểm đường bay nên xấp xỉ bán trục lớn Sao Hỏa. Không bằng
   đúng, vì thời gian bay 258,9 ngày mới là ràng buộc cứng. */
near('viễn điểm chuyển tiếp xấp xỉ 1,52 AU', TRANSFER_ORBIT.rArrive, 1.52, 0.03, 'AU');

/* ---------- 2. giải phương trình Kepler ---------- */

section('2. Giải phương trình Kepler');

for (const e of [0, 0.016708, 0.0934, 0.2577]) {
  let worst = 0;
  for (let M = 0; M < 360; M += 7) {
    const E = solveKepler(M, e);
    const back = normDeg((E - e * Math.sin(E)) * (180 / Math.PI));
    let diff = Math.abs(back - normDeg(M));
    if (diff > 180) diff = 360 - diff;
    if (diff > worst) worst = diff;
  }
  ok(`Kepler e=${e}: sai số nghịch đảo dưới 1e-9 độ`, worst < 1e-9, `sai số ${worst.toExponential(2)} độ`);
}

ok('Kepler M=0 cho E=0', Math.abs(solveKepler(0, 0.0934)) < 1e-12);
ok(
  'Kepler M=180 cho E=180',
  Math.abs(Math.abs(solveKepler(180, 0.0934)) - Math.PI) < 1e-9
);

/* ---------- 3. hình học quỹ đạo hành tinh ---------- */

section('3. Hình học quỹ đạo hành tinh');

/* Trái Đất: cận điểm bằng a(1-e), viễn điểm bằng a(1+e). */
near('Trái Đất cận điểm 0,9833 AU', earthAt(0).r, 1.0 * (1 - 0.016708), 1e-6, 'AU');

/* Sau nửa chu kỳ Trái Đất phải ở viễn điểm. */
const earthHalf = earthAt(EARTH_ORBIT.period / 2);
near('Trái Đất viễn điểm sau nửa chu kỳ', earthHalf.r, 1.0 * (1 + 0.016708), 1e-6, 'AU');

/* Quỹ đạo khép kín: sau đúng một chu kỳ phải về chỗ cũ. */
const earthFull = earthAt(EARTH_ORBIT.period);
near('Trái Đất về chỗ cũ sau một chu kỳ (bán kính)', earthFull.r, earthAt(0).r, 1e-6, 'AU');
/* So kinh độ phải theo khoảng cách vòng, vì 360 độ và 0 độ là một
   điểm. So thẳng số sẽ báo hỏng ở đúng chỗ hình học đúng. */
let lonDiff = Math.abs(earthFull.lonDeg - earthAt(0).lonDeg) % 360;
if (lonDiff > 180) lonDiff = 360 - lonDiff;
ok('Trái Đất về chỗ cũ sau một chu kỳ (kinh độ)', lonDiff < 1e-6, `lệch ${lonDiff.toExponential(2)} độ`);

/* Sao Hỏa: kiểm tra cận điểm và viễn điểm. */
let marsMin = Infinity;
let marsMax = -Infinity;
for (let d = 0; d <= MARS_ORBIT.period; d += 1) {
  const r = marsAt(d).r;
  if (r < marsMin) marsMin = r;
  if (r > marsMax) marsMax = r;
}
near('Sao Hỏa cận điểm a(1-e)', marsMin, MARS_ORBIT.a * (1 - MARS_ORBIT.e), 2e-3, 'AU');
near('Sao Hỏa viễn điểm a(1+e)', marsMax, MARS_ORBIT.a * (1 + MARS_ORBIT.e), 2e-3, 'AU');

/* Mọi điểm trên quỹ đạo Sao Hỏa phải nằm giữa hai mốc đó. */
let allInside = true;
for (let d = 0; d <= MARS_ORBIT.period; d += 3) {
  const r = marsAt(d).r;
  if (r < MARS_ORBIT.a * (1 - MARS_ORBIT.e) - 1e-9) allInside = false;
  if (r > MARS_ORBIT.a * (1 + MARS_ORBIT.e) + 1e-9) allInside = false;
}
ok('mọi điểm quỹ đạo Sao Hỏa nằm trong dải cận viễn điểm', allInside);

/* Đường vẽ phải trùng quỹ đạo thật. Đây là lỗi từng có: phần vẽ dùng
   quỹ đạo gốc với hướng cận điểm bằng 0, trong khi hành tinh đã được
   quay đi. Khi đó hành tinh nằm lệch khỏi vòng được vẽ, mắt nhìn thấy
   ngay là sai, dù mọi con số vẫn đúng. */
ok('có quỹ đạo Trái Đất dùng để vẽ', !!EARTH_PATH && !!MARS_PATH);
near('hướng cận điểm quỹ đạo vẽ Sao Hỏa khớp epoch', MARS_PATH.periDeg, MARS_PERI_DEG, 1e-9, 'độ');
near('hướng cận điểm quỹ đạo vẽ Trái Đất khớp epoch', EARTH_PATH.periDeg, EARTH_PERI_DEG, 1e-9, 'độ');

/* Kiểm tra giải tích, không phụ thuộc số mẫu: với một ellipse có tiêu
   điểm ở gốc, bán kính tại góc cực nu phải bằng a(1-e^2)/(1+e cos nu).
   Nếu vòng vẽ bị quay sai, phương trình này không còn nghiệm. */
function ringEquationResidual(orbit, state) {
  const p = orbit.a * (1 - orbit.e * orbit.e);
  const expected = p / (1 + orbit.e * Math.cos((state.lonDeg - orbit.periDeg) * (Math.PI / 180)));
  return Math.abs(expected - state.r);
}

let worstRing = 0;
for (const day of [0, 50, 129.45, 200, 258.9]) {
  const r = ringEquationResidual(MARS_PATH, marsAt(day));
  if (r > worstRing) worstRing = r;
}
ok('vòng Sao Hỏa vẽ ra đi qua đúng vị trí Sao Hỏa', worstRing < 1e-9, `dư ${worstRing.toExponential(2)} AU`);

let worstEarthRing = 0;
for (const day of [0, 50, 129.45, 200, 258.9]) {
  const r = ringEquationResidual(EARTH_PATH, earthAt(day));
  if (r > worstEarthRing) worstEarthRing = r;
}
ok('vòng Trái Đất vẽ ra đi qua đúng vị trí Trái Đất', worstEarthRing < 1e-9, `dư ${worstEarthRing.toExponential(2)} AU`);

/* Phản chứng: nếu vẽ bằng quỹ đạo gốc chưa quay, sai số phải lớn hơn
   hẳn ngưỡng trên. Test này chứng minh phép kiểm tra ở trên thật sự
   bắt được lỗi, chứ không phải lúc nào cũng xanh. */
const wrongRing = ringEquationResidual({ ...MARS_ORBIT, periDeg: 0 }, marsAt(0));
ok(
  'vẽ bằng quỹ đạo chưa quay thì lệch rõ rệt',
  wrongRing > 0.01,
  `dư ${wrongRing.toFixed(3)} AU, đủ để mắt thấy`
);

/* ---------- 4. đường chuyển tiếp ---------- */

section('4. Đường chuyển tiếp Hohmann');

const departR = earthAt(0).r;
const arriveR = marsAt(TRANSFER_DAYS).r;

near('tàu xuất phát đúng bán kính Trái Đất', transferAt(0).r, departR, 1e-9, 'AU');
near('tàu tới đúng bán kính Sao Hỏa', transferAt(TRANSFER_DAYS).r, arriveR, 1e-9, 'AU');

near(
  'tàu tới đúng kinh độ Sao Hỏa ngày 258,9',
  transferAt(TRANSFER_DAYS).lonDeg,
  marsAt(TRANSFER_DAYS).lonDeg,
  1e-6,
  'độ'
);

/* Bán kính phải tăng đơn điệu: tàu chỉ đi ra, không quay lại. */
let monotonic = true;
let prevR = -Infinity;
for (let d = 0; d <= TRANSFER_DAYS; d += 0.5) {
  const r = transferAt(d).r;
  if (r < prevR - 1e-9) monotonic = false;
  prevR = r;
}
ok('bán kính tàu tăng đơn điệu suốt hành trình', monotonic);

/* Điểm giữa hành trình ứng với dị thường trung bình 90 độ, không phải
   dị thường lệch tâm 90 độ. Bán kính kiểm tra theo nghiệm Kepler độc
   lập, không theo trực giác. */
const eT = TRANSFER_ORBIT.e;
const aT = TRANSFER_ORBIT.a;
const E90 = solveKepler(90, eT);
const rAtM90 = aT * (1 - eT * Math.cos(E90));
near(
  'bán kính tàu ở giữa hành trình khớp công thức ellipse',
  transferAt(TRANSFER_DAYS / 2).r,
  rAtM90,
  1e-6,
  'AU'
);
ok(
  'bán kính giữa hành trình lớn hơn bán trục lớn',
  transferAt(TRANSFER_DAYS / 2).r > TRANSFER_ORBIT.a
);

/* Kẹp biên: ngày ngoài dải không được vượt quá hai đầu. */
near('ngày âm bị kẹp về điểm xuất phát', transferAt(-5).r, departR, 1e-9, 'AU');
near('ngày vượt bị kẹp về điểm tới', transferAt(400).r, arriveR, 1e-9, 'AU');

/* ---------- 5. góc pha lúc phóng ---------- */

section('5. Cửa sổ phóng');

/* Cửa sổ phóng Hohmann của Sao Hỏa vào khoảng 44 độ: 180 trừ quãng
   Sao Hỏa đi trong 258,9 ngày. */
between('cửa sổ phóng trong khoảng 40 tới 50 độ', PHASE_AT_LAUNCH, 40, 50, 'độ');
near('cửa sổ phóng khớp 180 trừ 0,52404 nhân 258,9', PHASE_AT_LAUNCH, 180 - 0.52404 * TRANSFER_DAYS, 0.01, 'độ');

/* Góc pha thật lúc phóng, đo giữa hai hành tinh, khác con số trên vì
   Sao Hỏa có tâm sai. Chỉ cần nằm trong khoảng hợp lý và dương, tức
   Sao Hỏa đi trước Trái Đất. */
const s0 = missionState(0);
between('góc pha thật ngày 0 trong khoảng 15 tới 45 độ', s0.phaseDeg, 15, 45, 'độ');
ok('Sao Hỏa đi trước Trái Đất ở ngày 0', s0.phaseDeg > 0);
between('khoảng cách ngày 0 trong khoảng 0,5 tới 1,5 AU', s0.distanceAu, 0.5, 1.5, 'AU');

/* Hai mốc neo phải trùng khít: tàu rời đúng chỗ Trái Đất và tới
   đúng chỗ Sao Hỏa, không hở khoảng nào trên hình vẽ. */
near('ngày 0 tàu trùng vị trí Trái Đất (bán kính)', transferAt(0).r, earthAt(0).r, 1e-9, 'AU');
near('ngày 0 tàu trùng vị trí Trái Đất (kinh độ)', transferAt(0).lonDeg, earthAt(0).lonDeg, 1e-9, 'độ');
near('ngày cuối tàu trùng vị trí Sao Hỏa (bán kính)', transferAt(TRANSFER_DAYS).r, marsAt(TRANSFER_DAYS).r, 1e-9, 'AU');
near('ngày cuối tàu trùng vị trí Sao Hỏa (kinh độ)', transferAt(TRANSFER_DAYS).lonDeg, marsAt(TRANSFER_DAYS).lonDeg, 1e-9, 'độ');

/* Ở hai đầu hành trình, khoảng cách phải khớp định lý cosin dựng từ
   hai bán kính và góc giữa hai hành tinh. Đây là phép kiểm tra độc
   lập với cách separationAu tính, nên nó bắt được lỗi toạ độ. */
function lawOfCosinesAu(day) {
  const e = earthAt(day);
  const m = marsAt(day);
  let dLon = Math.abs(m.lonDeg - e.lonDeg);
  if (dLon > 180) dLon = 360 - dLon;
  const c = Math.cos((dLon * Math.PI) / 180);
  return Math.sqrt(e.r * e.r + m.r * m.r - 2 * e.r * m.r * c);
}

near('khoảng cách ngày 0 khớp định lý cosin', separationAu(0), lawOfCosinesAu(0), 1e-9, 'AU');
near(
  'khoảng cách ngày cuối khớp định lý cosin',
  separationAu(TRANSFER_DAYS),
  lawOfCosinesAu(TRANSFER_DAYS),
  1e-9,
  'AU'
);
near(
  'khoảng cách giữa hành trình khớp định lý cosin',
  separationAu(TRANSFER_DAYS / 2),
  lawOfCosinesAu(TRANSFER_DAYS / 2),
  1e-9,
  'AU'
);

/* ---------- 6. khoảng cách theo ngày ---------- */

section('6. Khoảng cách Trái Đất Sao Hỏa');

const d0 = separationAu(0);
const dMid = separationAu(TRANSFER_DAYS / 2);
const dEnd = separationAu(TRANSFER_DAYS);

between('ngày 0 khoảng cách hợp lý cho cửa sổ phóng', d0, 0.5, 1.2, 'AU');
between('giữa hành trình khoảng cách dưới 0,8 AU', dMid, 0.4, 0.8, 'AU');
between('ngày cuối khoảng cách 1,5 tới 2,0 AU', dEnd, 1.5, 2.0, 'AU');

ok('khoảng cách giảm rồi tăng: ngày 0 xa hơn giữa hành trình', d0 > dMid);
ok('khoảng cách ngày cuối lớn hơn giữa hành trình', dEnd > dMid);

/* Khoảng cách không bao giờ vượt quá tổng hai viễn điểm, và không
   nhỏ hơn hiệu hai bán kính nhỏ nhất. Đây là chặn hình học tuyệt đối. */
let insideBounds = true;
for (let d = 0; d <= TRANSFER_DAYS; d += 0.5) {
  const au = separationAu(d);
  const maxPossible = MARS_ORBIT.a * (1 + MARS_ORBIT.e) + EARTH_ORBIT.a * (1 + EARTH_ORBIT.e);
  const minPossible = 0;
  if (au > maxPossible + 1e-6 || au < minPossible - 1e-6) insideBounds = false;
}
ok('khoảng cách luôn nằm dưới tổng hai viễn điểm', insideBounds);

/* Điểm gần nhất phải nằm trong hành trình, không phải ở hai đầu. */
const ex = rangeExtremes(0.05);
between('điểm gần nhất rơi vào khoảng ngày 40 tới 100', ex.minDay, 40, 100, 'ngày');
ok('điểm gần nhất gần hơn khoảng cách ngày 0', ex.minAu < d0);
ok('khoảng cách lớn nhất trong cửa sổ rơi vào cuối hành trình', ex.maxDay > 240);
near('khoảng cách lớn nhất khớp ngày cuối', ex.maxAu, dEnd, 0.01, 'AU');

/* Ghi chú về một kỳ vọng dễ nhầm trong đề bài: có ý kiến cho rằng
   khoảng cách lớn nhất rơi vào giữa hành trình. Điều đó không đúng
   với chuyển tiếp Hohmann, và test này ghi lại sự thật hình học.

   Lúc phóng, Sao Hỏa đi trước Trái Đất khoảng 44 độ, nên khoảng cách
   đã khá gần. Trong nửa đầu hành trình, Trái Đất chạy nhanh hơn Sao
   Hỏa trên cung ngắn nên hai bên tiến lại gần nhau, đạt cực tiểu
   quanh ngày 68, gần thời điểm đối xung. Nửa sau thì chúng xa dần,
   và khoảng cách lớn nhất rơi đúng vào ngày tới nơi.

   Vì vậy giữa hành trình là cực tiểu, không phải cực đại. Bản đồ vẽ
   theo hình học thật, không uốn theo kỳ vọng cho đẹp mắt. */
ok(
  'giữa hành trình là cực tiểu, không phải cực đại',
  dMid < d0 && dMid < dEnd,
  `giữa ${fmt(dMid)}, đầu ${fmt(d0)}, cuối ${fmt(dEnd)} AU`
);
ok(
  'khoảng cách lớn nhất không rơi vào giữa hành trình',
  Math.abs(ex.maxDay - TRANSFER_DAYS / 2) > 20,
  `cực đại ở ngày ${ex.maxDay}`
);

/* ---------- 7. quy đổi km và trễ tín hiệu ---------- */

section('7. Trễ tín hiệu một chiều');

near('1 AU ra km', auToKm(1), 149597870.7, 0.1, 'km');
near('1 AU trễ 8,317 phút', delayMinutes(1), 8.3167, 0.002, 'phút');

/* Trễ phải nằm trong dải 3 tới 23 phút cho toàn bộ cửa sổ. */
let minDelay = Infinity;
let maxDelay = -Infinity;
for (let d = 0; d <= TRANSFER_DAYS; d += 0.25) {
  const m = delayMinutes(separationAu(d));
  if (m < minDelay) minDelay = m;
  if (m > maxDelay) maxDelay = m;
}
between('trễ nhỏ nhất trong cửa sổ trên 3 phút', minDelay, DELAY_BAND.nearest, 23, 'phút');
between('trễ lớn nhất trong cửa sổ dưới 23 phút', maxDelay, 0, 23, 'phút');
ok('trễ tăng giảm cùng chiều với khoảng cách', maxDelay > minDelay);

const sArr = missionState(TRANSFER_DAYS);
between('trễ lúc tới nơi trong dải 12 tới 16 phút', sArr.delayMinutes, 12, 16, 'phút');
between('trễ lúc khởi hành trong dải 3 tới 23 phút', s0.delayMinutes, 3, 23, 'phút');

/* Đơn vị km: ngày 0 phải ra cỡ trăm triệu km. */
between('khoảng cách ngày 0 cỡ 100 tới 230 triệu km', s0.distanceKm / 1e6, 100, 230, 'triệu km');
near(
  'km tính từ AU khớp nhau',
  s0.distanceKm,
  s0.distanceAu * AU_KM,
  1e-3,
  'km'
);

/* ---------- 8. trạng thái theo ngày ---------- */

section('8. Gói trạng thái missionState');

const mid = missionState(129.45);
near('tiến trình ở giữa hành trình là 0,5', mid.progress, 0.5, 1e-9);
ok('ngày vượt bị kẹp về 258,9', missionState(999).day === TRANSFER_DAYS);
ok('ngày âm bị kẹp về 0', missionState(-20).day === 0);
ok('cờ tới nơi bật ở ngày cuối', missionState(TRANSFER_DAYS).arrived === true);
ok('cờ tới nơi tắt ở giữa hành trình', mid.arrived === false);

/* Tiến trình phải tăng đều. */
let progressOk = true;
for (let d = 0; d < TRANSFER_DAYS; d += 10) {
  if (missionState(d + 10).progress <= missionState(d).progress) progressOk = false;
}
ok('tiến trình tăng đơn điệu', progressOk);

/* Đồng hồ sứ mệnh. */
const c = missionClock(TRANSFER_DAYS);
ok('đồng hồ ngày cuối ra 258 ngày', c.days === 258, `nhận ${c.days}`);
between('đồng hồ giờ trong 0 tới 23', c.hours, 0, 23);
between('đồng hồ phút trong 0 tới 59', c.minutes, 0, 59);
ok('tổng số phút khớp số ngày', Math.abs(c.totalMinutes - TRANSFER_DAYS * 1440) <= 1);

const c0 = missionClock(0);
ok('đồng hồ ngày 0 là 0 ngày 0 giờ', c0.days === 0 && c0.hours === 0 && c0.minutes === 0);

/* ---------- 9. mốc TCM ---------- */

section('9. Mốc đốt hiệu chỉnh TCM');

ok('có đúng ba mốc TCM', TCM.length === 3);

let tcmSorted = true;
let tcmInRange = true;
let tcmSmall = true;
for (let i = 0; i < TCM.length; i++) {
  const item = TCM[i];
  if (i > 0 && item.day <= TCM[i - 1].day) tcmSorted = false;
  if (item.day <= 0 || item.day >= TRANSFER_DAYS) tcmInRange = false;
  if (item.dvMs <= 0 || item.dvMs > 50) tcmSmall = false;
  ok(`TCM ${item.index} có nhãn cả hai ngôn ngữ`, !!(item.label.vi && item.label.en));
  ok(`TCM ${item.index} có ghi chú cả hai ngôn ngữ`, !!(item.note.vi && item.note.en));
  ok(`TCM ${item.index} nằm trên đường bay`, Number.isFinite(transferAt(item.day).r));
}
ok('ba mốc xếp theo thời gian tăng dần', tcmSorted);
ok('ba mốc nằm trong hành trình', tcmInRange);
ok('delta-v từng mốc nhỏ, đúng cỡ hiệu chỉnh', tcmSmall);

ok('chưa đốt mốc nào ở ngày 0', tcmPassed(0) === 0);
ok('qua mốc 1 sau ngày 14,6', tcmPassed(15) === 1);
ok('qua hai mốc sau ngày 96,3', tcmPassed(100) === 2);
ok('qua cả ba mốc ở ngày cuối', tcmPassed(TRANSFER_DAYS) === 3);
ok('mốc kế tiếp ở ngày 0 là mốc 1', tcmNext(0).index === 1);
ok('sau mốc cuối không còn mốc kế tiếp', tcmNext(TRANSFER_DAYS) === null);

const sTcm = missionState(120);
ok('trạng thái ngày 120 báo đã qua hai mốc', sTcm.tcmPassed === 2);
ok('trạng thái ngày 120 báo mốc kế tiếp là mốc 3', sTcm.nextTcm && sTcm.nextTcm.index === 3);

/* Tỉ lệ vị trí TCM trên thanh tiến trình phải nằm trong 0 tới 100. */
let tcmPctOk = true;
for (const item of TCM) {
  const pct = (item.day / TRANSFER_DAYS) * 100;
  if (!(pct > 0 && pct < 100)) tcmPctOk = false;
}
ok('vị trí TCM trên thanh tiến trình hợp lệ', tcmPctOk);

/* ---------- 10. tính nhất quán giữa các hàm ---------- */

section('10. Nhất quán giữa các hàm');

near(
  'separationAu khớp missionState',
  separationAu(77),
  missionState(77).distanceAu,
  1e-12,
  'AU'
);
near(
  'delayMinutes khớp missionState',
  delayMinutes(separationAu(77)),
  missionState(77).delayMinutes,
  1e-12,
  'phút'
);
near('meanMotion Sao Hỏa 0,524 độ mỗi ngày', meanMotionDeg(MARS_ORBIT.period), 0.52404, 1e-4, 'độ/ngày');
near('meanMotion Trái Đất 0,9856 độ mỗi ngày', meanMotionDeg(EARTH_ORBIT.period), 0.98561, 1e-4, 'độ/ngày');

/* orbitState trả toạ độ Descartes phải khớp bán kính và góc cực. */
let cartsOk = true;
for (let i = 0; i < 36; i++) {
  const st = orbitState(MARS_ORBIT, i * 10);
  const r = Math.hypot(st.x, st.y);
  if (Math.abs(r - st.r) > 1e-9) cartsOk = false;
  const lon = normDeg(Math.atan2(st.y, st.x) * (180 / Math.PI));
  let diff = Math.abs(lon - st.lonDeg);
  if (diff > 180) diff = 360 - diff;
  if (diff > 1e-9) cartsOk = false;
}
ok('toạ độ Descartes khớp bán kính và góc cực', cartsOk);

/* Không có NaN ở bất kỳ mẫu nào. */
let noNaN = true;
for (let d = 0; d <= TRANSFER_DAYS; d += 1) {
  const s = missionState(d);
  const nums = [s.distanceAu, s.distanceKm, s.delayMinutes, s.progress, s.craft.r, s.craft.lonDeg];
  for (const n of nums) if (!Number.isFinite(n)) noNaN = false;
}
ok('không có NaN trong toàn bộ hành trình', noNaN);

/* ---------- 11. định dạng số ---------- */

section('11. Định dạng số theo ngôn ngữ');

ok('tiếng Việt dùng phẩy thập phân', formatNumber(0.689, 3, 'vi') === '0,689', formatNumber(0.689, 3, 'vi'));
ok('tiếng Anh dùng chấm thập phân', formatNumber(0.689, 3, 'en') === '0.689', formatNumber(0.689, 3, 'en'));
ok(
  'tiếng Việt dùng chấm hàng nghìn',
  formatNumber(103050648, 0, 'vi') === '103.050.648',
  formatNumber(103050648, 0, 'vi')
);
ok(
  'tiếng Anh dùng phẩy hàng nghìn',
  formatNumber(103050648, 0, 'en') === '103,050,648',
  formatNumber(103050648, 0, 'en')
);
ok('số nhỏ hơn 1000 không có dấu hàng nghìn', formatNumber(258.9, 1, 'vi') === '258,9');
ok('số âm giữ dấu trừ', formatNumber(-5.5, 1, 'vi') === '-5,5');
ok('số không hợp lệ trả về 0', formatNumber(NaN, 2, 'vi') === '0');
ok(
  'cùng một số ra hai kiểu khác nhau ở hai ngôn ngữ',
  formatNumber(1234.5, 1, 'vi') === '1.234,5' && formatNumber(1234.5, 1, 'en') === '1,234.5'
);

/* ---------- tổng kết ---------- */

console.log('\n' + '='.repeat(56));
console.log(`Kết quả: ${pass} PASS, ${fail} FAIL (tổng ${pass + fail})`);
if (fail) {
  console.log('Bài hỏng:');
  for (const f of failures) console.log('  - ' + f);
  process.exit(1);
}
console.log('Toàn bộ PASS');
process.exit(0);
