/**
 * ============================================================================
 * MARS RESCUE: MISSION DESIGN LAB (PHASE 2 ENGINE)
 * ============================================================================
 * Pure headless simulation engine grounded in NASA JPL Concept Maturity Levels
 * (CML 1-4), NASA GSFC Mission Design Lab (MDL) disciplines, and NASA's 4
 * Science Mission Segments (Launch, Space, Ground, User).
 *
 * ZERO DOM DEPENDENCIES: Communicate with UI strictly via `subscribe()` /
 * `emit()` events and public action methods so UI/CSS can be swapped anytime.
 * ============================================================================
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.RescueMissionEngine = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // --------------------------------------------------------------------------
  // 1. NASA REFERENCE CONSTANTS & COMPONENT CATALOG (MDL / CML 1-4)
  // --------------------------------------------------------------------------
  const NASA_STANDARDS = Object.freeze({
    MIN_DRY_MASS_MARGIN: 0.35,      // CML 4 Checklist: S/C Dry Mass Margin >= 35%
    MIN_POWER_MARGIN: 0.35,         // CML 4 Checklist: Power & Energy Margin >= 35%
    MIN_DEEP_SPACE_DB: 3.0,         // CML 4 Checklist: Telecom >= 3 dB (deep space)
    MIN_PROXIMITY_DB: 6.0,          // CML 4 Checklist: Telecom >= 6 dB (proximity links)
    MIN_CML4_GREEN_RATIO: 0.80,     // JPL Rule: >= 80% Green items to pass Life Cycle Gate
    LIGHT_SPEED_KM_S: 299792.458    // Exact speed of light (km/s)
  });

  const CATALOG = Object.freeze({
    objectives: {
      RESUPPLY_BIONUTRIENTS: {
        id: 'RESUPPLY_BIONUTRIENTS',
        name: 'Gói Tiếp Tế Sinh Học & ECLSS (BioNutrients + Spare Parts)',
        segment: 'User / Science Objective',
        payloadMassKg: 420,
        survivalExtensionSols: 320,
        precisionRequired: 'STANDARD',
        nasaReference: 'NASA BioNutrients-2 & ISS ECLSS (Khắc phục suy giảm vi chất & thay lõi lọc CO2)',
        description: 'Nhẹ, dễ hạ cánh. Bù đắp vitamin, chất béo và linh kiện lọc khí để kéo dài sự sống thêm 320 Sol.'
      },
      MAV_ASCENT_RESCUE: {
        id: 'MAV_ASCENT_RESCUE',
        name: 'Mô-đun Nhiên Liệu & Cất Cánh Khẩn Cấp (MAV Ascent Kit)',
        segment: 'User / Exploration Objective',
        payloadMassKg: 1150,
        survivalExtensionSols: 999,
        precisionRequired: 'HIGH',
        nasaReference: 'Mars Sample Retrieval Lander / MAV Architecture',
        description: 'Nặng, đòi hỏi hạ cánh chính xác cao. Cung cấp nhiên liệu & linh kiện để phi hành gia bay lên quỹ đạo.'
      }
    },

    launchVehicles: {
      MEDIUM_LV: {
        id: 'MEDIUM_LV',
        name: 'Tên Lửa Đẩy Hạng Trung (Commercial Heavy-Medium)',
        segment: 'Launch Segment',
        prepDays: 15,
        maxThrowMassKg: 1450,
        deltaVCapacityKmS: 4.1,
        costM: 180,
        reliability: 0.94,
        description: 'Chuẩn bị phóng nhanh (15 ngày), chi phí thấp nhưng giới hạn tải trọng tới Sao Hỏa.'
      },
      SLS_HEAVY: {
        id: 'SLS_HEAVY',
        name: 'Tên Lửa Siêu Nặng SLS (Space Launch System)',
        segment: 'Launch Segment',
        prepDays: 42,
        maxThrowMassKg: 3200,
        deltaVCapacityKmS: 6.2,
        costM: 650,
        reliability: 0.97,
        description: 'Sức đẩy cực lớn, tăng biên độ khối lượng và rút ngắn thời gian bay, nhưng mất 42 ngày lắp ráp.'
      }
    },

    trajectories: {
      HOHMANN_MIN_ENERGY: {
        id: 'HOHMANN_MIN_ENERGY',
        name: 'Quỹ Đạo Chuyển Tiếp Hohmann (Minimum-Energy Transfer)',
        segment: 'Flight Dynamics',
        flightSols: 235,
        requiredDeltaVKmS: 3.6,
        massPenaltyFactor: 1.0,
        description: 'Tiết kiệm nhiên liệu tối đa, chở được nhiều hàng nhưng thời gian bay dài (~235 Sol).'
      },
      FAST_CONJUNCTION_ASSIST: {
        id: 'FAST_CONJUNCTION_ASSIST',
        name: 'Quỹ Đạo Năng Lượng Cao (Fast Transit / Gravity Assist)',
        segment: 'Flight Dynamics',
        flightSols: 155,
        requiredDeltaVKmS: 5.1,
        massPenaltyFactor: 1.38,
        description: 'Rút ngắn thời gian bay xuống 155 Sol nhưng tiêu tốn Delta-V lớn, giảm sức chở hàng hóa.'
      }
    },

    powerSystems: {
      SOLAR_ARRAY: {
        id: 'SOLAR_ARRAY',
        name: 'Pin Mặt Trời Hiệu Suất Cao (UltraFlex Solar Array)',
        segment: 'Space Segment (Power)',
        massKg: 95,
        basePowerMargin: 0.48,
        dustStormPenalty: 0.30, // Drops margin to 0.18 (< 0.35!) during dust storm
        isNuclear: false,
        costM: 45,
        description: 'Nhẹ, không cần cấp phép hạt nhân, nhưng suy giảm công suất nghiêm trọng khi có bão bụi.'
      },
      RTG_PLUTONIUM: {
        id: 'RTG_PLUTONIUM',
        name: 'Nguồn Nhiệt Điện Đồng Vị Phóng Xạ (MMRTG - Plutonium-238)',
        segment: 'Space Segment (Power & Thermal)',
        massKg: 190,
        basePowerMargin: 0.52,
        dustStormPenalty: 0.0,
        isNuclear: true,
        costM: 140,
        description: 'Cung cấp điện & nhiệt liên tục bất chấp bão bụi, nhưng bắt buộc xin giấy phép hạt nhân (Launch Approval).'
      }
    },

    edlSystems: {
      AIRBAG_CHUTE: {
        id: 'AIRBAG_CHUTE',
        name: 'Dù Siêu Thanh + Túi Khí (Supersonic Parachute & Airbags)',
        segment: 'Space Segment (Mechanical / EDL)',
        massKg: 180,
        maxSupportedPayloadKg: 600,
        landingPrecision: 'STANDARD',
        costM: 70,
        description: 'Phù hợp tải nhẹ (như Mars Pathfinder). Không chịu được tải nặng hoặc yêu cầu hạ cánh điểm.'
      },
      RETRO_SKYCRANE: {
        id: 'RETRO_SKYCRANE',
        name: 'Khiên Nhiệt + Động Cơ Hãm Phản Lực (Guided Retro-Propulsion)',
        segment: 'Space Segment (Propulsion / EDL)',
        massKg: 410,
        maxSupportedPayloadKg: 1600,
        landingPrecision: 'HIGH',
        costM: 210,
        description: 'Bắt buộc cho tải nặng trong khí quyển loãng (0.6% Trái Đất) của Sao Hỏa (như Curiosity/Perseverance).'
      }
    },

    telecomSystems: {
      X_BAND_STD: {
        id: 'X_BAND_STD',
        name: 'Hệ Thống X-Band Tiêu Chuẩn (Direct-to-Earth Only)',
        segment: 'Ground & Space Telecom',
        massKg: 45,
        deepSpaceMarginDb: 3.4,
        proximityMarginDb: 4.2, // Fails >= 6.0 dB requirement for surface beacon lock!
        costM: 40,
        description: 'Đủ liên lạc không gian sâu (>=3 dB) nhưng yếu ở cự ly gần (<6 dB) khi dẫn đường hạ cánh.'
      },
      KA_BAND_UHF_RELAY: {
        id: 'KA_BAND_UHF_RELAY',
        name: 'Tổ Hợp Ka-Band + UHF Proximity Transceiver',
        segment: 'Ground & Space Telecom',
        massKg: 85,
        deepSpaceMarginDb: 5.1,
        proximityMarginDb: 7.8, // Passes >= 6.0 dB requirement
        costM: 95,
        description: 'Đạt chuẩn DSN không gian sâu và khóa tín hiệu tầm gần (>=6 dB) với đèn hiệu của phi hành gia.'
      }
    }
  });

  // --------------------------------------------------------------------------
  // 2. EVENT BUS (DECOUPLED OBSERVER PATTERN FOR UI)
  // --------------------------------------------------------------------------
  class EventBus {
    constructor() {
      this.listeners = {};
    }
    on(event, fn) {
      if (!this.listeners[event]) this.listeners[event] = [];
      this.listeners[event].push(fn);
      return () => this.off(event, fn);
    }
    off(event, fn) {
      if (!this.listeners[event]) return;
      this.listeners[event] = this.listeners[event].filter(cb => cb !== fn);
    }
    emit(event, payload) {
      if (!this.listeners[event]) return;
      this.listeners[event].forEach(cb => cb(payload));
    }
  }

  // --------------------------------------------------------------------------
  // 3. FEATURE MODULE A: PHASE 1 <-> PHASE 2 TELEMETRY & DSN COMMS BRIDGE
  // --------------------------------------------------------------------------
  class TelemetryBridge {
    constructor(bus) {
      this.bus = bus;
      this.marsState = {
        signalReceived: false,
        astronautSurvivalSols: 250,
        cropHealthPercent: 75,
        dustStormActive: true,
        earthMarsDistanceKm: 215000000, // ~215M km (~11.95 light-minutes)
        landingBeaconReady: false,
        landingSiteCleared: false
      };
      this.messageQueue = [];
    }

    ingestFromPhase1(phase1Data) {
      this.marsState = Object.assign({}, this.marsState, phase1Data, {
        signalReceived: true
      });
      this.bus.emit('mars:telemetryUpdated', this.getSnapshot());
    }

    getOneWayLightTimeMinutes() {
      const seconds = this.marsState.earthMarsDistanceKm / NASA_STANDARDS.LIGHT_SPEED_KM_S;
      return Number((seconds / 60).toFixed(2));
    }

    sendCommandToMars(commandType, simulatedDelayMs = 2500) {
      const msg = {
        id: 'DSN-' + Date.now(),
        commandType,
        lightTimeMinutes: this.getOneWayLightTimeMinutes(),
        status: 'IN_TRANSIT',
        sentAt: Date.now()
      };
      this.messageQueue.push(msg);
      this.bus.emit('dsn:messageQueued', msg);

      setTimeout(() => {
        msg.status = 'DELIVERED';
        this.bus.emit('dsn:messageDelivered', msg);
      }, simulatedDelayMs);

      return msg;
    }

    updateMarsFieldStatus(updates) {
      this.marsState = Object.assign({}, this.marsState, updates);
      this.bus.emit('mars:telemetryUpdated', this.getSnapshot());
    }

    getSnapshot() {
      return Object.assign({}, this.marsState, {
        oneWayLightTimeMin: this.getOneWayLightTimeMinutes()
      });
    }
  }

  // --------------------------------------------------------------------------
  // 4. FEATURE MODULE B: MDL TRADE SPACE & PHYSICS CALCULATOR (CML 2-3)
  // --------------------------------------------------------------------------
  class TradeSpaceEngine {
    static evaluate(selection, marsTelemetry) {
      const obj = CATALOG.objectives[selection.objectiveId];
      const lv = CATALOG.launchVehicles[selection.launchVehicleId];
      const traj = CATALOG.trajectories[selection.trajectoryId];
      const pwr = CATALOG.powerSystems[selection.powerSystemId];
      const edl = CATALOG.edlSystems[selection.edlSystemId];
      const tel = CATALOG.telecomSystems[selection.telecomSystemId];

      // 1. Timeline vs Survival KPP
      const totalMissionSols = lv.prepDays + traj.flightSols;
      const survivalMarginSols = marsTelemetry.astronautSurvivalSols - totalMissionSols;

      // 2. Mass & S/C Dry Mass Margin (>= 35% required by JPL CML 4)
      const spacecraftDryMassKg = pwr.massKg + edl.massKg + tel.massKg + 220; // 220kg bus/avionics/thermal
      const totalInjectedMassKg = (spacecraftDryMassKg + obj.payloadMassKg) * traj.massPenaltyFactor;
      const remainingMassCapacityKg = lv.maxThrowMassKg - totalInjectedMassKg;
      const dryMassMargin = Number((remainingMassCapacityKg / lv.maxThrowMassKg).toFixed(3));

      // 3. Delta-V check
      const deltaVFeasible = lv.deltaVCapacityKmS >= traj.requiredDeltaVKmS;

      // 4. Power & Energy Margin (>= 35% required by CML 4)
      const effectivePowerMargin = Number(
        (pwr.basePowerMargin - (marsTelemetry.dustStormActive ? pwr.dustStormPenalty : 0)).toFixed(3)
      );

      // 5. Telecom Margins (>= 3 dB Deep Space, >= 6 dB Proximity)
      const deepSpaceMarginDb = tel.deepSpaceMarginDb;
      const proximityMarginDb = tel.proximityMarginDb;

      // 6. EDL Compatibility
      const edlMassOk = obj.payloadMassKg <= edl.maxSupportedPayloadKg;
      const edlPrecisionOk = obj.precisionRequired === 'STANDARD' || edl.landingPrecision === 'HIGH';

      // 7. Programmatic Cost & Risk
      const totalCostM = lv.costM + pwr.costM + edl.costM + tel.costM + 120; // +120M MOS/GDS ops

      return {
        totalMissionSols,
        survivalMarginSols,
        spacecraftDryMassKg,
        totalInjectedMassKg: Math.round(totalInjectedMassKg),
        dryMassMargin,
        deltaVFeasible,
        effectivePowerMargin,
        deepSpaceMarginDb,
        proximityMarginDb,
        edlMassOk,
        edlPrecisionOk,
        totalCostM,
        requiresNuclearApproval: pwr.isNuclear
      };
    }
  }

  // --------------------------------------------------------------------------
  // 5. FEATURE MODULE C: NASA CML 4 CHECKLIST & RYG GATE VALIDATOR
  // --------------------------------------------------------------------------
  class CML4Validator {
    /**
     * Evaluates architecture against JPL CML 4 Checklist (Red / Yellow / Green)
     * Returns detailed educational diagnostics for every discipline.
     */
    static audit(selection, metrics, complianceFlags) {
      const items = [];

      // SCIENCE / KPP
      items.push({
        id: 'KPP_TIMELINE',
        category: 'SCIENCE & KPP',
        label: 'Thời gian giải cứu <= Giới hạn sinh tồn của phi hành gia',
        status: metrics.survivalMarginSols >= 10 ? 'G' : (metrics.survivalMarginSols >= 0 ? 'Y' : 'R'),
        detail: metrics.survivalMarginSols >= 0
          ? `Tàu tới nơi trước hạn ${metrics.survivalMarginSols} Sol.`
          : `Thất bại KPP: Tàu tới trễ ${Math.abs(metrics.survivalMarginSols)} Sol so với lượng calo/oxy từ vườn cây.`
      });

      // TECHNICAL: Flight Dynamics & Delta-V
      items.push({
        id: 'DELTA_V_BUDGET',
        category: 'TECHNICAL (Flight Dynamics)',
        label: 'Ngân sách Delta-V & Năng lượng phóng tên lửa',
        status: metrics.deltaVFeasible ? 'G' : 'R',
        detail: metrics.deltaVFeasible
          ? 'Tên lửa đẩy đủ Delta-V để đưa tàu vào quỹ đạo chuyển tiếp liên hành tinh.'
          : 'Lỗi quỹ đạo: Tên lửa hạng trung không đủ Delta-V cho quỹ đạo bay nhanh. Hãy đổi sang SLS hoặc quỹ đạo Hohmann.'
      });

      // TECHNICAL: S/C Dry Mass Margin >= 35%
      items.push({
        id: 'DRY_MASS_MARGIN',
        category: 'TECHNICAL (Margins)',
        label: 'Biên độ dự phòng khối lượng khô (S/C Dry Mass Margin >= 35%)',
        status: metrics.dryMassMargin >= NASA_STANDARDS.MIN_DRY_MASS_MARGIN ? 'G' : (metrics.dryMassMargin >= 0.20 ? 'Y' : 'R'),
        detail: `Biên độ hiện tại: ${(metrics.dryMassMargin * 100).toFixed(1)}% (Chuẩn JPL CML 4 yêu cầu >= 35%).`
      });

      // TECHNICAL: Power & Energy Margin >= 35%
      items.push({
        id: 'POWER_MARGIN',
        category: 'TECHNICAL (Power & Thermal)',
        label: 'Biên độ năng lượng & sưởi ấm (Power Margin >= 35%)',
        status: metrics.effectivePowerMargin >= NASA_STANDARDS.MIN_POWER_MARGIN ? 'G' : 'R',
        detail: metrics.effectivePowerMargin >= NASA_STANDARDS.MIN_POWER_MARGIN
          ? `Biên độ năng lượng đạt ${(metrics.effectivePowerMargin * 100).toFixed(0)}%.`
          : 'Cảnh báo MDL Power: Bão bụi làm hiệu suất Pin Mặt Trời tụt dưới 35%. Hãy đổi sang nguồn hạt nhân RTG!'
      });

      // TECHNICAL: Telecom Margins (>= 3 dB Deep Space, >= 6 dB Proximity)
      const telecomOk = metrics.deepSpaceMarginDb >= NASA_STANDARDS.MIN_DEEP_SPACE_DB &&
                        metrics.proximityMarginDb >= NASA_STANDARDS.MIN_PROXIMITY_DB;
      items.push({
        id: 'TELECOM_MARGIN',
        category: 'TECHNICAL (Communications)',
        label: 'Biên độ viễn thông (>= 3 dB Deep Space; >= 6 dB Proximity)',
        status: telecomOk ? 'G' : 'R',
        detail: telecomOk
          ? `Deep Space: ${metrics.deepSpaceMarginDb} dB | Proximity Link: ${metrics.proximityMarginDb} dB (Đạt chuẩn).`
          : `Proximity Link chỉ đạt ${metrics.proximityMarginDb} dB (< 6 dB). Không thể khóa đèn hiệu hạ cánh trên mặt đất!`
      });

      // TECHNICAL: Mechanical / EDL Compatibility
      items.push({
        id: 'EDL_ARCHITECTURE',
        category: 'TECHNICAL (Mechanical / EDL)',
        label: 'Tương thích hệ thống hạ cánh khí quyển loãng Sao Hỏa (0.6% Trái Đất)',
        status: (metrics.edlMassOk && metrics.edlPrecisionOk) ? 'G' : 'R',
        detail: (metrics.edlMassOk && metrics.edlPrecisionOk)
          ? 'Cấu hình EDL chịu được tải trọng và đáp ứng độ chính xác bãi đáp.'
          : 'Lỗi EDL: Túi khí/Dù không đủ sức hãm tải trọng lớn hoặc thiếu độ chính xác. Hãy dùng Động cơ hãm phản lực.'
      });

      // TECHNICAL: Planetary Protection
      items.push({
        id: 'PLANETARY_PROTECTION',
        category: 'TECHNICAL (Planetary Protection)',
        label: 'Khử trùng sinh học tàu vũ trụ (Planetary Protection Compliance)',
        status: complianceFlags.planetaryProtectionSterilized ? 'G' : 'R',
        detail: complianceFlags.planetaryProtectionSterilized
          ? 'Đã khử trùng cấp độ IVb, ngăn ngừa nhiễm khuẩn chéo lên Sao Hỏa.'
          : 'Chưa xác nhận quy trình Planetary Protection theo chuẩn NASA.'
      });

      // OTHER: Launch Approval (Nuclear Safety if RTG selected)
      items.push({
        id: 'LAUNCH_APPROVAL',
        category: 'OTHER (Launch Approval)',
        label: 'Phê duyệt an toàn phóng (Nuclear / Public Safety Approval)',
        status: !metrics.requiresNuclearApproval
          ? 'G'
          : (complianceFlags.launchApprovalSubmitted ? 'G' : 'R'),
        detail: !metrics.requiresNuclearApproval
          ? 'Không sử dụng vật liệu phóng xạ, tự động đạt chuẩn.'
          : (complianceFlags.launchApprovalSubmitted
            ? 'Đã nộp hồ sơ phê duyệt an toàn hạt nhân cho nguồn RTG.'
            : 'Bắt buộc tick xác nhận Launch Approval vì tàu sử dụng Plutonium-238 (RTG).')
      });

      const greenCount = items.filter(i => i.status === 'G').length;
      const redCount = items.filter(i => i.status === 'R').length;
      const greenRatio = Number((greenCount / items.length).toFixed(2));
      const canLaunch = redCount === 0 && greenRatio >= NASA_STANDARDS.MIN_CML4_GREEN_RATIO;

      return {
        items,
        greenCount,
        totalCount: items.length,
        greenRatio,
        canLaunch,
        nasaAnalogue: CML4Validator.findNasaAnalogue(selection)
      };
    }

    static findNasaAnalogue(selection) {
      if (selection.edlSystemId === 'RETRO_SKYCRANE' && selection.powerSystemId === 'RTG_PLUTONIUM') {
        return 'Mars Science Laboratory (Curiosity) & Perseverance / Mars Sample Retrieval Lander';
      }
      if (selection.edlSystemId === 'AIRBAG_CHUTE' && selection.powerSystemId === 'SOLAR_ARRAY') {
        return 'Mars Pathfinder (Sojourner) & Mars Exploration Rovers (Spirit / Opportunity)';
      }
      return 'NASA Custom Planetary Discovery-Class Architecture';
    }
  }

  // --------------------------------------------------------------------------
  // 6. MAIN CONTROLLER: PHASE 2 MISSION DESIGN LAB ENGINE
  // --------------------------------------------------------------------------
  class Phase2MissionEngine {
    constructor() {
      this.bus = new EventBus();
      this.bridge = new TelemetryBridge(this.bus);

      this.state = {
        currentCmlStep: 1, // 1: Objective/KPP, 2: Trade Space (CML 3), 3: Point Design Audit (CML 4), 4: Execution
        selection: {
          objectiveId: 'RESUPPLY_BIONUTRIENTS',
          launchVehicleId: 'MEDIUM_LV',
          trajectoryId: 'HOHMANN_MIN_ENERGY',
          powerSystemId: 'SOLAR_ARRAY',
          edlSystemId: 'AIRBAG_CHUTE',
          telecomSystemId: 'X_BAND_STD'
        },
        compliance: {
          planetaryProtectionSterilized: false,
          launchApprovalSubmitted: false
        },
        execution: {
          status: 'DESIGNING', // DESIGNING | LAUNCHED | PROXIMITY_WAIT | COMPLETED | FAILED
          progressPercent: 0,
          outcomeReason: ''
        }
      };

      this.recalculate();
    }

    // --- Public API for UI / Phase 1 Integration ---
    subscribe(event, callback) {
      return this.bus.on(event, callback);
    }

    initFromPhase1(phase1Summary) {
      this.bridge.ingestFromPhase1(phase1Summary);
      this.recalculate();
    }

    setCmlStep(stepNumber) {
      this.state.currentCmlStep = Math.max(1, Math.min(4, stepNumber));
      this.emitState();
    }

    updateSelection(key, value) {
      if (Object.prototype.hasOwnProperty.call(this.state.selection, key)) {
        this.state.selection[key] = value;
        this.recalculate();
      }
    }

    updateCompliance(key, boolVal) {
      if (Object.prototype.hasOwnProperty.call(this.state.compliance, key)) {
        this.state.compliance[key] = Boolean(boolVal);
        this.recalculate();
      }
    }

    recalculate() {
      const marsSnapshot = this.bridge.getSnapshot();
      const metrics = TradeSpaceEngine.evaluate(this.state.selection, marsSnapshot);
      const checklist = CML4Validator.audit(this.state.selection, metrics, this.state.compliance);

      this.computed = {
        mars: marsSnapshot,
        metrics,
        checklist
      };
      this.emitState();
      return this.computed;
    }

    launchMission() {
      const { checklist, metrics } = this.computed;
      if (!checklist.canLaunch) {
        this.bus.emit('mission:launchBlocked', checklist);
        return false;
      }

      this.state.currentCmlStep = 4;
      this.state.execution.status = 'LAUNCHED';
      this.state.execution.progressPercent = 10;
      this.emitState();

      // Send DSN Proximity Link instruction to Mars astronaut
      this.bridge.sendCommandToMars('DEPLOY_LANDING_BEACON_AND_CLEAR_ZONE', 2000);

      // Simulate transit to Mars
      setTimeout(() => {
        this.state.execution.progressPercent = 75;
        this.state.execution.status = 'PROXIMITY_WAIT';
        this.emitState();
      }, 2500);

      return true;
    }

    completeMarsGroundPrep() {
      this.bridge.updateMarsFieldStatus({
        landingBeaconReady: true,
        landingSiteCleared: true
      });
      if (this.state.execution.status === 'PROXIMITY_WAIT') {
        this.finalizeLanding();
      }
    }

    finalizeLanding() {
      const mars = this.bridge.getSnapshot();
      if (mars.landingBeaconReady && mars.landingSiteCleared) {
        this.state.execution.progressPercent = 100;
        this.state.execution.status = 'COMPLETED';
        this.state.execution.outcomeReason =
          `Giải cứu thành công! Tàu đáp an toàn với biên độ viễn thông ${this.computed.metrics.proximityMarginDb} dB. ` +
          `Kiến trúc tương đồng: ${this.computed.checklist.nasaAnalogue}.`;
      } else {
        this.state.execution.status = 'FAILED';
        this.state.execution.outcomeReason =
          'Thất bại khi hạ cánh (EDL): Phi hành gia trên Sao Hỏa chưa đặt đèn hiệu dẫn đường Proximity Link!';
      }
      this.emitState();
    }

    getFullState() {
      return {
        catalog: CATALOG,
        standards: NASA_STANDARDS,
        state: JSON.parse(JSON.stringify(this.state)),
        computed: this.computed
      };
    }

    emitState() {
      this.bus.emit('state:changed', this.getFullState());
    }
  }

  return {
    NASA_STANDARDS,
    CATALOG,
    Phase2MissionEngine
  };
}));
