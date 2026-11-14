/* ui.js — the only file that touches the DOM.
 *
 * It never computes game values. It reads engine output and writes it into
 * elements selected by [data-ui="..."]. Re-skinning = edit css/mission.css.
 * Re-theming = edit the :root tokens. Nothing here needs to change for either.
 */

import { computeMission, emptyDesign, listOptions } from './engine.js';

const $ = (key) => document.querySelectorAll(`[data-ui="${key}"]`);
const one = (key) => document.querySelector(`[data-ui="${key}"]`);
const setText = (key, text) => { for (const el of $(key)) el.textContent = text ?? ''; };
const setHTML = (key, html) => { for (const el of $(key)) el.innerHTML = html; };

const OPT = listOptions();
let design = emptyDesign(OPT.scenarios[0].id);
let lastResult = null;

/* ---------- URL state: a design is shareable, so hot-seat works without a server ---------- */
function readHash() {
  const raw = location.hash.replace(/^#/, '');
  if (!raw) return null;
  try {
    const parsed = JSON.parse(decodeURIComponent(raw));
    if (parsed && parsed.scenarioId && parsed.bus) return parsed;
  } catch { /* ignore */ }
  return null;
}
function writeHash() {
  const encoded = encodeURIComponent(JSON.stringify(design));
  history.replaceState(null, '', `#${encoded}`);
}

/* ---------- screens ---------- */
function show(name) {
  for (const s of document.querySelectorAll('[data-screen]')) {
    s.hidden = s.dataset.screen !== name;
  }
  window.scrollTo({ top: 0, behavior: 'instant' });
}

/* ---------- option rendering ---------- */
const money = (v) => `$${v.toFixed(1)}M`;
const kg = (v) => `${v} kg`;
const watts = (v) => `${v} W`;

function optionButton({ pressed, disabled, name, meta, note, onClick }) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'opt';
  b.setAttribute('aria-pressed', String(!!pressed));
  if (disabled) b.disabled = true;
  b.innerHTML = `<span class="opt-name"></span><span class="opt-meta"></span>` +
    (note ? `<span class="opt-note"></span>` : '');
  b.querySelector('.opt-name').textContent = name;
  b.querySelector('.opt-meta').textContent = meta;
  if (note) b.querySelector('.opt-note').textContent = note;
  if (!disabled) b.addEventListener('click', onClick);
  return b;
}

function renderBus() {
  const host = one('opt.bus');
  host.replaceChildren(...OPT.bus.map((b) => optionButton({
    pressed: design.bus === b.id,
    name: b.name,
    meta: `${kg(b.dry_mass_kg)} · ${money(b.cost_musd)} · ${b.max_instruments} khe`,
    note: b.blurb,
    onClick: () => { design.bus = b.id; renderAll(); },
  })));
}

function renderPower() {
  const a = one('opt.power');
  a.replaceChildren(...OPT.power.map((p) => optionButton({
    pressed: design.power === p.id,
    name: p.name,
    meta: `${watts(p.power_gen_w)} · ${kg(p.mass_kg)} · ${money(p.cost_musd)}`,
    note: p.tradeoff,
    onClick: () => { design.power = p.id; renderAll(); },
  })));
  const b = one('opt.battery');
  b.replaceChildren(...OPT.battery.map((x) => optionButton({
    pressed: design.battery === x.id,
    name: x.name,
    meta: `${x.capacity_wh} Wh · ${kg(x.mass_kg)} · ${money(x.cost_musd)}`,
    note: x.blurb,
    onClick: () => { design.battery = x.id; renderAll(); },
  })));
}

function renderInstruments() {
  const bus = OPT.bus.find((b) => b.id === design.bus);
  const full = design.instruments.length >= bus.max_instruments;
  const host = one('opt.instruments');
  host.replaceChildren(...OPT.instruments.map((i) => {
    const on = design.instruments.includes(i.id);
    return optionButton({
      pressed: on,
      disabled: !on && full,
      name: i.name,
      meta: `${kg(i.mass_kg)} · ${watts(i.power_w)} · ${money(i.cost_musd)} · ${i.data_gb_day} GB/d`,
      note: `khoa học ${i.science_value} — ${i.tradeoff}`,
      onClick: () => {
        design.instruments = on
          ? design.instruments.filter((x) => x !== i.id)
          : [...design.instruments, i.id];
        renderAll();
      },
    });
  }));
  setText('payload.count', `${design.instruments.length}/${bus.max_instruments}`);
}

