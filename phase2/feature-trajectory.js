/* ============================================================
   phase2/feature-trajectory.js
   Cửa sổ chọn quy đạo bay cho Giai đoạn 2.

   Ba lựa chọn quy đạo, mỗi thẻ là một thẻ dọc gồm tên, ba con số
   (thời gian bay, delta-v, so sánh với solsRemaining), dòng mô tả
   đánh đổi, nút Chọn/Gỡ và một biểu đồ SVG riêng vẽ hình dạng
   quỹ đạo nhìn từ trên xuống (Mặt Trời ở giữa bên trái).

   API theo phase2/CONTRACT.md:
     openTrajectoryModal({ engine, onClose }) -> { root, close }

   CÁCH SUY RA CON SỐ DELTA-V (đề bài yêu cầu ghi rõ):
     Mốc đối chiếu là bốn chặng trong src/data/nasa/rescue_mission.json,
     lấy bằng deltaVLegs() và REQUIRED_DELTA_V_MS:
       leo_departure          3.570 m/s   (doc)
       heliocentric_transfer  5.594 m/s   (calculated, chỉ là số đo
                                           năng lượng của riêng phần
                                           chuyển tiếp, KHÔNG cộng dồn)
       mars_capture           2.080 m/s   (doc)
       mars_descent           1.000 m/s   (estimate)
     Ngân sách cộng dồn đúng để kiểm tra nhiên liệu là
     REQUIRED_DELTA_V_MS = 3570 + 2080 + 1000 = 6.650 m/s.
     Thời gian bay Hohmann 258,9 ngày cũng lấy từ cùng file JSON
     (transfer.flight_time_days).

     - hohmann: đúng hồ sơ của JSON, 258,9 ngày, phần chuyển tiếp
       nhật tâm 5.594 m/s (heliocentric_reference_ms). Đây là lựa
       chọn rẻ nhất và chậm nhất của cửa sổ phóng hẹp.
     - fast_transit: 180 ngày, khoảng 9.200 m/s. Suy luận: bay nhanh
       hơn Hohmann nghĩa là elip dài hơn, vận tốc vô cực khi rời
       Trái Đất tăng từ 2,945 km/s lên khoảng 4,3 km/s (công thức
       năng lượng trên bán trục lớn ngắn hơn), tức phần khởi hành
       tăng khoảng 1,3 km/s so với 3,570 m/s; phần hãm ở Sao Hỏa
       cũng tăng tương ứng vì tới với vận tốc dư cao hơn. Cộng dồn
       hai phần đó cho khoảng 9.200 m/s, tức tốn thêm khoảng
       3.600 m/s so với 5.594 m/s của phần chuyển tiếp, đổi lại
       nhanh hơn 79 ngày. Đây là ước tính của nhóm làm game, không
       phải số liệu NASA.
     - bi_elliptic: 320 ngày, khoảng 4.800 m/s. Suy luận: quy đạo
       hai xung vung tàu ra ngoài quỹ đạo Sao Hỏa rồi quay vào,
       xung thứ nhất nhẹ hơn nhiều so với đốt thẳng tới Sao Hỏa,
       nên tổng cộng dồn thấp hơn Hohmann khoảng 800 m/s. Cái giá
       là thời gian bay dài hơn Hohmann tới 61 ngày, đồng đội trên
       Sao Hỏa có thể không chờ được. Cũng là ước tính của nhóm.

   Quy tắc dự án:
     - CSS nạp bằng new URL('.', import.meta.url).href
     - không dấu gạch dài trong chuỗi hiển thị
     - song ngữ Việt và Anh, chuỗi giữ trong chính file này
     - màu lấy từ ../src/css/tokens.css, không hardcode
     - SVG thuần viewBox, không Canvas
     - tôn trọng prefers-reduced-motion và html.motion-off
   ============================================================ */

import { REQUIRED_DELTA_V_MS, deltaVLegs } from '../src/nasa-data.js';

const BASE = new URL('.', import.meta.url).href;
const CSS_URL = new URL('css-trajectory.css', import.meta.url).href;

