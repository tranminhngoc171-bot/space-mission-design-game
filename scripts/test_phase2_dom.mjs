/**
 * Test tích hợp DOM cho Giai đoạn 2, không cần trình duyệt.
 *
 * Máy này không có Chromium nên không lái được browser thật. Thay vào đó dựng
 * một shim DOM tối thiểu (chỉ những API mà phase2/ dùng) rồi chạy đúng 8 file
 * theo đúng thứ tự script trong phase2-demo.html. Mục đích: bắt lỗi runtime
 * (undefined, sai selector, render nổ) mà node --check không thấy.
 *
 * Usage: node scripts/test_phase2_dom.mjs
 */
import vm from 'node:vm';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const P2 = path.join(ROOT, 'phase2');
let failures = 0;
const fail = (m) => { console.log('  !! ' + m); failures++; };

/* ---------------- shim DOM ---------------- */
class El {
  constructor(tag) {
    this.nodeType = 1;
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.attrs = {};
    this.dataset = {};
    this.style = {};
    this.listeners = {};
    this._text = undefined;
    this._class = '';
    this.parentNode = null;
    this.hidden = false;
    this.disabled = false;
  }
  get firstChild() { return this.children[0] || null; }
  get textContent() {
    if (this._text !== undefined) return this._text;
    return this.children.map((c) => c.textContent).join(' ');
  }
  set textContent(v) { this._text = String(v); this.children = []; }
  get className() { return this._class; }
  set className(v) { this._class = String(v); }
  get classList() {
    const self = this;
    return {
      add: (c) => { if (!self._class.split(' ').includes(c)) self._class += (self._class ? ' ' : '') + c; },
      remove: (c) => { self._class = self._class.split(' ').filter((x) => x !== c).join(' '); },
      toggle: (c, on) => { on ? self.classList.add(c) : self.classList.remove(c); },
      contains: (c) => self._class.split(' ').includes(c)
    };
  }
  appendChild(child) {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }
  removeChild(child) {
    this.children = this.children.filter((c) => c !== child);
    return child;
  }
  replaceChildren(...kids) { this.children = []; kids.forEach((k) => this.appendChild(k)); }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
    if (k.startsWith('data-')) this.dataset[k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = String(v);
    if (k === 'disabled') this.disabled = true;
    if (k === 'hidden') this.hidden = true;
  }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); }
  dispatch(type, ev) { (this.listeners[type] || []).forEach((fn) => fn(ev)); }
  getContext() {
    const noop = () => {};
    return {
      clearRect: noop, beginPath: noop, arc: noop, stroke: noop, fill: noop, fillText: noop,
      moveTo: noop, lineTo: noop, quadraticCurveTo: noop, setLineDash: noop,
      createRadialGradient: () => ({ addColorStop: noop }),
      save: noop, restore: noop,
      set fillStyle(v) {}, set strokeStyle(v) {}, set lineWidth(v) {}, set font(v) {}
    };
  }
  matches(sel) { return matchSel(this, sel); }
  querySelector(sel) { return descendants(this).find((n) => matchSel(n, sel)) || null; }
  querySelectorAll(sel) { return descendants(this).filter((n) => matchSel(n, sel)); }
}

function descendants(node, out = []) {
  for (const c of node.children || []) {
    if (c.nodeType === 1) out.push(c);
    descendants(c, out);
  }
  return out;
}

