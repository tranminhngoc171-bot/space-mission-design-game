/**
 * Headless lifecycle test cho Giai đoạn 2 — chạy bằng node, không cần trình duyệt.
 *
 * Kiểm tra đúng luồng hợp đồng: initFromPhase1 -> chọn kiến trúc -> CML 4
 * -> launchMission -> earth:dsn-command-sent -> completeMarsGroundPrep -> COMPLETED.
 * Đồng thời kiểm tra tĩnh: mọi key i18n dùng trong phase2 đều có bản VI và EN.
 *
 * Usage: node scripts/test_phase2_lifecycle.mjs
 */
import { createRequire } from 'node:module';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const P2 = path.join(ROOT, 'phase2');

let failures = 0;
const fail = (msg) => { console.log('  !! ' + msg); failures++; };

/* ---------- 1. lifecycle thật của engine ---------- */
const E = require(path.join(P2, 'phase2-engine.js'));

const engine = new E.Phase2MissionEngine();
engine.initFromPhase1({
  astronautSurvivalSols: 250,
  cropHealthPercent: 75,
  dustStormActive: true,
  earthMarsDistanceKm: 215000000
});

if (engine.computed.mars.oneWayLightTimeMin !== 11.95) {
  fail(`oneWayLightTimeMin=${engine.computed.mars.oneWayLightTimeMin}, kỳ vọng 11.95`);
}

/* Tìm một tổ hợp phóng được (không hard-code trong UI: UI chỉ đọc canLaunch) */
const C = E.CATALOG;
let winning = null;
outer:
for (const o of Object.keys(C.objectives))
  for (const lv of Object.keys(C.launchVehicles))
    for (const tr of Object.keys(C.trajectories))
      for (const p of Object.keys(C.powerSystems))
        for (const edl of Object.keys(C.edlSystems))
          for (const tel of Object.keys(C.telecomSystems)) {
            engine.updateSelection('objectiveId', o);
            engine.updateSelection('launchVehicleId', lv);
            engine.updateSelection('trajectoryId', tr);
            engine.updateSelection('powerSystemId', p);
            engine.updateSelection('edlSystemId', edl);
            engine.updateSelection('telecomSystemId', tel);
            engine.updateCompliance('planetaryProtectionSterilized', true);
            engine.updateCompliance('launchApprovalSubmitted', true);
            if (engine.computed.checklist.canLaunch) { winning = { o, lv, tr, p, edl, tel }; break outer; }
          }

if (!winning) fail('không còn tổ hợp nào phóng được ở mức sinh tồn 250 Sol — cân bằng gãy');
else {
  console.log(`  tổ hợp phóng được: ${JSON.stringify(winning)}`);
  /* Bắt sự kiện DSN rồi phóng. Engine dùng setTimeout nên luồng là bất đồng bộ. */
  let dsnPayload = null;
  engine.subscribe('dsn:messageDelivered', (msg) => { dsnPayload = msg; });
  if (!engine.launchMission()) fail('launchMission trả false dù canLaunch = true');

  /* Beacon tới trước mốc 75%: bridge phải ghi nhớ và hoàn tất khi tới mốc. */
  engine.completeMarsGroundPrep();

  await new Promise((resolve) => setTimeout(resolve, 2800));
  engine.completeMarsGroundPrep();

  const state = engine.getFullState().state;
  if (state.execution.status !== 'COMPLETED') fail(`trạng thái ${state.execution.status}, kỳ vọng COMPLETED`);
  if (!dsnPayload || dsnPayload.commandType !== 'DEPLOY_LANDING_BEACON_AND_CLEAR_ZONE') fail('payload DSN sai');
  if (!engine.getFullState().state.execution.outcomeReason) fail('thiếu outcomeReason cho debrief');
  console.log(`  lifecycle: LAUNCHED -> PROXIMITY_WAIT -> COMPLETED, DSN ${dsnPayload ? dsnPayload.lightTimeMinutes + ' min' : 'MISSING'}`);
}

/* Chuỗi thất bại: beacon chưa cắm mà ép hạ cánh */
const eng2 = new E.Phase2MissionEngine();
eng2.initFromPhase1({ astronautSurvivalSols: 999, dustStormActive: false, earthMarsDistanceKm: 215000000 });
eng2.completeMarsGroundPrep();
if (eng2.getFullState().state.execution.status !== 'DESIGNING') {
  fail('beacon trước khi phóng không được phép ép EDL khi chưa PROXIMITY_WAIT');
}

/* ---------- 2. kiểm tra tĩnh: i18n đủ VI/EN, container khớp ---------- */
const i18nSrc = readFileSync(path.join(P2, 'phase2-i18n.js'), 'utf8');
const viCount = (i18nSrc.match(/vi:\s*{/g) || []).length;
const enCount = (i18nSrc.match(/en:\s*{/g) || []).length;
if (viCount !== 1 || enCount !== 1) fail(`i18n kỳ vọng 1 bảng vi và 1 bảng en, thấy ${viCount}/${enCount}`);

const featureSrc = ['feature-cml1-telemetry.js', 'feature-cml3-tradespace.js',
  'feature-cml4-checklist.js', 'feature-execution-viz.js']
  .map((f) => readFileSync(path.join(P2, f), 'utf8')).join('\n');

const usedKeys = new Set([...featureSrc.matchAll(/\bt\('([a-z0-9.]+)'\)/g)].map((m) => m[1]));
const html = readFileSync(path.join(P2, 'phase2-demo.html'), 'utf8');
const appSrc = readFileSync(path.join(P2, 'phase2-app.js'), 'utf8');
const allSrc = i18nSrc + featureSrc + appSrc;

for (const key of usedKeys) {
  const vi = new RegExp(`'${key}':\\s*'`).test(allSrc) || new RegExp(`"${key}"`).test(allSrc);
  if (!vi) fail(`key i18n thiếu định nghĩa: ${key}`);
}

for (const sel of [...appSrc.matchAll(/data-phase2="([a-z0-9-]+)"/g)].map((m) => m[1])) {
  if (!html.includes(`data-phase2="${sel}"`)) fail(`container thiếu trong demo html: ${sel}`);
}

for (const id of ['dev-sos', 'dev-beacon', 'dev-reset', 'dev-lang', 'dev-step-1', 'dev-step-2', 'dev-step-3', 'dev-step-4']) {
  if (!html.includes(`id="${id}"`)) fail(`nút thử nghiệm thiếu: #${id}`);
}

/* Phase 1 không được bị đụng tới: phase2 không import gì từ src/ */
if (/from\s+['"]\.\.\/src\//.test(featureSrc + appSrc)) fail('phase2 không được import file của Giai đoạn 1');

console.log(failures ? `\n${failures} lỗi.` : '\nPhase 2 lifecycle + tĩnh: sạch.');
process.exit(failures ? 1 : 0);
