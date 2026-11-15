/* ============================================================
   scripts/test_negotiation.mjs
   Kiểm tra dữ liệu đàm phán và lõi negotiation.js.

   Chạy:  node scripts/test_negotiation.mjs

   Bốn nhóm kiểm tra:
     1. cấu trúc: đủ 16 sự kiện, đủ trường, 2 tới 3 phương án
     2. song ngữ: mọi trường vi và en đều có chữ
     3. dấu gạch dài: không có em dash hay en dash trong bất kỳ chuỗi nào
     4. mô phỏng: chọn toàn phương án phá hoại thì phải tan rã,
        chọn toàn phương án cân bằng thì phải giữ trên 50
   ============================================================ */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import {
  ROLES,
  createNegotiation,
  pickNextEvent,
  applyChoice,
  getCohesionStatus,
  getVetoReaction,
  getSummary,
} from '../src/negotiation.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(HERE, '..', 'src', 'data', 'events', 'role_negotiations.json');

const PHASE_ORDER = ['cruise', 'approach', 'descent', 'surface'];
const REQUIRED_EVENT_FIELDS = [
  'id', 'phase', 'title_vi', 'title_en',
  'situation_vi', 'situation_en', 'stakes_vi', 'stakes_en', 'options',
];
const REQUIRED_OPTION_FIELDS = [
  'id', 'label_vi', 'label_en', 'favors', 'effects',
  'risk_vi', 'risk_en', 'rationale_vi', 'rationale_en',
];

/* U+2014 em dash và U+2013 en dash. Người dùng cấm cả hai trong
   nội dung hiển thị, nên test chặn cả hai chứ không chỉ em dash. */
const BAD_DASHES = [
  { char: '\u2014', name: 'em dash (U+2014)' },
  { char: '\u2013', name: 'en dash (U+2013)' },
];

let pass = 0;
let fail = 0;
const failures = [];

function ok(name) {
  pass++;
  console.log(`  PASS  ${name}`);
}

function bad(name, detail) {
  fail++;
  failures.push({ name, detail });
  console.log(`  FAIL  ${name}`);
  if (detail) console.log(`        ${detail}`);
}

function check(cond, name, detail) {
  if (cond) ok(name);
  else bad(name, detail);
}

function walkStrings(node, path, out) {
  if (typeof node === 'string') {
    out.push({ path, value: node });
    return;
  }
  if (Array.isArray(node)) {
    node.forEach((v, i) => walkStrings(v, `${path}[${i}]`, out));
    return;
  }
  if (node && typeof node === 'object') {
    for (const [k, v] of Object.entries(node)) {
      walkStrings(k, `${path}.<key>`, out);
      walkStrings(v, `${path}.${k}`, out);
    }
  }
}

const raw = readFileSync(DATA_PATH, 'utf8');
const data = JSON.parse(raw);
const events = data.events;

/* ---------- 1. cấu trúc ---------- */

console.log('\n[1] Cau truc du lieu');

check(Array.isArray(events), 'events la mang');
check(events.length >= 15, `co it nhat 15 su kien (thuc te: ${events.length})`);
check(events.length === 16, `du 16 su kien (thuc te: ${events.length})`);

const ids = new Set();
for (const ev of events) {
  for (const field of REQUIRED_EVENT_FIELDS) {
    check(ev[field] !== undefined && ev[field] !== null, `${ev.id}: co truong ${field}`);
  }
  check(!ids.has(ev.id), `${ev.id}: id khong trung`);
  ids.add(ev.id);
  check(PHASE_ORDER.includes(ev.phase), `${ev.id}: phase hop le (${ev.phase})`);

  const opts = ev.options || [];
  check(opts.length >= 2 && opts.length <= 3, `${ev.id}: co 2 toi 3 phuong an (${opts.length})`);

  const optIds = new Set();
  const favored = new Set();
  for (const opt of opts) {
    for (const field of REQUIRED_OPTION_FIELDS) {
      check(opt[field] !== undefined && opt[field] !== null, `${ev.id}/${opt.id}: co truong ${field}`);
    }
    check(!optIds.has(opt.id), `${ev.id}/${opt.id}: id phuong an khong trung`);
    optIds.add(opt.id);
    check(ROLES.includes(opt.favors), `${ev.id}/${opt.id}: favors thuoc ba vai tro`);
    favored.add(opt.favors);

    const eff = opt.effects || {};
    const keys = Object.keys(eff);
    check(keys.length > 0, `${ev.id}/${opt.id}: effects co so lieu`);
    const allNumeric = keys.every((k) => typeof eff[k] === 'number' && Number.isFinite(eff[k]));
    check(allNumeric, `${ev.id}/${opt.id}: moi effect la so huu han`);
    const magnitude = keys.reduce((s, k) => s + Math.abs(eff[k]), 0);
    check(magnitude > 0, `${ev.id}/${opt.id}: effects khac khong`);
  }

  /* Moi su kien phai co it nhat hai vai tro khac nhau duoc uu ai,
     neu khong thi khong con gi de dam phan. */
  check(favored.size >= 2, `${ev.id}: it nhat hai vai tro duoc uu ai (${[...favored].join(', ')})`);
}