function matchSel(node, sel) {
  sel = sel.trim();
  if (sel.startsWith('#')) return node.attrs.id === sel.slice(1);
  if (sel.startsWith('.')) return node.classList.contains(sel.slice(1));
  const attr = sel.match(/^\[([a-zA-Z0-9-]+)(?:="([^"]*)")?\]$/);
  if (attr) {
    const [, name, value] = attr;
    if (!(name in node.attrs)) return false;
    return value === undefined ? true : node.attrs[name] === value;
  }
  return node.tagName === sel.toUpperCase();
}

class TextNode {
  constructor(text) { this.nodeType = 3; this._text = String(text); }
  get textContent() { return this._text; }
}

const body = new El('body');
body.attrs['data-phase1'] = 'disconnected';

/* trang demo: tạo đúng các container và nút mà phase2-app.js tìm */
const stage = new El('main');
body.appendChild(stage);
const sectionFor = (step) => {
  const s = new El('section');
  s.setAttribute('data-step', String(step));
  if (step !== 1) s.hidden = true;
  return s;
};
const steps = [1, 2, 3, 4].map((n) => { const s = sectionFor(n); stage.appendChild(s); return s; });
const roots = {};
for (const name of ['cml1', 'cml3', 'cml4']) {
  const root = new El('div');
  root.setAttribute('data-phase2', name);
  steps[name === 'cml1' ? 0 : name === 'cml3' ? 1 : 2].appendChild(root);
  roots[name] = root;
}
const vizRoot = new El('div');
vizRoot.setAttribute('data-phase2', 'viz');
vizRoot.hidden = true;
stage.appendChild(vizRoot);
roots.viz = vizRoot;

const tabBar = new El('nav');
tabBar.setAttribute('data-step-tabs', '');
for (const n of [1, 2, 3, 4]) {
  const t = new El('button');
  t.className = 'p2-tab';
  t.setAttribute('data-for', String(n));
  tabBar.appendChild(t);
}
body.appendChild(tabBar);
for (const id of ['dev-sos', 'dev-beacon', 'dev-reset', 'dev-lang', 'dev-step-1', 'dev-step-2', 'dev-step-3', 'dev-step-4']) {
  const b = new El('button');
  b.setAttribute('id', id);
  body.appendChild(b);
}
for (const role of ['header-sol', 'header-light', 'header-signal']) {
  const s = new El('span');
  s.setAttribute('data-role', role);
  body.appendChild(s);
}

const document = {
  body,
  createElement: (tag) => new El(tag),
  createTextNode: (text) => new TextNode(text),
  querySelector: (sel) => (matchSel(body, sel) ? body : body.querySelector(sel)),
  querySelectorAll: (sel) => descendants(body).filter((n) => matchSel(n, sel))
};

const listeners = {};
const windowObj = {
  document,
  localStorage: { getItem: () => null, setItem: () => {} },
  location: { reload: () => {} },
  addEventListener: (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); },
  dispatchEvent: (ev) => { (listeners[ev.type] || []).forEach((fn) => fn(ev)); return true; },
  requestAnimationFrame: (fn) => setTimeout(() => fn(Date.now()), 0),
  cancelAnimationFrame: (id) => clearTimeout(id),
  setTimeout, clearTimeout, console,
  CustomEvent: class { constructor(type, opts) { this.type = type; this.detail = opts && opts.detail; } },
  Math, Date, JSON, Number, Object, Array, String, Boolean, RegExp, Error
};
windowObj.window = windowObj;
windowObj.self = windowObj;

const context = vm.createContext(windowObj);

/* ---------------- chạy 8 file theo đúng thứ tự trong phase2-demo.html ---------------- */
const ORDER = [
  'phase2-engine.js', 'phase2-i18n.js', 'bridge-adapter.js',
  'feature-cml1-telemetry.js', 'feature-cml3-tradespace.js',
  'feature-cml4-checklist.js', 'feature-execution-viz.js', 'phase2-app.js'
];
for (const file of ORDER) {
  const code = readFileSync(path.join(P2, file), 'utf8');
  try { vm.runInContext(code, context, { filename: file }); }
  catch (err) { fail(`${file} nổ khi nạp: ${err.message}\n     ${(err.stack || '').split('\n').slice(0, 4).join('\n     ')}`); }
}

/* ---------------- kiểm tra ---------------- */
if (!windowObj.phase2Engine) fail('phase2-app.js không tạo window.phase2Engine');
if (!windowObj.Phase2Features || Object.keys(windowObj.Phase2Features).length !== 4) {
  fail('thiếu feature module: ' + Object.keys(windowObj.Phase2Features || {}).join(','));
}
if (!windowObj.Phase2Bridge) fail('bridge-adapter.js không gắn window.Phase2Bridge');