/* ---------- chuỗi song ngữ ---------- */

const T = {
  vi: {
    eyebrow: 'LẬP KẾ HOẠCH BAY',
    title: 'Chọn quy đạo bay tới Sao Hỏa',
    titleEn: 'Pick the flight path to Mars',
    sub: 'Mỗi quy đạo là một cách tiêu nhiên liệu đổi lấy thời gian. Chọn chậm thì rẻ nhưng đồng đội phải chờ lâu hơn.',
    close: 'Đóng cửa sổ',
    pick: 'Chọn',
    picked: 'Gỡ',
    pickedMark: 'Đang chọn',
    statDays: 'Thời gian bay',
    statDv: 'Delta-v cộng dồn',
    statSols: 'So với thời gian đồng đội còn lại',
    solsLeft: '{n} sol còn lại',
    enough: 'Kip thời gian, còn dư {n} sol',
    late: 'Bay lâu hơn thời gian đồng đội còn lại {n} sol',
    warnLate: 'Đồng đội không chờ được lâu vậy',
    okInTime: 'Tới kịp, còn dư {n} sol',
    noteCompare: 'Con số so sánh lấy từ đồng hồ thời gian của engine: state.solsRemaining.',
    footNote: 'Con số delta-v lấy từ bốn chặng trong src/data/nasa/rescue_mission.json, xem phần giải thích ở đầu feature-trajectory.js.',
    chartCaption: '{d} ngày bay · {v} m/s',
    chartEarth: 'TD',
    chartMars: 'SH',
    chartSun: 'MT',
    chartTitle: 'Hình dạng quy đạo nhìn từ trên xuống',
  },
  en: {
    eyebrow: 'FLIGHT PLANNING',
    title: 'Pick the flight path to Mars',
    titleEn: 'Pick the flight path to Mars',
    sub: 'Each path trades propellant for time. The slow one is cheap, but the crew has to hold out much longer.',
    close: 'Close the window',
    pick: 'Select',
    picked: 'Remove',
    pickedMark: 'Selected',
    statDays: 'Flight time',
    statDv: 'Additive delta-v',
    statSols: 'Against the crew time left',
    solsLeft: '{n} sols left',
    enough: 'In time, {n} sols to spare',
    late: 'Flies {n} sols longer than the crew has left',
    warnLate: 'The crew cannot wait that long',
    okInTime: 'Arrives in time, {n} sols to spare',
    noteCompare: 'The comparison reads the engine time gauge: state.solsRemaining.',
    footNote: 'Delta-v figures come from the four legs in src/data/nasa/rescue_mission.json, see the derivation note at the top of feature-trajectory.js.',
    chartCaption: '{d} days of flight · {v} m/s',
    chartEarth: 'TD',
    chartMars: 'SH',
    chartSun: 'MT',
    chartTitle: 'Path shape seen from above',
  },
};

/* ---------- ba lựa chọn quy đạo ----------
   Con số và cách suy ra đã ghi ở đầu file. days là ngày Trái Đất,
   dvMs là ngân sách cộng dồn đúng để kiểm tra nhiên liệu. */

