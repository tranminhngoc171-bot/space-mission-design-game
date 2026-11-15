/**
 * bridge-adapter.js — cầu nối hai chiều giữa Giai đoạn 1 (Sao Hỏa) và Giai đoạn 2.
 *
 * Luật: chỉ giao tiếp qua window.CustomEvent + window.MARS_RESCUE_SHARED_STATE.
 * Giai đoạn 1 không bao giờ bị gọi hàm trực tiếp, và file này không sửa gì
 * trong src/ của Giai đoạn 1.
 *
 * Sự kiện:
 *   mars:sos-received      (Phase 1 -> 2)  mở khóa Mission Control
 *   earth:dsn-command-sent (2 -> 1)        yêu cầu phi hành gia cắm đèn hiệu
 *   mars:beacon-deployed   (1 -> 2)        đèn hiệu xong, tàu bắt đầu EDL
 *   phase2:goto-mars       (2 -> 1)        nút chuyển tab trên giao diện
 *   phase2:unlocked        (nội bộ)        UI vừa mở khóa
 *   phase2:launch-blocked  (nội bộ)        bấm phóng khi còn lỗi đỏ
 */
(function () {
  'use strict';

  /* ---------------- tiện ích dựng DOM dùng chung ---------------- */
  var Util = {
    el: function (tag, attrs, children) {
      var node = document.createElement(tag);
      attrs = attrs || {};
      Object.keys(attrs).forEach(function (key) {
        var value = attrs[key];
        if (value === null || value === undefined || value === false) return;
        if (key === 'class') node.className = value;
        else if (key === 'text') node.textContent = value;
        else if (key === 'html') node.innerHTML = value;
        else if (key.indexOf('on') === 0 && typeof value === 'function') {
          node.addEventListener(key.slice(2).toLowerCase(), value);
        } else node.setAttribute(key, String(value));
      });
      var list = Array.isArray(children) ? children : (children === undefined ? [] : [children]);
      list.forEach(function (child) {
        if (child === null || child === undefined || child === false) return;
        node.appendChild(typeof child === 'object' && child.nodeType
          ? child
          : document.createTextNode(String(child)));
      });
      return node;
    },
    clear: function (node) {
      while (node && node.firstChild) node.removeChild(node.firstChild);
      return node;
    },
    pct: function (value) { return Math.round(value * 100) + '%'; },
    num: function (value, digits) {
      var d = digits === undefined ? 1 : digits;
      return Number(value).toFixed(d);
    },
    signed: function (value, unit) { return (value > 0 ? '+' : '') + value + (unit || ''); },
    clamp: function (value, min, max) { return Math.max(min, Math.min(max, value)); },
    /* G / Y / R -> class, một chỗ duy nhất để đổi cách tô màu */
    ryg: function (status) {
      return status === 'G' ? 'is-green' : (status === 'Y' ? 'is-yellow' : 'is-red');
    },
    /* margin 0..1 -> G/Y/R theo ngưỡng 0.35 và 0.20 */
    marginClass: function (margin) {
      if (margin >= 0.35) return 'is-green';
      if (margin >= 0.20) return 'is-yellow';
      return 'is-red';
    },
    t: function (key, vars) { return window.Phase2I18N ? window.Phase2I18N.t(key, vars) : key; }
  };
  window.Phase2Util = Util;

  /* ---------------- trạng thái chia sẻ giữa hai tab ---------------- */
  var SHARED_KEY = 'MARS_RESCUE_SHARED_STATE';
  if (!window[SHARED_KEY]) window[SHARED_KEY] = { phase1: null, phase2: null };
  var shared = window[SHARED_KEY];

  var DEFAULT_SOS = {
    astronautSurvivalSols: 250,
    cropHealthPercent: 75,
    dustStormActive: true,
    earthMarsDistanceKm: 215000000
  };

  var Bridge = {
    engine: null,

    init: function (engine) {
      var self = this;
      this.engine = engine;

      /* Phase 2 -> Phase 1: DSN giao lệnh xong thì báo sang tab Sao Hỏa */
      engine.subscribe('dsn:messageDelivered', function (msg) {
        shared.phase2 = shared.phase2 || {};
        shared.phase2.lastDsnCommand = msg;
        window.dispatchEvent(new CustomEvent('earth:dsn-command-sent', {
          detail: { commandType: msg.commandType, lightTimeMinutes: msg.lightTimeMinutes }
        }));
      });

      /* Gương trạng thái sang shared state để lỡ đổi tab vẫn không lệch nhịp */
      engine.subscribe('state:changed', function (full) {
        shared.phase2 = Object.assign(shared.phase2 || {}, {
          execution: full.state.execution,
          selection: full.state.selection,
          compliance: full.state.compliance,
          canLaunch: full.computed.checklist.canLaunch,
          mars: full.computed.mars
        });
        if (self.pendingBeacon && full.state.execution.status === 'PROXIMITY_WAIT') {
          self.pendingBeacon = false;
          engine.completeMarsGroundPrep();
        }
      });

      engine.subscribe('mission:launchBlocked', function () {
        window.dispatchEvent(new CustomEvent('phase2:launch-blocked'));
      });

      window.addEventListener('mars:sos-received', function (event) {
        self.onSos(event.detail);
      });
      window.addEventListener('mars:beacon-deployed', function (event) {
        self.onBeacon(event.detail);
      });

      /* Nếu Giai đoạn 1 đã phát SOS trước khi trang này mở, chạy lại ngay */
      if (shared.phase1 && shared.phase1.sos) self.onSos(shared.phase1.sos);

      return this;
    },

    onSos: function (detail) {
      var payload = Object.assign({}, DEFAULT_SOS, detail || {});
      shared.phase1 = Object.assign(shared.phase1 || {}, { sos: payload });
      this.engine.initFromPhase1(payload);
      window.dispatchEvent(new CustomEvent('phase2:unlocked', { detail: payload }));
    },

    onBeacon: function (detail) {
      shared.phase1 = Object.assign(shared.phase1 || {}, { beaconDeployed: detail || true });
      /* Nếu đèn hiệu tới trước mốc PROXIMITY_WAIT, engine sẽ bỏ qua vì chỉ hạ
         cánh khi đúng trạng thái. Ghi nhớ lại và hoàn tất khi tới mốc. */
      if (this.engine.getFullState().state.execution.status === 'PROXIMITY_WAIT') {
        this.engine.completeMarsGroundPrep();
      } else {
        this.pendingBeacon = true;
      }
    },

    /* --- dùng cho bảng thử nghiệm và cho nút chuyển tab --- */
    simulateSos: function (overrides) {
      window.dispatchEvent(new CustomEvent('mars:sos-received', {
        detail: Object.assign({}, DEFAULT_SOS, overrides || {})
      }));
    },

    simulateBeaconDeployed: function () {
      window.dispatchEvent(new CustomEvent('mars:beacon-deployed', { detail: { cleared: true } }));
    },

    requestMarsBeacon: function () {
      window.dispatchEvent(new CustomEvent('phase2:goto-mars'));
    },

    shared: shared
  };

  window.Phase2Bridge = Bridge;
})();
