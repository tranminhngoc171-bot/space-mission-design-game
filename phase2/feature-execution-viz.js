/**
 * feature-execution-viz.js — Hồi 4-5.
 *
 * Trách nhiệm: bản đồ quỹ đạo 2D (Canvas), luồng truyền tin DSN, trạng thái hành
 * trình, nút yêu cầu cắm đèn hiệu ở 75%, và màn tổng kết đối chiếu NASA analogue.
 * Không tính quỹ đạo: hình vẽ là sơ đồ, số liệu lấy từ engine.
 */
(function () {
  'use strict';
  var U = window.Phase2Util;
  var t = U.t;

  function mount(root, engine) {
    var canvas = U.el('canvas', { class: 'p2-canvas', width: 720, height: 380 });
    var statusLine = U.el('div', { class: 'p2-status' });
    var progressLine = U.el('div', { class: 'p2-bar-block' }, [
      U.el('div', { class: 'p2-bar-head' }, [
        U.el('span', { text: t('exec.progress') }),
        U.el('span', { class: 'p2-num', 'data-role': 'progress', text: '0%' })
      ]),
      U.el('div', { class: 'p2-bar-track' }, [
        U.el('div', { class: 'p2-bar-fill', 'data-role': 'progress-fill', style: 'width:0%' })
      ])
    ]);
    var actionSlot = U.el('div', { class: 'p2-actions' });
    var debriefSlot = U.el('div', { class: 'p2-debrief' });

    U.clear(root).appendChild(
      U.el('section', { class: 'p2-panel p2-panel-viz' }, [
        U.el('div', { class: 'p2-panel-head' }, [
          U.el('h2', { class: 'p2-h2', text: t('exec.heading') }),
          U.el('span', { class: 'p2-badge', 'data-role': 'statusbadge', text: t('exec.statusDesigning') })
        ]),
        U.el('div', { class: 'p2-canvas-wrap' }, [canvas]),
        statusLine,
        progressLine,
        actionSlot,
        debriefSlot
      ])
    );

    var ctx = canvas.getContext('2d');
    var shownProgress = 0;
    var raf = null;
    var lastFull = engine.getFullState();

    /* ---------- vẽ ---------- */
    function draw() {
      var full = lastFull;
      var state = full.state;
      var mars = full.computed.mars;
      var w = canvas.width;
      var h = canvas.height;
      var cx = w * 0.13;
      var cy = h * 0.52;
      var r1 = h * 0.17;
      var r2 = h * 0.36;

      ctx.clearRect(0, 0, w, h);

      /* quỹ đạo nền */
      ctx.strokeStyle = 'rgba(120, 160, 200, 0.18)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(cx, cy, r1, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx, cy, r2, 0, Math.PI * 2); ctx.stroke();

      /* Mặt Trời */
      var sun = ctx.createRadialGradient(cx, cy, 0, cx, cy, 26);
      sun.addColorStop(0, 'rgba(255, 214, 130, 0.95)');
      sun.addColorStop(1, 'rgba(255, 160, 60, 0)');
      ctx.fillStyle = sun;
      ctx.beginPath(); ctx.arc(cx, cy, 26, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#ffd27a';
      ctx.beginPath(); ctx.arc(cx, cy, 9, 0, Math.PI * 2); ctx.fill();

      /* Trái Đất */
      var earthAngle = Math.PI * 1.18;
      var ex = cx + Math.cos(earthAngle) * r1;
      var ey = cy + Math.sin(earthAngle) * r1;
      ctx.fillStyle = '#4ea8ff';
      ctx.beginPath(); ctx.arc(ex, ey, 7, 0, Math.PI * 2); ctx.fill();

      /* Sao Hỏa */
      var marsAngle = -0.18;
      var mx = cx + Math.cos(marsAngle) * r2;
      var my = cy + Math.sin(marsAngle) * r2;
      ctx.fillStyle = mars.dustStormActive ? '#c9683f' : '#d9825a';
      ctx.beginPath(); ctx.arc(mx, my, 9, 0, Math.PI * 2); ctx.fill();
      if (mars.dustStormActive) {
        ctx.strokeStyle = 'rgba(201, 104, 63, 0.35)';
        ctx.lineWidth = 5;
        ctx.beginPath(); ctx.arc(mx, my, 15, 0, Math.PI * 2); ctx.stroke();
      }

      /* đường chuyển tiếp: Hohmann cong, Fast Transit gần thẳng */
      var fast = state.selection.trajectoryId === 'FAST_CONJUNCTION_ASSIST';
      var ctrlX = fast ? (ex + mx) / 2 - 10 : cx + (ex + mx) / 2 * 0.62;
      var ctrlY = fast ? (ey + my) / 2 - 26 : cy - r2 * 0.42;
      ctx.strokeStyle = fast ? '#ffa94d' : '#4ea8ff';
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(ex, ey);
      ctx.quadraticCurveTo(ctrlX, ctrlY, mx, my);
      ctx.stroke();

      /* tàu */
      if (state.execution.status !== 'DESIGNING') {
        var p = shownProgress / 100;
        var qx = (1 - p) * (1 - p) * ex + 2 * (1 - p) * p * ctrlX + p * p * mx;
        var qy = (1 - p) * (1 - p) * ey + 2 * (1 - p) * p * ctrlY + p * p * my;
        ctx.fillStyle = '#eaf2ff';
        ctx.beginPath(); ctx.arc(qx, qy, 4.5, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = 'rgba(234, 242, 255, 0.35)';
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(qx, qy, 9, 0, Math.PI * 2); ctx.stroke();
      }

      /* sóng DSN bay sang Sao Hỏa khi đã phóng */
      if (state.execution.status === 'LAUNCHED' || state.execution.status === 'PROXIMITY_WAIT') {
        var t0 = (Date.now() % 2000) / 2000;
        for (var i = 0; i < 3; i++) {
          var phase = (t0 + i / 3) % 1;
          var sx = ex + (mx - ex) * phase;
          var sy = ey + (my - ey) * phase * 0.5 + Math.sin(phase * Math.PI) * -18;
          ctx.fillStyle = 'rgba(92, 225, 230, ' + (0.65 * (1 - Math.abs(phase - 0.5) * 2)) + ')';
          ctx.beginPath(); ctx.arc(sx, sy, 2.4, 0, Math.PI * 2); ctx.fill();
        }
      }

      /* đèn hiệu bãi đáp */
      if (mars.landingBeaconReady) {
        ctx.strokeStyle = '#35d39a';
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(mx, my + 16, 6, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = '#35d39a';
        ctx.beginPath(); ctx.arc(mx, my + 16, 2.5, 0, Math.PI * 2); ctx.fill();
      }

      /* nhãn */
      ctx.fillStyle = 'rgba(200, 214, 232, 0.55)';
      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.fillText('EARTH', ex - 16, ey - 12);
      ctx.fillText('MARS', mx - 12, my - 14);
      ctx.fillText(fast ? 'FAST TRANSIT' : 'HOHMANN', w * 0.5 - 30, h * 0.12);

      raf = window.requestAnimationFrame(draw);
    }

    function start() { if (!raf) raf = window.requestAnimationFrame(draw); }
    function stop() { if (raf) { window.cancelAnimationFrame(raf); raf = null; } }

    /* ---------- trạng thái ---------- */
    function render(full) {
      lastFull = full;
      var state = full.state;
      var exec = state.execution;
      var statusMap = {
        DESIGNING: t('exec.statusDesigning'),
        LAUNCHED: t('exec.statusLaunched'),
        PROXIMITY_WAIT: t('exec.statusProximity'),
        COMPLETED: t('exec.statusCompleted'),
        FAILED: t('exec.statusFailed')
      };
      var badgeClass = exec.status === 'COMPLETED' ? 'is-green'
        : exec.status === 'FAILED' ? 'is-red'
        : exec.status === 'PROXIMITY_WAIT' ? 'is-yellow' : '';

      var badge = root.querySelector('[data-role="statusbadge"]');
      if (badge) {
        badge.textContent = statusMap[exec.status] || exec.status;
        badge.className = 'p2-badge ' + badgeClass;
      }

      var progressLabel = root.querySelector('[data-role="progress"]');
      if (progressLabel) progressLabel.textContent = Math.round(shownProgress) + '%';
      var progressFill = root.querySelector('[data-role="progress-fill"]');
      if (progressFill) progressFill.style.width = Math.round(shownProgress) + '%';

      U.clear(statusLine).appendChild(
        U.el('div', { class: 'p2-status-row' }, [
          U.el('span', { class: 'p2-status-key', text: 'DSN' }),
          U.el('span', { class: 'p2-status-val', text: t('exec.dsnSend') + ' · ' + full.computed.mars.oneWayLightTimeMin + ' ' + t('app.minutes') })
        ])
      );

      U.clear(actionSlot);
      if (exec.status === 'PROXIMITY_WAIT') {
        actionSlot.appendChild(U.el('p', { class: 'p2-warn', text: t('exec.beaconNeeded') }));
        actionSlot.appendChild(U.el('button', {
          class: 'p2-btn p2-btn-primary', type: 'button', text: t('exec.gotoMars'),
          onclick: function () { window.Phase2Bridge.requestMarsBeacon(); }
        }));
        actionSlot.appendChild(U.el('p', { class: 'p2-muted p2-tiny', text: t('exec.waitingBeacon') }));
      }

      U.clear(debriefSlot);
      if (exec.status === 'COMPLETED' || exec.status === 'FAILED') {
        var m = full.computed.metrics;
        debriefSlot.appendChild(
          U.el('div', { class: 'p2-debrief-card ' + (exec.status === 'COMPLETED' ? 'is-green' : 'is-red') }, [
            U.el('h3', { class: 'p2-debrief-title', text: t('exec.debrief') }),
            U.el('p', { class: 'p2-debrief-reason', text: exec.outcomeReason }),
            U.el('dl', { class: 'p2-debrief-grid' }, [
              row(t('exec.analogue'), full.computed.checklist.nasaAnalogue),
              row(t('exec.flight'), m.totalMissionSols + ' ' + t('exec.sols')),
              row(t('exec.injected'), m.totalInjectedMassKg + ' kg'),
              row(t('exec.dryMass'), m.spacecraftDryMassKg + ' kg (' + U.pct(m.dryMassMargin) + ' margin)'),
              row(t('exec.cost'), m.totalCostM + ' M$')
            ]),
            U.el('button', {
              class: 'p2-btn p2-btn-sm', type: 'button', text: t('exec.restart'),
              onclick: function () { window.location.reload(); }
            })
          ])
        );
      }

      var target = exec.progressPercent || 0;
      var step = function () {
        if (Math.abs(shownProgress - target) < 0.5) { shownProgress = target; }
        else { shownProgress += (target - shownProgress) * 0.08; window.requestAnimationFrame(step); }
        var pl = root.querySelector('[data-role="progress"]');
        if (pl) pl.textContent = Math.round(shownProgress) + '%';
        var pf = root.querySelector('[data-role="progress-fill"]');
        if (pf) pf.style.width = Math.round(shownProgress) + '%';
      };
      window.requestAnimationFrame(step);
    }

    function row(key, value) {
      return U.el('div', { class: 'p2-debrief-row' }, [
        U.el('dt', { text: key }),
        U.el('dd', { class: 'p2-num', text: value })
      ]);
    }

    var unsubscribe = engine.subscribe('state:changed', render);
    window.addEventListener('phase2:lang-changed', function () { render(engine.getFullState()); });
    render(engine.getFullState());
    start();

    return {
      destroy: function () { stop(); unsubscribe(); }
    };
  }

  window.Phase2Features = window.Phase2Features || {};
  window.Phase2Features.executionViz = mount;
})();
