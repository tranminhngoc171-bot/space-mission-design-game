/**
 * feature-cml3-tradespace.js — Hồi 2 (CML 3).
 *
 * Trách nhiệm: bốn phân khu lựa chọn (Launch / Space / Flight Dynamics / Ground)
 * và bốn đồng hồ biên độ cập nhật tức thì. Không tính toán: đọc
 * full.computed.metrics do engine trả về.
 */
(function () {
  'use strict';
  var U = window.Phase2Util;
  var t = U.t;

  var GROUPS = [
    { field: 'launchVehicleId', catalog: 'launchVehicles', segment: 'cml3.launch' },
    { field: 'trajectoryId', catalog: 'trajectories', segment: 'cml3.flight' },
    { field: 'powerSystemId', catalog: 'powerSystems', segment: 'cml3.space', sub: 'cml3.power' },
    { field: 'edlSystemId', catalog: 'edlSystems', segment: 'cml3.space', sub: 'cml3.edl' },
    { field: 'telecomSystemId', catalog: 'telecomSystems', segment: 'cml3.ground', sub: 'cml3.telecom' }
  ];

  function metaFor(kind, item) {
    if (kind === 'launchVehicles') {
      return item.maxThrowMassKg + ' kg · ' + item.prepDays + ' d · ' + item.costM + ' M$ · ΔV ' + item.deltaVCapacityKmS + ' km/s';
    }
    if (kind === 'trajectories') {
      return item.flightSols + ' Sol · ΔV ' + item.requiredDeltaVKmS + ' km/s · ×' + item.massPenaltyFactor;
    }
    if (kind === 'powerSystems') {
      return item.massKg + ' kg · margin ' + U.pct(item.basePowerMargin) + ' · ' + item.costM + ' M$';
    }
    if (kind === 'edlSystems') {
      return item.massKg + ' kg · max ' + item.maxSupportedPayloadKg + ' kg · ' + item.landingPrecision;
    }
    if (kind === 'telecomSystems') {
      return item.deepSpaceMarginDb + ' dB DS · ' + item.proximityMarginDb + ' dB prox · ' + item.costM + ' M$';
    }
    return '';
  }

  function gauge(label, value, suffix, cls, hint) {
    var pctWidth = U.clamp(typeof value === 'number' && value <= 1 ? value * 100 : value, 0, 100);
    return U.el('div', { class: 'p2-gauge ' + cls }, [
      U.el('div', { class: 'p2-gauge-head' }, [
        U.el('span', { class: 'p2-gauge-label', text: label }),
        U.el('span', { class: 'p2-gauge-value p2-num', text: suffix })
      ]),
      U.el('div', { class: 'p2-gauge-track' }, [
        U.el('div', { class: 'p2-gauge-fill', style: 'width:' + Math.round(pctWidth) + '%' })
      ]),
      hint ? U.el('span', { class: 'p2-gauge-hint', text: hint }) : null
    ]);
  }

  function mount(root, engine) {
    function render(full) {
      var selection = full.state.selection;
      var metrics = full.computed.metrics;
      var mars = full.computed.mars;

      /* --- bốn phân khu --- */
      var columns = GROUPS.map(function (group) {
        var items = full.catalog[group.catalog];
        var cards = Object.keys(items).map(function (id) {
          var item = items[id];
          var pressed = selection[group.field] === id;
          return U.el('button', {
            class: 'p2-card p2-card-sm' + (pressed ? ' is-selected' : ''),
            type: 'button',
            'aria-pressed': String(pressed),
            onclick: function () { engine.updateSelection(group.field, id); }
          }, [
            U.el('span', { class: 'p2-card-title', text: item.name }),
            U.el('span', { class: 'p2-card-meta', text: metaFor(group.catalog, item) }),
            U.el('span', { class: 'p2-card-note', text: item.description })
          ]);
        });
        return U.el('div', { class: 'p2-segment' }, [
          U.el('div', { class: 'p2-segment-head' }, [
            U.el('span', { class: 'p2-segment-name', text: t(group.segment) }),
            group.sub ? U.el('span', { class: 'p2-segment-sub', text: t(group.sub) }) : null
          ]),
          U.el('div', { class: 'p2-card-col' }, cards)
        ]);
      });

      /* --- bốn đồng hồ --- */
      var timeMargin = mars.astronautSurvivalSols - metrics.totalMissionSols;
      var timeRatio = U.clamp(timeMargin / Math.max(mars.astronautSurvivalSols, 1), -1, 1);
      var timeClass = timeMargin >= 10 ? 'is-green' : (timeMargin >= 0 ? 'is-yellow' : 'is-red');

      var powerConflict = selection.powerSystemId === 'SOLAR_ARRAY' && mars.dustStormActive;
      var powerClass = U.marginClass(metrics.effectivePowerMargin) + (powerConflict ? ' is-flash' : '');

      var telecomOk = metrics.deepSpaceMarginDb >= full.standards.MIN_DEEP_SPACE_DB &&
        metrics.proximityMarginDb >= full.standards.MIN_PROXIMITY_DB;

      var gauges = U.el('div', { class: 'p2-gauges' }, [
        U.el('h3', { class: 'p2-h3', text: t('cml3.gauges') }),
        gauge(t('cml3.gaugeTime'), U.clamp(Math.abs(timeRatio) * 100, 0, 100),
          U.signed(timeMargin, ' Sol'), timeClass, t('cml3.need35')),
        gauge(t('cml3.gaugeMass'), metrics.dryMassMargin, U.pct(metrics.dryMassMargin),
          U.marginClass(metrics.dryMassMargin), t('cml3.need35')),
        gauge(t('cml3.gaugePower'), metrics.effectivePowerMargin, U.pct(metrics.effectivePowerMargin),
          powerClass, t('cml3.need35')),
        gauge(t('cml3.gaugeTelecom'),
          U.clamp(metrics.proximityMarginDb / 6 * 100, 0, 100),
          metrics.deepSpaceMarginDb + ' / ' + metrics.proximityMarginDb + ' dB',
          telecomOk ? 'is-green' : 'is-red', t('cml3.needDb'))
      ]);

      U.clear(root).appendChild(
        U.el('section', { class: 'p2-panel' }, [
          U.el('div', { class: 'p2-panel-head' }, [
            U.el('h2', { class: 'p2-h2', text: t('cml3.heading') }),
            U.el('span', { class: 'p2-badge', text: 'CML 3' })
          ]),
          powerConflict ? U.el('p', { class: 'p2-warn', text: t('cml3.conflict') }) : null,
          U.el('div', { class: 'p2-segments' }, columns),
          gauges,
          U.el('div', { class: 'p2-footrow' }, [
            U.el('span', { class: 'p2-num', text: t('cml3.deltaV') + ': ' + (metrics.deltaVFeasible ? 'OK' : 'FAIL') }),
            U.el('span', { class: 'p2-num', text: t('cml3.cost') + ': ' + metrics.totalCostM + ' M$' })
          ]),
          U.el('div', { class: 'p2-actions' }, [
            U.el('button', {
              class: 'p2-btn', type: 'button', text: t('app.step1'),
              onclick: function () { engine.setCmlStep(1); }
            }),
            U.el('button', {
              class: 'p2-btn p2-btn-primary', type: 'button', text: t('cml3.next'),
              onclick: function () { engine.setCmlStep(3); }
            })
          ])
        ])
      );
    }

    var unsubscribe = engine.subscribe('state:changed', render);
    render(engine.getFullState());
    return { destroy: unsubscribe };
  }

  window.Phase2Features = window.Phase2Features || {};
  window.Phase2Features.cml3TradeSpace = mount;
})();