const TRAJECTORIES = [
  {
    id: 'hohmann',
    name_vi: 'Quy đạo Hohmann tiết kiệm',
    name_en: 'Lean Hohmann transfer',
    tradeoff_vi:
      'Re nhất và chậm nhất của cửa sổ phóng hẹp. Một lần đốt mỗi chặng, tốn ít nhiên liệu nhất, nhưng 258,9 ngày trên đường là rất lâu khi có người đang chờ cứu.',
    tradeoff_en:
      'The cheapest and slowest option of the narrow launch window. One burn per leg, the least propellant of any path, but 258.9 days in flight is a long time when people are waiting for rescue.',
    days: 258.9,
    dvMs: 5594,
    dvNote_vi: 'Đúng phần chuyển tiếp nhật tâm 5.594 m/s của hồ sơ Hohmann trong rescue_mission.json.',
    dvNote_en: 'Exactly the 5594 m/s heliocentric transfer of the Hohmann profile in rescue_mission.json.',
    /* Hình dạng: nửa vòng elip rộng, rời Trái Đất cong nhẹ ra ngoài
       rồi vào thẳng Sao Hỏa. */
    chart: 'hohmann',
  },
  {
    id: 'fast_transit',
    name_vi: 'Đường bay tốc độ cao',
    name_en: 'High speed transit',
    tradeoff_vi:
      'Nhanh hơn 79 ngày nhưng tốn thêm khoảng 3.600 m/s. Elip dài hơn phải đốt mạnh hơn lúc rời Trái Đất và hãm gắt hơn lúc tới nơi, tức bình nhiên liệu to hơn.',
    tradeoff_en:
      '79 days faster but about 3600 m/s more expensive. The longer ellipse burns harder leaving Earth and brakes harder on arrival, which means a bigger tank.',
    days: 180,
    dvMs: 9200,
    dvNote_vi: 'Ước tính của nhóm làm game: khởi hành tăng khoảng 1,3 km/s cộng hãm tăng tương ứng, so với 5.594 m/s của Hohmann.',
    dvNote_en: 'A game side estimate: departure up about 1.3 km/s plus a matching harder capture, against the 5594 m/s Hohmann figure.',
    /* Hình dạng: cung ngắn hơn nhưng vọt xa ra ngoài quỹ đạo. */
    chart: 'fast',
  },
  {
    id: 'bi_elliptic',
    name_vi: 'Quy đạo hai xung',
    name_en: 'Bi elliptic transfer',
    tradeoff_vi:
      'Rẻ nhất về nhiên liệu nhưng chậm: vung tàu ra ngoài quỹ đạo Sao Hỏa rồi mới quay vào, tiết kiệm khoảng 800 m/s, đổi lại 320 ngày và đồng đội có thể không chờ được.',
    tradeoff_en:
      'The cheapest in propellant but slow: swing out beyond Mars orbit and curve back in, saving about 800 m/s at the cost of 320 days, and the crew may not last that long.',
    days: 320,
    dvMs: 4800,
    dvNote_vi: 'Ước tính của nhóm làm game: xung thứ nhất nhẹ hơn đốt thẳng tới Sao Hỏa, tổng thấp hơn Hohmann khoảng 800 m/s.',
    dvNote_en: 'A game side estimate: the first burn is gentler than flying straight to Mars, so the total sits about 800 m/s under Hohmann.',
    /* Hình dạng: vòng lớn vung ra ngoài quỹ đạo Sao Hỏa rồi mới
       quay vào đón Sao Hỏa. */
    chart: 'bi',
  },
];

/* ---------- tiện ích ---------- */