/* Phase nao cung phai co su kien. */
for (const phase of PHASE_ORDER) {
  const n = events.filter((e) => e.phase === phase).length;
  check(n >= 3, `phase ${phase}: co it nhat 3 su kien (${n})`);
}

/* ---------- 2. song ngu ---------- */

console.log('\n[2] Song ngu Viet va Anh');

const EVENT_VI = ['title_vi', 'situation_vi', 'stakes_vi'];
const EVENT_EN = ['title_en', 'situation_en', 'stakes_en'];
const OPTION_VI = ['label_vi', 'risk_vi', 'rationale_vi'];
const OPTION_EN = ['label_en', 'risk_en', 'rationale_en'];

let emptyVi = 0;
let emptyEn = 0;
const emptyPaths = [];

function requireText(obj, field) {
  const v = obj[field];
  if (typeof v !== 'string' || !v.trim()) {
    emptyPaths.push(field);
    return false;
  }
  return true;
}

for (const ev of events) {
  for (const f of EVENT_VI) if (!requireText(ev, f)) emptyVi++;
  for (const f of EVENT_EN) if (!requireText(ev, f)) emptyEn++;
  for (const opt of ev.options) {
    for (const f of OPTION_VI) if (!requireText(opt, f)) emptyVi++;
    for (const f of OPTION_EN) if (!requireText(opt, f)) emptyEn++;
  }
}
check(emptyVi === 0, `khong co truong tieng Viet rong (rong: ${emptyVi})`, emptyPaths.slice(0, 6).join(', '));
check(emptyEn === 0, `khong co truong tieng Anh rong (rong: ${emptyEn})`, emptyPaths.slice(0, 6).join(', '));

/* Cau tieng Viet phai dai hon mot tu, va tieng Anh cung vay. */
const tooShort = [];
for (const ev of events) {
  if (ev.situation_vi.trim().length < 40) tooShort.push(`${ev.id}.situation_vi`);
  if (ev.situation_en.trim().length < 40) tooShort.push(`${ev.id}.situation_en`);
  for (const opt of ev.options) {
    if (opt.rationale_vi.trim().length < 20) tooShort.push(`${ev.id}/${opt.id}.rationale_vi`);
    if (opt.rationale_en.trim().length < 20) tooShort.push(`${ev.id}/${opt.id}.rationale_en`);
  }
}
check(tooShort.length === 0, 'mo ta du dai de doc', tooShort.slice(0, 5).join(', '));

/* ---------- 3. dau gach dai ---------- */

console.log('\n[3] Khong co dau gach dai');

const strings = [];
walkStrings(data, 'root', strings);

for (const { char, name } of BAD_DASHES) {
  const hits = strings.filter((s) => s.value.includes(char));
  check(
    hits.length === 0,
    `khong co ${name} trong du lieu`,
    hits.map((h) => h.path).slice(0, 5).join(', ')
  );
}

/* Kiem tra tho tren file goc, khong chi tren chuoi da parse, de bat
   ca truong hop dau gach nam trong ten khoa. */
for (const { char, name } of BAD_DASHES) {
  const count = raw.split(char).length - 1;
  check(count === 0, `file JSON khong chua ${name} (dem: ${count})`);
}

/* ---------- 4. mo phong ---------- */

console.log('\n[4] Mo phong');

function simulate({ pickOption, label }) {
  const state = createNegotiation({ events, startCohesion: 70, seed: 20261115 });
  let played = 0;

  outer: for (const phase of PHASE_ORDER) {
    let ev = pickNextEvent(state, phase);
    while (ev) {
      const opt = pickOption(ev);
      applyChoice(state, opt.id);
      played++;
      if (state.mutiny) break outer;
      ev = pickNextEvent(state, phase);
    }
  }
  return { state, played, label };
}

/* Chon phuong an lam hai cohesion nhat trong moi su kien. */
const destructive = simulate({
  label: 'pha hoai',
  pickOption: (ev) =>
    ev.options.reduce((worst, o) =>
      (o.effects.cohesion_pct ?? 0) < (worst.effects.cohesion_pct ?? 0) ? o : worst
    ),
});

check(destructive.state.cohesion === 0, `pha hoai: cohesion ve 0 (${destructive.state.cohesion})`);
check(destructive.state.mutiny === true, 'pha hoai: tra ve mutiny');
check(destructive.state.done === true, 'pha hoai: trang thai ket thuc');
check(destructive.played > 0 && destructive.played <= 16, `pha hoai: so luot hop le (${destructive.played})`);