const standby = roots.cml1.textContent;
if (!/CHỜ TÍN HIỆU|WAITING FOR THE DISTRESS/.test(standby)) fail('màn chờ không render đúng: ' + standby.slice(0, 80));

/* SOS mở khóa toàn bộ */
windowObj.Phase2Bridge.simulateSos({ astronautSurvivalSols: 250, dustStormActive: true, earthMarsDistanceKm: 215000000 });
const afterSos = roots.cml1.textContent;
if (!/250/.test(afterSos)) fail('sau SOS, telemetry sinh tồn không hiện số 250');
if (!/11\.95/.test(roots.cml1.textContent + body.textContent)) fail('độ trễ ánh sáng 11.95 không hiện ở header/telemetry');

/* CML 4 phải render đủ 8 dòng kiểm duyệt */
const checkRows = descendants(roots.cml4).filter((n) => n.classList.contains('p2-check'));
if (checkRows.length !== 8) fail(`CML 4 render ${checkRows.length} dòng, kỳ vọng 8`);

/* Nút launch phải bị khoá khi còn lỗi đỏ */
const launchBtn = descendants(roots.cml4).find((n) => n.classList.contains('p2-btn-launch'));
if (!launchBtn) fail('không tìm thấy nút LAUNCH');
else if (!launchBtn.classList.contains('is-locked')) fail('nút LAUNCH phải bị khoá khi checklist chưa đạt');

/* Cấu hình thắng: mở khoá và phóng */
const eng = windowObj.phase2Engine;
eng.updateSelection('objectiveId', 'RESUPPLY_BIONUTRIENTS');
eng.updateSelection('launchVehicleId', 'SLS_HEAVY');
eng.updateSelection('trajectoryId', 'FAST_CONJUNCTION_ASSIST');
eng.updateSelection('powerSystemId', 'RTG_PLUTONIUM');
eng.updateSelection('edlSystemId', 'AIRBAG_CHUTE');
eng.updateSelection('telecomSystemId', 'KA_BAND_UHF_RELAY');
eng.updateCompliance('planetaryProtectionSterilized', true);
eng.updateCompliance('launchApprovalSubmitted', true);

const launchBtn2 = descendants(roots.cml4).find((n) => n.classList.contains('p2-btn-launch'));
if (launchBtn2 && launchBtn2.classList.contains('is-locked')) fail('cấu hình thắng vẫn bị khoá LAUNCH');

eng.launchMission();
await new Promise((r) => setTimeout(r, 2800));
windowObj.Phase2Bridge.simulateBeaconDeployed();

const status = eng.getFullState().state.execution.status;
if (status !== 'COMPLETED') fail(`trạng thái cuối ${status}, kỳ vọng COMPLETED`);

const vizText = roots.viz.textContent;
if (!/HẠ CÁNH THÀNH CÔNG|LANDING SUCCESSFUL/.test(vizText)) fail('màn tổng kết không hiện trạng thái thành công');
if (!/Curiosity|Pathfinder|Architecture/.test(vizText)) fail('màn tổng kết thiếu NASA analogue');

/* Shared state phải được bridge ghi lại */
const shared = windowObj.MARS_RESCUE_SHARED_STATE;
if (!shared || !shared.phase2 || !shared.phase2.execution) fail('shared state không được cập nhật');
if (!shared.phase2.lastDsnCommand) fail('shared state thiếu lệnh DSN cuối');

/* Đổi ngôn ngữ không được nổ */
try { windowObj.Phase2I18N.setLang('en'); } catch (e) { fail('đổi sang EN nổ: ' + e.message); }

console.log(failures ? `\n${failures} lỗi.` : '\nPhase 2 DOM integration: sạch.');
process.exit(failures ? 1 : 0);
