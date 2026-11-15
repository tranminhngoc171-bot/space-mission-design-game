/**
 * phase2-app.js — điều phối Giai đoạn 2.
 *
 * Tạo engine duy nhất (window.phase2Engine), nối bridge, mount bốn feature module
 * độc lập, và định tuyến màn hình theo state.currentCmlStep + execution.status.
 * Không chứa công thức nào.
 */
(function () {
  'use strict';
  var U = window.Phase2Util;
  var t = U.t;

  var engine = new window.RescueMissionEngine.Phase2MissionEngine();
  window.phase2Engine = engine;

  window.Phase2Bridge.init(engine);

  /* ---------- mount feature ---------- */
  var mounts = [];
  function mountFeature(name, selector) {
    var root = document.querySelector(selector);
    var factory = window.Phase2Features[name];
    if (!root || !factory) {
      if (window.console) console.warn('[phase2] thiếu root hoặc feature:', name, selector);
      return;
    }
    mounts.push(factory(root, engine));
  }

  mountFeature('cml1Telemetry', '[data-phase2="cml1"]');
  mountFeature('cml3TradeSpace', '[data-phase2="cml3"]');
  mountFeature('cml4Checklist', '[data-phase2="cml4"]');
  mountFeature('executionViz', '[data-phase2="viz"]');

  /* ---------- định tuyến hồi ---------- */
  function route(full) {
    var step = full.state.currentCmlStep;
    var executing = full.state.execution.status !== 'DESIGNING';
    var effective = executing ? 4 : step;

    document.querySelectorAll('[data-step]').forEach(function (section) {
      section.hidden = Number(section.dataset.step) !== effective;
    });

    document.querySelectorAll('[data-step-tabs] .p2-tab').forEach(function (tab) {
      tab.classList.toggle('is-active', Number(tab.dataset.for) === effective);
    });

    var vizPanel = document.querySelector('[data-phase2="viz"]');
    if (vizPanel) vizPanel.hidden = effective < 2 && !executing;

    var headerSol = document.querySelector('[data-role="header-sol"]');
    var headerLight = document.querySelector('[data-role="header-light"]');
    var headerSignal = document.querySelector('[data-role="header-signal"]');
    var mars = full.computed.mars;
    if (headerSol) headerSol.textContent = mars.astronautSurvivalSols + ' ' + t('app.sol');
    if (headerLight) headerLight.textContent = mars.oneWayLightTimeMin + ' ' + t('app.minutes');
    if (headerSignal) {
      headerSignal.textContent = mars.signalReceived ? t('app.signalLocked') : t('app.signalWait');
      headerSignal.className = 'p2-badge ' + (mars.signalReceived ? 'is-green' : 'is-locked');
    }
    document.body.classList.toggle('is-unlocked', mars.signalReceived);
  }

  engine.subscribe('state:changed', route);
  window.addEventListener('phase2:unlocked', function () { route(engine.getFullState()); });
  window.addEventListener('phase2:lang-changed', function () { route(engine.getFullState()); });
  route(engine.getFullState());

  /* ---------- bảng thử nghiệm ---------- */
  function bind(id, handler) {
    var node = document.querySelector('#' + id);
    if (node) node.addEventListener('click', handler);
  }

  bind('dev-sos', function () { window.Phase2Bridge.simulateSos(); });
  bind('dev-beacon', function () { window.Phase2Bridge.simulateBeaconDeployed(); });
  bind('dev-reset', function () { window.location.reload(); });
  bind('dev-lang', function () {
    var next = window.Phase2I18N.getLang() === 'vi' ? 'en' : 'vi';
    window.Phase2I18N.setLang(next);
  });

  [1, 2, 3, 4].forEach(function (n) {
    bind('dev-step-' + n, function () { engine.setCmlStep(n); });
  });

  /* Nút chuyển tab trên giao diện phát sự kiện này; nếu không có Giai đoạn 1
     đang chạy (chế độ demo độc lập) thì tự giả lập đèn hiệu để khỏi kẹt. */
  window.addEventListener('phase2:goto-mars', function () {
    var tab = document.querySelector('[data-role="mars-tab-link"]');
    if (tab) { tab.setAttribute('data-requested', 'true'); tab.classList.add('is-pulse'); }
    if (document.body.dataset.phase1 === 'connected') return;
    document.body.classList.add('is-demo');
  });

  window.addEventListener('phase2:launch-blocked', function () {
    var root = document.querySelector('[data-phase2="cml4"]');
    if (!root) return;
    root.classList.add('is-shake');
    window.setTimeout(function () { root.classList.remove('is-shake'); }, 450);
  });

  window.addEventListener('beforeunload', function () {
    mounts.forEach(function (m) { if (m && m.destroy) m.destroy(); });
  });
})();