const mutinyStatus = getCohesionStatus(destructive.state);
check(mutinyStatus.status === 'mutiny', `pha hoai: trang thai la mutiny (${mutinyStatus.status})`);
check(mutinyStatus.value === 0, 'pha hoai: gia tri hien thi la 0');
check(
  typeof mutinyStatus.label_vi === 'string' && mutinyStatus.label_vi.length > 0,
  'pha hoai: co nhan tieng Viet'
);
check(
  typeof mutinyStatus.label_en === 'string' && mutinyStatus.label_en.length > 0,
  'pha hoai: co nhan tieng Anh'
);

/* Chon phuong an giu cohesion tot nhat, hoa nhau thi chon ben it
   lam mat niem tin cua vai tro hon. */
const balanced = simulate({
  label: 'can bang',
  pickOption: (ev) =>
    ev.options.reduce((best, o) => {
      const a = o.effects.cohesion_pct ?? 0;
      const b = best.effects.cohesion_pct ?? 0;
      if (a !== b) return a > b ? o : best;
      const ta = Object.values(o.role_trust || {}).reduce((s, v) => s + Math.min(0, v), 0);
      const tb = Object.values(best.role_trust || {}).reduce((s, v) => s + Math.min(0, v), 0);
      return ta > tb ? o : best;
    }),
});

check(balanced.played === 16, `can bang: di het 16 su kien (${balanced.played})`);
check(balanced.state.cohesion > 50, `can bang: cohesion giu tren 50 (${balanced.state.cohesion})`);
check(balanced.state.mutiny === false, 'can bang: khong tan ra');
check(balanced.state.log.length === balanced.played, 'can bang: log ghi du so luot');

const balStatus = getCohesionStatus(balanced.state);
check(balStatus.status === 'good', `can bang: trang thai la good (${balStatus.status})`);

/* Khong su kien nao bi lap. */
const playedIds = balanced.state.log.map((l) => l.eventId);
check(new Set(playedIds).size === playedIds.length, 'khong su kien nao bi lap trong mot luot');
check(playedIds.length === 16, 'ca 16 su kien deu duoc dung toi');

/* Phan ung cua vai tro bi gat phai co ca hai thu tieng. */
let vetoCount = 0;
for (const ev of events) {
  for (const opt of ev.options) {
    const state = createNegotiation({ events, startCohesion: 70 });
    state.current = ev;
    const v = getVetoReaction(state, opt);
    if (!v) continue;
    vetoCount++;
    check(ROLES.includes(v.role), `${ev.id}/${opt.id}: phan ung dung vai tro`);
    check(!!v.line_vi && !!v.line_en, `${ev.id}/${opt.id}: phan ung co ca hai thu tieng`);
    check(
      !v.line_vi.includes('\u2014') && !v.line_en.includes('\u2014'),
      `${ev.id}/${opt.id}: phan ung khong co em dash`
    );
  }
}
check(vetoCount >= 30, `co phan ung vai tro cho phan lon phuong an (${vetoCount})`);

/* applyChoice phai nem loi khi phuong an khong ton tai. */
{
  const state = createNegotiation({ events, startCohesion: 70 });
  let threw = false;
  state.current = events[0];
  try {
    applyChoice(state, 'khong_ton_tai');
  } catch {
    threw = true;
  }
  check(threw, 'applyChoice: nem loi khi phuong an sai');
}

/* pickNextEvent phai tra null khi het su kien cua phase. */
{
  const state = createNegotiation({ events, startCohesion: 70 });
  let n = 0;
  let ev = pickNextEvent(state, 'surface');
  while (ev) {
    n++;
    ev = pickNextEvent(state, 'surface');
  }
  const surfaceCount = events.filter((e) => e.phase === 'surface').length;
  check(n === surfaceCount, `pickNextEvent: tra het ${surfaceCount} su kien surface roi null (${n})`);
}

/* Cohesion luon nam trong 0..100. */
{
  const state = createNegotiation({ events, startCohesion: 70 });
  state.cohesion = 98;
  state.current = events[0];
  const best = events[0].options.reduce((b, o) =>
    (o.effects.cohesion_pct ?? 0) > (b.effects.cohesion_pct ?? 0) ? o : b
  );
  applyChoice(state, best.id);
  check(state.cohesion <= 100, `cohesion khong vuot 100 (${state.cohesion})`);
}

const summary = getSummary(balanced.state);
check(summary && summary.turns === 16, 'getSummary: dem du so luot');
check(summary.roles.length === 3, 'getSummary: co ba vai tro');

/* ---------- ket qua ---------- */

console.log('\n' + '-'.repeat(56));
console.log(`  PASS ${pass}   FAIL ${fail}`);
if (fail) {
  console.log('\n  Chi tiet loi:');
  for (const f of failures) {
    console.log(`   - ${f.name}${f.detail ? ' :: ' + f.detail : ''}`);
  }
  process.exit(1);
}
console.log('  Tat ca kiem tra deu dat.');