function renderOrbit() {
  const host = one('opt.orbit');
  host.replaceChildren(...OPT.orbits.map((o) => optionButton({
    pressed: design.orbit === o.id,
    name: o.name,
    meta: `${o.revisit_hours} h revisit · ${o.comm_window_pct}% cửa sổ · ${o.downlink_mbps} Mbps`,
    note: o.tradeoff,
    onClick: () => { design.orbit = o.id; renderAll(); },
  })));
}

function renderLauncher() {
  const host = one('opt.launcher');
  host.replaceChildren(...OPT.launchers.map((l) => {
    const cap = (l.capacity_kg && l.capacity_kg[design.orbit]) || 0;
    return optionButton({
      pressed: design.launcher === l.id,
      disabled: cap === 0,
      name: l.name,
      meta: cap > 0 ? `${cap} kg tới quỹ đạo · ${money(l.cost_musd)}` : `không tới được quỹ đạo này`,
      note: cap > 0 ? `${l.lead_time_months} tháng chờ phóng` : null,
      onClick: () => { design.launcher = l.id; renderAll(); },
    });
  }));
}

/* ---------- live resource panel ---------- */
function renderResources(preview) {
  const rows = Object.entries(preview.resources).map(([key, r]) => `
    <div class="res" data-status="${r.status}" data-res="${key}">
      <div class="res-head">
        <span class="res-label">${r.label}</span>
        <span class="res-val num">${r.value.toFixed(1)} / ${r.limit.toFixed(1)} ${r.unit}</span>
      </div>
      <div class="res-track"><div class="res-fill" style="width:${Math.min(100, r.pct).toFixed(1)}%"></div></div>
      <span class="res-detail">${r.detail}</span>
    </div>`).join('');
  setHTML('res.list', rows);

  const gates = preview.checks.map((c) => `
    <div class="gate" data-pass="${c.pass}">
      <span class="gate-dot"></span>
      <span class="gate-label">${c.label}</span>
    </div>`).join('');
  setHTML('checks.list', gates);

  const blocked = preview.checks.filter((c) => !c.pass);
  setText('design.warning', blocked.length
    ? `${blocked.length} cổng chưa đạt — sứ mệnh sẽ không rời bệ phóng.`
    : 'Mọi cổng tương thích đã đạt. Sẵn sàng mô phỏng.');
}

/* ---------- briefing ---------- */
function renderBriefing() {
  const s = OPT.scenarios.find((x) => x.id === design.scenarioId) || OPT.scenarios[0];
  setText('scenario.name', s.name);
  setText('scenario.story', s.story);
  setText('scenario.difficulty', s.difficulty);
  setText('scenario.budget', money(s.budget_musd));
  setText('scenario.duration', `${s.duration_months} tháng`);
  setText('scenario.objcount', `${s.objectives.length}`);
  setText('scenario.hint', Array.isArray(s.hints) ? s.hints[0] : (s.hints || ''));
  setHTML('scenario.objectives', s.objectives.map((o) => `
    <tr>
      <td>${o.label}</td>
      <td class="ta-r num">${o.operator === 'min' ? '≥' : '≤'} ${o.target}</td>
      <td class="ta-r num">${(o.weight * 100).toFixed(0)}%</td>
    </tr>`).join(''));
}

/* ---------- debrief ---------- */
const bandLabel = {
  excellent: 'xuất sắc', good: 'tốt', marginal: 'chật vật', failed: 'thất bại',
};