function esc(v) {
  return String(v == null ? '' : v)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fill(str, vars) {
  let s = str;
  for (const k of Object.keys(vars)) s = s.split('{' + k + '}').join(String(vars[k]));
  return s;
}

function fmt(n, digits = 0) {
  if (!Number.isFinite(Number(n))) return '0';
  const fixed = Number(n).toFixed(digits);
  const parts = fixed.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return parts.join(',');
}

function fmtEn(n, digits = 0) {
  if (!Number.isFinite(Number(n))) return '0';
  return Number(n).toFixed(digits);
}

let cssInjected = false;

function injectCss() {
  if (cssInjected) return;
  cssInjected = true;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = CSS_URL;
  link.dataset.featureCss = 'trajectory';
  document.head.appendChild(link);
}

function readMotion() {
  let gameOn = true;
  try {
    if (document.documentElement.classList.contains('motion-off')) gameOn = false;
  } catch {
    /* không có document thì bỏ qua */
  }
  let osOk = true;
  try {
    osOk = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch {
    osOk = true;
  }
  return gameOn && osOk;
}

function currentLang() {
  try {
    const lang = (document.documentElement.getAttribute('lang') || 'vi').toLowerCase();
    return lang.indexOf('vi') === 0 ? 'vi' : 'en';
  } catch {
    return 'vi';
  }
}

function readState(engine) {
  if (!engine || typeof engine.getState !== 'function') return null;
  try {
    return engine.getState() || null;
  } catch {
    return null;
  }
}

/* Mốc đối chiếu: tổng cộng dồn của các chặng thật. Dùng làm ghi chú
   kiểm chứng ở chân modal, không dùng để chặn lựa chọn. */
function legsSummary() {
  try {
    const legs = deltaVLegs();
    return legs.map((l) => l.id + ' ' + fmt(l.delta_v_ms, 0)).join(' + ');
  } catch {
    return '';
  }
}

/* ============================================================
   BA BIỂU ĐỒ SVG
   Cùng một viewBox 0 0 660 150, cùng bố cục: Mặt Trời ở giữa bên
   trái, Trái Đất và Sao Hỏa ở hai bán kính quỹ đạo khác nhau.
   Khác nhau nằm ở đường bay:
     hohmann      nửa vòng elip rộng, cong nhẹ ra ngoài rồi vào
     fast_transit cung ngắn hơn nhưng vọt xa khỏi quỹ đạo
     bi_elliptic  vòng lớn vung ra ngoài quỹ đạo Sao Hỏa rồi mới
                  quay vào
   ============================================================ */

const CH_W = 660;
const CH_H = 150;

/* Khung nhìn là một cửa sổ nhìn từ trên xuống, góc nhìn xiên nên
   quỹ đạo tròn hiện ra thành elip dẹt. Hai elip dùng CÙNG một tỉ lệ
   dẹt 0,125 để phép chiếu nhất quán:
     Trái Đất  rx 320, ry 40
     Sao Hỏa   rx 545, ry 68
   Mặt Trời đặt gần mép trái, cả hai quỹ đạo quét hết bề ngang. */
const SUN_X = 70;
const SUN_Y = 75;
const E_RX = 320;
const E_RY = 40;
const M_RX = 545;
const M_RY = 68;

function ellipsePoint(cx, cy, rx, ry, deg) {
  const a = (deg * Math.PI) / 180;
  return { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a) };
}

/* Trái Đất lúc phóng, góc 8 độ: gần đỉnh elip, bên phải Mặt Trời. */
const EARTH_DEG = 8;
/* Sao Hỏa lúc tàu tới, góc -28 độ: cao hơn, xa hơn. */
const MARS_DEG = -28;

const E = ellipsePoint(SUN_X, SUN_Y, E_RX, E_RY, EARTH_DEG);
const M = ellipsePoint(SUN_X, SUN_Y, M_RX, M_RY, MARS_DEG);

const n = (v) => v.toFixed(1);

function orbitSvg() {
  return `
    <ellipse class="tj-orbit tj-orbit-earth" cx="${SUN_X}" cy="${SUN_Y}"
             rx="${E_RX}" ry="${E_RY}"></ellipse>
    <ellipse class="tj-orbit tj-orbit-mars" cx="${SUN_X}" cy="${SUN_Y}"
             rx="${M_RX}" ry="${M_RY}"></ellipse>`;
}

function sunSvg() {
  return `
    <circle class="tj-sun-glow" cx="${SUN_X}" cy="${SUN_Y}" r="30"></circle>
    <circle class="tj-sun-glow2" cx="${SUN_X}" cy="${SUN_Y}" r="19"></circle>
    <circle class="tj-sun" cx="${SUN_X}" cy="${SUN_Y}" r="11"></circle>`;
}

/* Ba đường bay. Ba chuỗi d khác nhau hoàn toàn:
     hohmann  cung rộng nửa vòng, đỉnh nằm gọn giữa hai quỹ đạo
     fast     cung hẹp hơn nhưng vọt lên rất cao, vượt hẳn quỹ đạo
              Sao Hỏa rồi mới cắm xuống đón
     bi       vòng lớn: rời Trái Đất, vung ngược lên trên và sang
              trái, vượt quỹ đạo Sao Hỏa, rồi mới cong về phía Sao
              Hỏa theo một nhánh thứ hai
   Toạ độ đã canh theo khung 660 x 150. */

function pathHohmann() {
  /* Nửa vòng rộng: từ Trái Đất cong lên đỉnh thấp rồi xuống Sao Hỏa. */
  return (
    `M ${n(E.x)} ${n(E.y)} ` +
    `C ${n(E.x + 10)} ${n(E.y - 46)} ${n(M.x - 96)} ${n(M.y - 34)} ${n(M.x - 26)} ${n(M.y - 4)} ` +
    `S ${n(M.x)} ${n(M.y)} ${n(M.x)} ${n(M.y)}`
  );
}

function pathFast() {
  /* Cung ngắn, đỉnh vọt cao hẳn ra ngoài quỹ đạo Sao Hỏa. */
  return (
    `M ${n(E.x)} ${n(E.y)} ` +
    `C ${n(E.x + 4)} ${n(E.y - 78)} ${n(E.x + 46)} ${n(2)} ${n(E.x + 90)} ${n(4)} ` +
    `C ${n(M.x - 60)} ${n(6)} ${n(M.x - 26)} ${n(M.y + 6)} ${n(M.x)} ${n(M.y)}`
  );
}

function pathBi() {
  /* Vòng lớn: ra xa quỹ đạo Sao Hỏa rồi mới quay vào, có hai
     nhánh rõ ràng nên hình khác hẳn hai cái trên. */
  return (
    `M ${n(E.x)} ${n(E.y)} ` +
    `C ${n(E.x - 16)} ${n(E.y - 58)} ${n(E.x - 62)} ${n(14)} ${n(E.x - 118)} ${n(20)} ` +
    `C ${n(E.x - 186)} ${n(27)} ${n(E.x - 232)} ${n(74)} ${n(E.x - 186)} ${n(104)} ` +
    `C ${n(E.x - 128)} ${n(136)} ${n(M.x - 150)} ${n(120)} ${n(M.x - 62)} ${n(92)} ` +
    `S ${n(M.x)} ${n(M.y)} ${n(M.x)} ${n(M.y)}`
  );
}

const PATHS = { hohmann: pathHohmann, fast: pathFast, bi: pathBi };

function chartSvg(traj, t) {
  const d = (PATHS[traj.chart] || pathHohmann)();
  return `
    <svg class="tj-chart" viewBox="0 0 ${CH_W} ${CH_H}" role="img"
         aria-label="${esc(traj.name_vi)} · ${esc(t('chartTitle'))}"
         preserveAspectRatio="xMidYMid meet">
      ${orbitSvg()}
      ${sunSvg()}
      <path class="tj-orbit-tag tj-orbit-tag-earth"
            d="M ${n(SUN_X + E_RX - 34)} ${n(SUN_Y + 4)} h 40"></path>
      <path class="tj-orbit-tag tj-orbit-tag-mars"
            d="M ${n(SUN_X + M_RX - 30)} ${n(SUN_Y + 8)} h 40"></path>
      <path class="tj-flight" d="${d}"></path>
      <path class="tj-flight-arrow" d="${d}"></path>
      <circle class="tj-dot tj-dot-earth" cx="${n(E.x)}" cy="${n(E.y)}" r="5.5"></circle>
      <circle class="tj-dot-halo tj-dot-halo-earth" cx="${n(E.x)}" cy="${n(E.y)}" r="10"></circle>
      <text class="tj-tag tj-tag-earth" x="${n(E.x)}" y="${n(E.y + 20)}" text-anchor="middle">${esc(t('chartEarth'))}</text>
      <circle class="tj-dot tj-dot-mars" cx="${n(M.x)}" cy="${n(M.y)}" r="7"></circle>
      <circle class="tj-dot-halo tj-dot-halo-mars" cx="${n(M.x)}" cy="${n(M.y)}" r="12"></circle>
      <text class="tj-tag tj-tag-mars" x="${n(M.x)}" y="${n(M.y + 24)}" text-anchor="middle">${esc(t('chartMars'))}</text>
      <text class="tj-tag tj-tag-sun" x="${SUN_X}" y="${n(SUN_Y + 26)}" text-anchor="middle">${esc(t('chartSun'))}</text>
    </svg>`;
}

/* ============================================================
   MODULE CHÍNH / MAIN
   ============================================================ */

let uid = 0;

export function openTrajectoryModal({ engine, onClose } = {}) {
  injectCss();

  uid += 1;
  const titleId = 'tj-title-' + uid;

  let lang = currentLang();
  const t = (key) => {
    const table = T[lang] || T.vi;
    return table[key] != null ? table[key] : key;
  };
  const fmtNum = (n, digits) => (lang === 'en' ? fmtEn(n, digits) : fmt(n, digits));

  /* Chọn hiện có, đọc từ engine. Engine có thể chưa hỗ trợ nhóm
     trajectory, nên đọc an toàn và mặc định là chưa chọn. */
  const state0 = readState(engine);
  let pickedId =
    (state0 && state0.selection && state0.selection.trajectory) || null;
  if (pickedId && !TRAJECTORIES.some((tr) => tr.id === pickedId)) pickedId = null;

  const root = document.createElement('div');
  root.className = 'tj-root';
  root.innerHTML = `
    <div class="tj-scrim" data-close="scrim"></div>
    <div class="tj-modal" role="dialog" aria-modal="true" aria-labelledby="${titleId}">
      <header class="tj-head">
        <div class="tj-head-text">
          <p class="tj-eyebrow mono">${esc(t('eyebrow'))}</p>
          <h2 class="tj-title" id="${titleId}">${esc(t('title'))}</h2>
          <p class="tj-sub">${esc(t('sub'))}</p>
        </div>
        <button type="button" class="tj-x" data-close="x" aria-label="${esc(t('close'))}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"
               stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </header>
      <div class="tj-scroll">
        <div class="tj-cards"></div>
        <p class="tj-note">${esc(t('noteCompare'))}</p>
        <p class="tj-footnote">${esc(t('footNote'))}${legsSummary() ? ' · ' + esc(legsSummary()) : ''}</p>
      </div>
    </div>
  `;
  document.body.appendChild(root);

  const cardsEl = root.querySelector('.tj-cards');
  const solsRemaining = Number(state0 && state0.solsRemaining);
  const hasSols = Number.isFinite(solsRemaining) && solsRemaining > 0;

  /* ---------- dựng ba thẻ ---------- */

  const cardViews = TRAJECTORIES.map((traj) => {
    const card = document.createElement('article');
    card.className = 'tj-card';
    card.dataset.id = traj.id;

    /* Cảnh báo sinh tồn: so thời gian bay với solsRemaining. */
    let survivalClass = '';
    let survivalText = '';
    if (hasSols) {
      if (traj.days > solsRemaining) {
        survivalClass = 'is-late';
        survivalText = t('late').replace('{n}', fmtNum(traj.days - solsRemaining, 0));
      } else {
        survivalClass = 'is-in-time';
        survivalText = t('enough').replace('{n}', fmtNum(solsRemaining - traj.days, 0));
      }
    }

    const dv = fmtNum(traj.dvMs, 0);
    card.innerHTML = `
      <div class="tj-card-head">
        <h3 class="tj-name"><span class="tj-name-vi">${esc(traj.name_vi)}</span>
            <em class="tj-name-en">${esc(traj.name_en)}</em></h3>
        <button type="button" class="tj-pick" data-act="pick" data-id="${esc(traj.id)}">
          <span class="tj-pick-txt"></span>
        </button>
      </div>
      <dl class="tj-stats">
        <div class="tj-stat"><dt>${esc(t('statDays'))}</dt><dd class="mono">${fmtNum(traj.days, 1)}</dd></div>
        <div class="tj-stat"><dt>${esc(t('statDv'))}</dt><dd class="mono">${dv} m/s</dd></div>
        <div class="tj-stat tj-stat-sols"><dt>${esc(t('statSols'))}</dt>
          <dd class="mono ${survivalClass}">${hasSols ? fill(t('solsLeft'), { n: fmtNum(solsRemaining, 0) }) : '...'}</dd></div>
      </dl>
      <p class="tj-survival ${survivalClass}" role="status">${esc(survivalText)}</p>
      <p class="tj-trade"><span class="tj-lang mono">VI</span><span class="tj-txt">${esc(traj.tradeoff_vi)}</span></p>
      <p class="tj-trade tj-trade-en"><span class="tj-lang mono">EN</span><span class="tj-txt">${esc(traj.tradeoff_en)}</span></p>
      <p class="tj-dvnote">${esc(lang === 'en' ? traj.dvNote_en : traj.dvNote_vi)}</p>
      <div class="tj-chart-wrap">${chartSvg(traj, t)}</div>
      <p class="tj-caption mono">${fill(t('chartCaption'), { d: fmtNum(traj.days, 1), v: dv })}</p>
    `;
    cardsEl.appendChild(card);

    return { traj, card, pickBtn: card.querySelector('.tj-pick') };
  });

  /* ---------- vẽ trạng thái chọn ---------- */

  function paint() {
    for (const v of cardViews) {
      const on = pickedId === v.traj.id;
      v.card.classList.toggle('is-picked', on);
      v.pickBtn.classList.toggle('is-on', on);
      v.pickBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
      v.pickBtn.querySelector('.tj-pick-txt').textContent = on ? t('picked') : t('pick');
    }
  }

  /* ---------- chọn: gọi engine trong try/catch ----------
     Engine có thể chưa hỗ trợ nhóm trajectory, vẫn gọi và ghi rõ
     ở comment: hợp đồng yêu cầu gọi đúng dạng này, engine từ chối
     thì chỉ là cảnh báo, không làm vỡ modal. */

  function choose(traj) {
    const turningOff = pickedId === traj.id;
    pickedId = turningOff ? null : traj.id;
    try {
      if (engine && typeof engine.updateSelection === 'function') {
        engine.updateSelection({ group: 'trajectory', part: turningOff ? null : traj.id });
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('[tj] updateSelection lỗi', err);
    }
    paint();
  }

  cardsEl.addEventListener('click', (ev) => {
    const btn = ev.target.closest('[data-act="pick"]');
    if (!btn) return;
    const traj = TRAJECTORIES.find((x) => x.id === btn.dataset.id);
    if (traj) choose(traj);
  });

  /* ---------- đóng ---------- */

  let destroyed = false;
  let lastFocus = document.activeElement;

  function close() {
    if (destroyed) return;
    destroyed = true;
    document.removeEventListener('keydown', onKey, true);
    root.classList.add('is-closing');
    if (typeof onClose === 'function') {
      try {
        onClose();
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('[tj] onClose lỗi', err);
      }
    }
    root.remove();
    if (lastFocus && typeof lastFocus.focus === 'function') {
      try {
        lastFocus.focus({ preventScroll: true });
      } catch {
        /* phần tử cũ đã bị gỡ thì thôi */
      }
    }
  }

  function focusables() {
    const sel = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';
    return Array.from(root.querySelectorAll(sel)).filter((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
  }

  function onKey(ev) {
    if (destroyed) return;
    if (ev.key === 'Escape') {
      ev.preventDefault();
      ev.stopPropagation();
      close();
      return;
    }
    if (ev.key !== 'Tab') return;
    const list = focusables();
    if (!list.length) return;
    const first = list[0];
    const last = list[list.length - 1];
    const active = document.activeElement;
    if (list.indexOf(active) < 0) {
      ev.preventDefault();
      first.focus();
      return;
    }
    if (!ev.shiftKey && active === last) {
      ev.preventDefault();
      first.focus();
    } else if (ev.shiftKey && active === first) {
      ev.preventDefault();
      last.focus();
    }
  }

  root.addEventListener('click', (ev) => {
    if (ev.target.closest('[data-close]')) close();
  });

  document.addEventListener('keydown', onKey, true);

  const xBtn = root.querySelector('.tj-x');
  if (xBtn) xBtn.focus({ preventScroll: true });

  paint();

  return { root, close };
}

export default openTrajectoryModal;
