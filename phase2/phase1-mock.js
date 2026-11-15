/**
 * phase1-mock.js — bộ giả lập Giai đoạn 1 để test Giai đoạn 2 độc lập.
 *
 * Nó KHÔNG phải Giai đoạn 1 thật. Nó chỉ phát đúng ba sự kiện trong hợp đồng,
 * với dữ liệu do người test chỉnh bằng thanh trượt, để kiểm tra toàn bộ đường
 * đi của Giai đoạn 2 mà không cần chạy game sinh tồn.
 *
 * Sự kiện phát ra: mars:sos-received, mars:beacon-deployed
 * Sự kiện nghe:   earth:dsn-command-sent (mở khoá nhiệm vụ cắm đèn hiệu)
 */
(function () {
  'use strict';
  var U = window.Phase2Util;

  var PRESETS = {
    easy: { label: 'Dễ: 320 Sol', sols: 320, crop: 82, dust: false, distanceKm: 180000000 },
    normal: { label: 'Chuẩn: 250 Sol', sols: 250, crop: 75, dust: true, distanceKm: 215000000 },
    hard: { label: 'Khó: 200 Sol', sols: 200, crop: 48, dust: true, distanceKm: 380000000 }
  };

  function mount(root) {
    var state = { sols: 250, crop: 75, dust: true, distanceKm: 215000000 };
    var beaconUnlocked = false;
    var beaconDone = false;
    var logEntries = [];

    /* ---------- nhật ký sự kiện ---------- */
    function log(name, detail) {
      var time = new Date().toLocaleTimeString('vi-VN');
      logEntries.unshift({ time: time, name: name, detail: detail });
      if (logEntries.length > 12) logEntries.pop();
      renderLog();
    }

    function renderLog() {
      var host = root.querySelector('[data-role="p1-log"]');
      if (!host) return;
      U.clear(host);
      if (!logEntries.length) {
        host.appendChild(U.el('p', { class: 'p2-tiny', text: 'Chưa có sự kiện nào. Bấm «Gửi SOS» để bắt đầu.' }));
        return;
      }
      logEntries.forEach(function (entry) {
        host.appendChild(U.el('div', { class: 'p2-log-row' }, [
          U.el('span', { class: 'p2-log-time p2-num', text: entry.time }),
          U.el('span', { class: 'p2-log-name p2-num', text: entry.name }),
          U.el('span', { class: 'p2-log-detail', text: entry.detail || '' })
        ]));
      });
    }

    /* ---------- điều khiển ---------- */
    function slider(key, label, min, max, step, format) {
      var readout = U.el('span', { class: 'p2-num p2-slider-val', text: format(state[key]) });
      var input = U.el('input', {
        type: 'range', min: min, max: max, step: step, value: state[key],
        class: 'p2-slider',
        'aria-label': label
      });
      input.addEventListener('input', function () {
        state[key] = Number(input.value);
        readout.textContent = format(state[key]);
        var light = root.querySelector('[data-role="p1-light"]');
        if (light) light.textContent = (state.distanceKm / 299792.458 / 60).toFixed(2) + ' phút';
      });
      return U.el('label', { class: 'p2-slider-row' }, [
        U.el('span', { class: 'p2-slider-key', text: label }),
        input,
        readout
      ]);
    }

    function render() {
      U.clear(root).appendChild(
        U.el('section', { class: 'p2-panel p2-panel-mock' }, [
          U.el('div', { class: 'p2-panel-head' }, [
            U.el('h2', { class: 'p2-h2', text: 'GIAI ĐOẠN 1 (GIẢ LẬP) · SAO HỎA' }),
            U.el('span', { class: 'p2-badge is-locked', text: 'MOCK' })
          ]),
          U.el('p', { class: 'p2-muted', text: 'Đây không phải game sinh tồn thật. Nó chỉ phát đúng ba sự kiện trong hợp đồng với dữ liệu dưới đây, để test Giai đoạn 2.' }),

          U.el('div', { class: 'p2-mock-grid' }, [
            slider('sols', 'Phi hành gia còn sống (Sol)', 120, 420, 10, function (v) { return v + ' Sol'; }),
            slider('crop', 'Sức khỏe vườn cây (%)', 0, 100, 5, function (v) { return v + '%'; }),
            slider('distanceKm', 'Khoảng cách Trái Đất - Sao Hỏa (triệu km)', 55000000, 400000000, 5000000,
              function (v) { return Math.round(v / 1e6) + ' triệu km'; })
          ]),

          U.el('div', { class: 'p2-mock-row' }, [
            U.el('span', { class: 'p2-tiny', text: 'Độ trễ một chiều:' }),
            U.el('span', { class: 'p2-num', 'data-role': 'p1-light', text: (state.distanceKm / 299792.458 / 60).toFixed(2) + ' phút' }),
            U.el('span', { class: 'p2-dev-sep' }),
            U.el('label', { class: 'p2-switch p2-switch-inline' }, [
              U.el('input', {
                type: 'checkbox', checked: state.dust ? 'checked' : null,
                onchange: function (e) { state.dust = e.target.checked; }
              }),
              U.el('span', { class: 'p2-switch-track' }, [U.el('span', { class: 'p2-switch-knob' })]),
              U.el('span', { class: 'p2-switch-label', text: 'Bão bụi đang hoạt động' })
            ])
          ]),

          U.el('div', { class: 'p2-actions' }, [
            U.el('button', {
              class: 'p2-btn p2-btn-sm', type: 'button', text: PRESETS.easy.label,
              onclick: function () { applyPreset('easy'); }
            }),
            U.el('button', {
              class: 'p2-btn p2-btn-sm', type: 'button', text: PRESETS.normal.label,
              onclick: function () { applyPreset('normal'); }
            }),
            U.el('button', {
              class: 'p2-btn p2-btn-sm', type: 'button', text: PRESETS.hard.label,
              onclick: function () { applyPreset('hard'); }
            })
          ]),

          U.el('div', { class: 'p2-actions' }, [
            U.el('button', {
              class: 'p2-btn p2-btn-primary', type: 'button', text: 'Gửi SOS về Trái Đất',
              onclick: function () {
                window.Phase2Bridge.simulateSos({
                  astronautSurvivalSols: state.sols,
                  cropHealthPercent: state.crop,
                  dustStormActive: state.dust,
                  earthMarsDistanceKm: state.distanceKm
                });
                switchView('earth');
              }
            }),
            U.el('button', {
              class: 'p2-btn', type: 'button', 'data-role': 'p1-eva',
              text: beaconDone ? 'Đèn hiệu đã cắm' : 'EVA: cắm đèn hiệu và dọn bãi đáp',
              disabled: (!beaconUnlocked || beaconDone) ? 'disabled' : null,
              onclick: function () {
                if (!beaconUnlocked || beaconDone) return;
                beaconDone = true;
                window.Phase2Bridge.simulateBeaconDeployed();
                log('mars:beacon-deployed', '{ cleared: true }');
                render();
              }
            })
          ]),

          U.el('p', { class: 'p2-tiny', 'data-role': 'p1-hint', text: beaconUnlocked
            ? 'DSN đã giao lệnh. Nhiệm vụ EVA đã mở khoá.'
            : 'Nhiệm vụ EVA chỉ mở sau khi Trái Đất gửi lệnh qua DSN (mốc 75% hành trình).' }),

          U.el('h3', { class: 'p2-h3', text: 'Nhật ký sự kiện' }),
          U.el('div', { class: 'p2-log', 'data-role': 'p1-log' })
        ])
      );
      renderLog();
    }

    function applyPreset(key) {
      var p = PRESETS[key];
      state.sols = p.sols;
      state.crop = p.crop;
      state.dust = p.dust;
      state.distanceKm = p.distanceKm;
      render();
    }

    /* ---------- nghe sự kiện từ Giai đoạn 2 ---------- */
    window.addEventListener('earth:dsn-command-sent', function (event) {
      beaconUnlocked = true;
      log('earth:dsn-command-sent', event.detail.commandType + ' · ' + event.detail.lightTimeMinutes + ' phút');
      var btn = root.querySelector('[data-role="p1-eva"]');
      if (btn) { btn.disabled = false; btn.removeAttribute('disabled'); }
      var hint = root.querySelector('[data-role="p1-hint"]');
      if (hint) hint.textContent = 'DSN đã giao lệnh. Nhiệm vụ EVA đã mở khoá.';
      flashMarsTab();
    });

    window.addEventListener('mars:sos-received', function (event) {
      var d = event.detail || {};
      log('mars:sos-received', d.astronautSurvivalSols + ' Sol · bão bụi ' + (d.dustStormActive ? 'có' : 'không') +
        ' · ' + Math.round((d.earthMarsDistanceKm || 0) / 1e6) + ' triệu km');
    });

    function flashMarsTab() {
      var tab = document.querySelector('#view-mars');
      if (!tab) return;
      tab.classList.add('is-pulse');
      window.setTimeout(function () { tab.classList.remove('is-pulse'); }, 2600);
    }

    render();
    return { destroy: function () {} };
  }

  /* ---------- chuyển tab Trái Đất / Sao Hỏa ---------- */
  function switchView(name) {
    document.querySelectorAll('[data-view]').forEach(function (node) {
      node.hidden = node.dataset.view !== name;
    });
    document.querySelectorAll('#view-earth, #view-mars').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.id === 'view-' + name);
    });
  }

  function init() {
    var root = document.querySelector('[data-phase1-mock]');
    if (root) mount(root);

    var earthBtn = document.querySelector('#view-earth');
    var marsBtn = document.querySelector('#view-mars');
    if (earthBtn) earthBtn.addEventListener('click', function () { switchView('earth'); });
    if (marsBtn) marsBtn.addEventListener('click', function () { switchView('mars'); });

    /* Nút "Chuyển sang Tab Sao Hỏa" của Giai đoạn 2 trỏ về đây */
    window.addEventListener('phase2:goto-mars', function () { switchView('mars'); });
  }

  window.Phase1Mock = { mount: mount, switchView: switchView };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
