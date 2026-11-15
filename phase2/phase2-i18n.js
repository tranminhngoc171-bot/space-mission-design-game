/**
 * phase2-i18n.js — chuỗi hiển thị của Giai đoạn 2, song ngữ VI/EN.
 *
 * Luật repo (docs/14 §4): mọi chuỗi người chơi đọc phải có cả hai bên, thiếu một
 * bên là lỗi. File này giữ toàn bộ chuỗi của phase2/ để không phải sửa
 * src/i18n.js của Giai đoạn 1 (vùng dùng chung, chỉ thêm key có tiền tố riêng).
 *
 * Dùng: Phase2I18N.t('cml1.standbyTitle')
 * Đổi ngôn ngữ: Phase2I18N.setLang('en') rồi phát 'phase2:lang-changed'.
 */
(function () {
  'use strict';

  var STRINGS = {
    vi: {
      'app.title': 'PHÒNG ĐIỀU KHIỂN SỨ MỆNH TRÁI ĐẤT',
      'app.subtitle': 'NASA MISSION DESIGN LAB · CML 1-4',
      'app.signalWait': 'CHỜ TÍN HIỆU',
      'app.signalLocked': 'ĐÃ KHÓA SÓNG DSN',
      'app.sol': 'Sol',
      'app.lightTime': 'Độ trễ một chiều',
      'app.minutes': 'phút',
      'app.devPanel': 'Bảng thử nghiệm',
      'app.simSos': 'Giả lập: nhận SOS từ Sao Hỏa',
      'app.simBeacon': 'Giả lập: đèn hiệu đã cắm',
      'app.step1': 'Hồi 1',
      'app.step2': 'Hồi 2',
      'app.step3': 'Hồi 3',
      'app.step4': 'Hồi 4-5',
      'app.reset': 'Chạy lại từ đầu',

      'cml1.standbyTitle': 'ĐANG CHỜ TÍN HIỆU CẦU CỨU',
      'cml1.standbyBody': 'Mạng lưới không gian sâu đang quét. Giao diện sẽ tự mở khóa khi nhận sự kiện mars:sos-received từ Giai đoạn 1.',
      'cml1.heading': 'Hồi 1 · CML 1-2 · Chốt mục tiêu và tham số sống còn',
      'cml1.survival': 'Phi hành gia còn sống',
      'cml1.crop': 'Sức khỏe vườn cây',
      'cml1.dust': 'Bão bụi',
      'cml1.dustActive': 'ĐANG HOẠT ĐỘNG',
      'cml1.dustClear': 'TRỜI TRONG',
      'cml1.budgetBar': 'Tổng thời gian sứ mệnh so với giới hạn sinh tồn',
      'cml1.missionTime': 'Sứ mệnh',
      'cml1.survivalLimit': 'Giới hạn',
      'cml1.marginOk': 'Tàu tới trước hạn {n} Sol',
      'cml1.marginLate': 'Tàu tới trễ {n} Sol',
      'cml1.objectiveHeading': 'Chọn mục tiêu giải cứu (KPP)',
      'cml1.payload': 'Tải trọng',
      'cml1.extension': 'Kéo dài sự sống',
      'cml1.precision': 'Độ chính xác hạ cánh',
      'cml1.reference': 'Tham chiếu NASA',
      'cml1.next': 'Sang Hồi 2: bàn cân não kiến trúc',

      'cml3.heading': 'Hồi 2 · CML 3 · Trade Space bốn phân khu',
      'cml3.launch': 'Launch Segment',
      'cml3.space': 'Space Segment',
      'cml3.flight': 'Flight Dynamics',
      'cml3.ground': 'Ground Segment',
      'cml3.power': 'Nguồn năng lượng',
      'cml3.edl': 'Hệ thống hạ cánh (EDL)',
      'cml3.telecom': 'Viễn thông',
      'cml3.trajectory': 'Quỹ đạo chuyển tiếp',
      'cml3.gauges': 'Bốn đồng hồ biên độ kỹ thuật',
      'cml3.gaugeTime': 'Biên độ thời gian',
      'cml3.gaugeMass': 'Biên độ khối lượng khô',
      'cml3.gaugePower': 'Biên độ năng lượng',
      'cml3.gaugeTelecom': 'Biên độ viễn thông',
      'cml3.need35': 'chuẩn >= 35%',
      'cml3.needDb': 'Deep Space >= 3 dB · Proximity >= 6 dB',
      'cml3.conflict': 'XUNG ĐỘT VẬT LÝ: pin mặt trời trong bão bụi, biên độ năng lượng tụt dưới 35%.',
      'cml3.deltaV': 'Delta-V',
      'cml3.cost': 'Chi phí',
      'cml3.next': 'Sang Hồi 3: cổng kiểm duyệt CML 4',

      'cml4.heading': 'Hồi 3 · CML 4 · Cổng kiểm duyệt kỹ thuật JPL',
      'cml4.ratio': 'Tỉ lệ đạt chuẩn',
      'cml4.need80': 'Cần >= 80% hạng G và không còn hạng R',
      'cml4.compliance': 'Công tắc quy trình NASA',
      'cml4.pp': 'Planetary Protection: khử trùng sinh học tàu',
      'cml4.approval': 'Launch Approval: phê duyệt an toàn hạt nhân',
      'cml4.approvalNotNeeded': 'Không dùng vật liệu phóng xạ nên không cần',
      'cml4.launch': 'LAUNCH MISSION',
      'cml4.blocked': 'Còn lỗi đỏ, chưa thể phóng',
      'cml4.back': 'Quay lại Hồi 2 tinh chỉnh',
      'cml4.knowledge': 'Kiến thức kỹ thuật',
      'cml4.clickRed': 'Bấm một dòng đỏ để xem giải thích',

      'exec.heading': 'Hồi 4-5 · Phóng tàu và hạ cánh EDL',
      'exec.statusDesigning': 'ĐANG THIẾT KẾ',
      'exec.statusLaunched': 'ĐÃ PHÓNG · ĐANG HÀNH TRÌNH',
      'exec.statusProximity': 'TỚI GẦN SAO HỎA · CHỜ ĐÈN HIỆU',
      'exec.statusCompleted': 'HẠ CÁNH THÀNH CÔNG',
      'exec.statusFailed': 'HẠ CÁNH THẤT BẠI',
      'exec.progress': 'Tiến trình hành trình',
      'exec.dsnSend': 'DSN đã gửi lệnh tới Sao Hỏa',
      'exec.beaconNeeded': 'Cần đèn hiệu dẫn đường dưới mặt đất. Chuyển sang Tab Sao Hỏa để cắm đèn hiệu.',
      'exec.gotoMars': 'Chuyển sang Tab Sao Hỏa / Kích hoạt đèn hiệu',
      'exec.waitingBeacon': 'Đang chờ sự kiện mars:beacon-deployed',
      'exec.debrief': 'Tổng kết đối chiếu thiết kế',
      'exec.analogue': 'Kiến trúc NASA tương đồng',
      'exec.cost': 'Tổng chi phí',
      'exec.injected': 'Khối lượng bơm vào quỹ đạo',
      'exec.dryMass': 'Khối lượng khô tàu',
      'exec.flight': 'Thời gian bay',
      'exec.sols': 'Sol',
      'exec.restart': 'Chạy lại'
    },
    en: {
      'app.title': 'EARTH MISSION CONTROL',
      'app.subtitle': 'NASA MISSION DESIGN LAB · CML 1-4',
      'app.signalWait': 'WAITING FOR SIGNAL',
      'app.signalLocked': 'DSN LOCK ACQUIRED',
      'app.sol': 'Sol',
      'app.lightTime': 'One-way light time',
      'app.minutes': 'min',
      'app.devPanel': 'Test bench',
      'app.simSos': 'Simulate: SOS from Mars',
      'app.simBeacon': 'Simulate: beacon deployed',
      'app.step1': 'Beat 1',
      'app.step2': 'Beat 2',
      'app.step3': 'Beat 3',
      'app.step4': 'Beat 4-5',
      'app.reset': 'Restart',

      'cml1.standbyTitle': 'WAITING FOR THE DISTRESS SIGNAL',
      'cml1.standbyBody': 'The Deep Space Network is sweeping. This screen unlocks when it receives mars:sos-received from Phase 1.',
      'cml1.heading': 'Beat 1 · CML 1-2 · Objective and survival KPP',
      'cml1.survival': 'Astronaut survival',
      'cml1.crop': 'Crop health',
      'cml1.dust': 'Dust storm',
      'cml1.dustActive': 'ACTIVE',
      'cml1.dustClear': 'CLEAR',
      'cml1.budgetBar': 'Total mission time against survival limit',
      'cml1.missionTime': 'Mission',
      'cml1.survivalLimit': 'Limit',
      'cml1.marginOk': 'Arrives {n} Sols early',
      'cml1.marginLate': 'Arrives {n} Sols late',
      'cml1.objectiveHeading': 'Choose the rescue objective (KPP)',
      'cml1.payload': 'Payload',
      'cml1.extension': 'Survival extension',
      'cml1.precision': 'Landing precision',
      'cml1.reference': 'NASA reference',
      'cml1.next': 'Go to Beat 2: architecture trade space',

      'cml3.heading': 'Beat 2 · CML 3 · Trade space across four segments',
      'cml3.launch': 'Launch Segment',
      'cml3.space': 'Space Segment',
      'cml3.flight': 'Flight Dynamics',
      'cml3.ground': 'Ground Segment',
      'cml3.power': 'Power source',
      'cml3.edl': 'Entry, descent and landing',
      'cml3.telecom': 'Telecom',
      'cml3.trajectory': 'Transfer trajectory',
      'cml3.gauges': 'Four engineering margin gauges',
      'cml3.gaugeTime': 'Time margin',
      'cml3.gaugeMass': 'Dry mass margin',
      'cml3.gaugePower': 'Power margin',
      'cml3.gaugeTelecom': 'Telecom margin',
      'cml3.need35': 'standard >= 35%',
      'cml3.needDb': 'Deep Space >= 3 dB · Proximity >= 6 dB',
      'cml3.conflict': 'PHYSICS CONFLICT: solar array during a dust storm drops the power margin below 35%.',
      'cml3.deltaV': 'Delta-V',
      'cml3.cost': 'Cost',
      'cml3.next': 'Go to Beat 3: CML 4 gate',

      'cml4.heading': 'Beat 3 · CML 4 · JPL technical review gate',
      'cml4.ratio': 'Green ratio',
      'cml4.need80': 'Needs >= 80% green and no red items',
      'cml4.compliance': 'NASA process switches',
      'cml4.pp': 'Planetary Protection: spacecraft sterilisation',
      'cml4.approval': 'Launch Approval: nuclear safety review',
      'cml4.approvalNotNeeded': 'No radioactive source selected, not required',
      'cml4.launch': 'LAUNCH MISSION',
      'cml4.blocked': 'Red items remain, launch is locked',
      'cml4.back': 'Back to Beat 2 to fix it',
      'cml4.knowledge': 'Engineering note',
      'cml4.clickRed': 'Click a red row to read the explanation',

      'exec.heading': 'Beat 4-5 · Launch and EDL',
      'exec.statusDesigning': 'DESIGNING',
      'exec.statusLaunched': 'LAUNCHED · IN TRANSIT',
      'exec.statusProximity': 'NEAR MARS · AWAITING BEACON',
      'exec.statusCompleted': 'LANDING SUCCESSFUL',
      'exec.statusFailed': 'LANDING FAILED',
      'exec.progress': 'Transit progress',
      'exec.dsnSend': 'DSN command sent to Mars',
      'exec.beaconNeeded': 'A ground beacon is required. Switch to the Mars tab and deploy it.',
      'exec.gotoMars': 'Switch to Mars tab / deploy beacon',
      'exec.waitingBeacon': 'Waiting for mars:beacon-deployed',
      'exec.debrief': 'Design comparison debrief',
      'exec.analogue': 'Closest NASA architecture',
      'exec.cost': 'Total cost',
      'exec.injected': 'Mass injected to orbit',
      'exec.dryMass': 'Spacecraft dry mass',
      'exec.flight': 'Flight time',
      'exec.sols': 'Sols',
      'exec.restart': 'Restart'
    }
  };

  var lang = 'vi';
  try {
    var stored = window.localStorage && window.localStorage.getItem('smdg.settings');
    if (stored) {
      var parsed = JSON.parse(stored);
      if (parsed && parsed.lang === 'en') lang = 'en';
    }
  } catch (err) { /* ignore */ }

  window.Phase2I18N = {
    t: function (key, vars) {
      var table = STRINGS[lang] || STRINGS.vi;
      var out = table[key] !== undefined ? table[key] : (STRINGS.vi[key] !== undefined ? STRINGS.vi[key] : key);
      if (vars) {
        Object.keys(vars).forEach(function (k) {
          out = out.replace('{' + k + '}', String(vars[k]));
        });
      }
      return out;
    },
    setLang: function (next) {
      if (next === 'vi' || next === 'en') {
        lang = next;
        window.dispatchEvent(new CustomEvent('phase2:lang-changed', { detail: { lang: lang } }));
      }
      return lang;
    },
    getLang: function () { return lang; },
    keys: function () { return Object.keys(STRINGS.vi); },
    tables: STRINGS
  };
})();
