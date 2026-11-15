/**
 * feature-cml1-telemetry.js — Hồi 1 (CML 1-2).
 *
 * Trách nhiệm: hiển thị telemetry Sao Hỏa (sinh tồn, độ trễ ánh sáng, bão bụi),
 * thanh so sánh thời gian sứ mệnh với giới hạn sinh tồn, và chọn mục tiêu KPP.
 * Không tính toán vật lý: mọi số lấy từ engine.
 */
(function () {
  'use strict';
  var U = window.Phase2Util;
  var t = U.t;

  function mount(root, engine) {
    function renderStandby() {
      U.clear(root).appendChild(
        U.el('section', { class: 'p2-panel p2-panel-locked' }, [
          U.el('div', { class: 'p2-panel-head' }, [
            U.el('h2', { class: 'p2-h2', text: t('cml1.standbyTitle') }),
            U.el('span', { class: 'p2-badge is-locked', text: t('app.signalWait') })
          ]),
          U.el('p', { class: 'p2-muted', text: t('cml1.standbyBody') }),
          U.el('div', { class: 'p2-scan' }, [
            U.el('span', { class: 'p2-scan-bar' })
          ])
        ])
      );
    }

    function badge(text, cls) {
      return U.el('span', { class: 'p2-badge ' + (cls || ''), text: text });
    }

    function render(full) {
      var mars = full.computed.mars;
      var metrics = full.computed.metrics;
      var selection = full.state.selection;
      if (!mars.signalReceived) { renderStandby(); return; }

      var margin = metrics.survivalMarginSols;
      var timeClass = margin >= 10 ? 'is-green' : (margin >= 0 ? 'is-yellow' : 'is-red');
      var ratio = U.clamp(metrics.totalMissionSols / Math.max(mars.astronautSurvivalSols, 1), 0, 1);

      var tel = U.el('div', { class: 'p2-telgrid' }, [
        cell(t('cml1.survival'), mars.astronautSurvivalSols + ' ' + t('app.sol'), ''),
        cell(t('app.lightTime'), mars.oneWayLightTimeMin + ' ' + t('app.minutes'), ''),
        cell(t('cml1.crop'), mars.cropHealthPercent + '%', ''),
        cell(t('cml1.dust'), mars.dustStormActive ? t('cml1.dustActive') : t('cml1.dustClear'),
          mars.dustStormActive ? 'is-red' : 'is-green')
      ]);

      var bar = U.el('div', { class: 'p2-bar-block ' + timeClass }, [
        U.el('div', { class: 'p2-bar-head' }, [
          U.el('span', { text: t('cml1.budgetBar') }),
          U.el('span', { class: 'p2-num', text: metrics.totalMissionSols + ' / ' + mars.astronautSurvivalSols + ' ' + t('app.sol') })
        ]),
        U.el('div', { class: 'p2-bar-track' }, [
          U.el('div', { class: 'p2-bar-fill', style: 'width:' + Math.round(ratio * 100) + '%' })
        ]),
        U.el('div', { class: 'p2-bar-legend' }, [
          U.el('span', { text: t('cml1.missionTime') + ': ' + metrics.totalMissionSols + ' ' + t('app.sol') }),
          U.el('span', { class: 'p2-num', text: margin >= 0
            ? t('cml1.marginOk', { n: margin })
            : t('cml1.marginLate', { n: Math.abs(margin) }) })
        ])
      ]);

      var objectives = Object.keys(full.catalog.objectives).map(function (id) {
        var obj = full.catalog.objectives[id];
        var pressed = selection.objectiveId === id;
        return U.el('button', {
          class: 'p2-card' + (pressed ? ' is-selected' : ''),
          type: 'button',
          'aria-pressed': String(pressed),
          onclick: function () { engine.updateSelection('objectiveId', id); }
        }, [
          U.el('span', { class: 'p2-card-title', text: obj.name }),
          U.el('span', { class: 'p2-card-meta' }, [
            t('cml1.payload') + ': ' + obj.payloadMassKg + ' kg · ' +
            t('cml1.extension') + ': ' + (obj.survivalExtensionSols >= 999 ? '∞' : obj.survivalExtensionSols + ' ' + t('app.sol')) +
            ' · ' + t('cml1.precision') + ': ' + obj.precisionRequired
          ]),
          U.el('span', { class: 'p2-card-note', text: obj.description }),
          U.el('span', { class: 'p2-card-ref', text: obj.nasaReference })
        ]);
      });

      U.clear(root).appendChild(
        U.el('section', { class: 'p2-panel' }, [
          U.el('div', { class: 'p2-panel-head' }, [
            U.el('h2', { class: 'p2-h2', text: t('cml1.heading') }),
            badge(t('app.signalLocked'), 'is-green')
          ]),
          tel,
          bar,
          U.el('h3', { class: 'p2-h3', text: t('cml1.objectiveHeading') }),
          U.el('div', { class: 'p2-card-row' }, objectives),
          U.el('div', { class: 'p2-actions' }, [
            U.el('button', {
              class: 'p2-btn p2-btn-primary', type: 'button', text: t('cml1.next'),
              onclick: function () { engine.setCmlStep(2); }
            })
          ])
        ])
      );
    }

    function cell(label, value, cls) {
      return U.el('div', { class: 'p2-cell ' + (cls || '') }, [
        U.el('span', { class: 'p2-cell-key', text: label }),
        U.el('span', { class: 'p2-cell-val p2-num', text: value })
      ]);
    }

    var unsubscribe = engine.subscribe('state:changed', render);
    render(engine.getFullState());
    return { destroy: unsubscribe };
  }

  window.Phase2Features = window.Phase2Features || {};
  window.Phase2Features.cml1Telemetry = mount;
})();