function renderDebrief(result) {
  setText('debrief.score', `${result.score.total}`);
  setText('debrief.band', bandLabel[result.score.band] || result.score.band);

  setHTML('debrief.parts', [
    ['Sứ mệnh', result.score.mission_success, '40%'],
    ['Khoa học', result.score.science_value, '25%'],
    ['Hiệu quả', result.score.resource_efficiency, '20%'],
    ['Bền bỉ', result.score.robustness, '15%'],
  ].map(([k, v, w]) => `
    <div class="part"><span class="part-key">${k} · ${w}</span><span class="part-val num">${v}</span></div>`).join(''));

  setHTML('debrief.checks', result.checks.map((c) => `
    <li class="check-item" data-pass="${c.pass}">
      <div class="item-head"><span>${c.label}</span><span class="num">${c.pass ? 'ĐẠT' : 'KHÔNG'}</span></div>
      <div class="item-msg">${c.detail}</div>
      ${c.fix ? `<div class="item-fix">→ ${c.fix}</div>` : ''}
    </li>`).join(''));

  setHTML('debrief.objectives', result.objectives.map((o) => `
    <li class="check-item" data-pass="${o.pass}">
      <div class="item-head">
        <span>${o.label}</span>
        <span class="num">${o.actual === null ? '—' : o.actual.toFixed(1)} / ${o.operator === 'min' ? '≥' : '≤'} ${o.target}</span>
      </div>
      <div class="item-msg">trọng số ${(o.weight * 100).toFixed(0)}%${o.pass ? '' : ` · thiếu ${o.gap.toFixed(1)}`}</div>
    </li>`).join(''));

  setHTML('debrief.events', result.events.length
    ? result.events.map((e) => `
      <li class="event-item">
        <div class="item-head"><span>${e.name}</span><span class="item-area">${e.phase}</span></div>
        <div class="item-msg">${e.narrative}</div>
      </li>`).join('')
    : '<li class="event-item"><div class="item-msg">Không sự kiện nào xảy ra trong lần chạy này.</div></li>');

  setHTML('debrief.analysis', result.analysis.map((a) => `
    <li class="analysis-item" data-level="${a.level}">
      <div class="item-head"><span class="item-area">${a.area}</span></div>
      <div class="item-msg">${a.message}</div>
      ${a.fix ? `<div class="item-fix">→ ${a.fix}</div>` : ''}
    </li>`).join(''));
}

/* ---------- orchestration ---------- */
function renderAll() {
  renderBriefing();
  renderBus();
  renderPower();
  renderInstruments();
  renderOrbit();
  renderLauncher();
  renderResources(computeMission(design, design.scenarioId, { seed: 1 }));
  writeHash();
}

function wire() {
  const select = one('select.scenario');
  select.replaceChildren(...OPT.scenarios.map((s) => {
    const o = document.createElement('option');
    o.value = s.id;
    o.textContent = s.name;
    return o;
  }));
  select.value = design.scenarioId;
  select.addEventListener('change', () => {
    const fresh = emptyDesign(select.value);
    design = { ...fresh, instruments: design.instruments };
    design.duration_months = fresh.duration_months;
    renderAll();
  });

  one('btn.start').addEventListener('click', () => show('design'));
  one('btn.reset').addEventListener('click', () => {
    design = emptyDesign(design.scenarioId);
    renderAll();
    show('briefing');
  });
  one('btn.back').addEventListener('click', () => show('design'));
  one('btn.share').addEventListener('click', async (e) => {
    try {
      await navigator.clipboard.writeText(location.href);
      e.target.textContent = 'Đã sao chép';
    } catch {
      e.target.textContent = 'Sao chép thủ công từ thanh địa chỉ';
    }
  });

  one('btn.simulate').addEventListener('click', () => {
    const seed = Math.floor(Math.random() * 100000);
    lastResult = computeMission(design, design.scenarioId, { seed });
    renderDebrief(lastResult);
    show('debrief');
  });
}

/* ---------- boot ---------- */
const fromHash = readHash();
if (fromHash) design = { ...emptyDesign(fromHash.scenarioId), ...fromHash };

wire();
renderAll();
show('briefing');

/* Exposed for console debugging and for the smoke test in CI. */
window.__mission = { computeMission, getDesign: () => design, getLast: () => lastResult, listOptions };
