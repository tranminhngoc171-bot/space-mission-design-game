/**
 * feature-cml4-checklist.js — Hồi 3 (CML 4).
 *
 * Trách nhiệm: bảng kiểm duyệt RYG, thanh tỉ lệ đạt chuẩn, hai công tắc quy trình
 * NASA, và khoá nút LAUNCH khi còn lỗi đỏ. Toàn bộ phán quyết do engine đưa ra
 * trong full.computed.checklist; file này chỉ hiển thị và chuyển tiếp thao tác.
 */
(function () {
  'use strict';
  var U = window.Phase2Util;
  var t = U.t;

  /* Thẻ kiến thức hiện khi bấm vào dòng đỏ. Nội dung kỹ thuật giải thích vì sao. */
  var KNOWLEDGE = {
    KPP_TIMELINE: {
      title: { vi: 'Thời gian là ràng buộc cứng', en: 'Time is a hard constraint' },
      body: {
        vi: 'Cửa sổ chuyển tiếp Hohmann chỉ mở theo chu kỳ giao hội 779,94 ngày. Đi nhanh hơn cần delta-V lớn hơn, nghĩa là tên lửa mạnh hơn hoặc bỏ bớt hàng. Không có cách nào vừa nhanh vừa rẻ, đó là bài toán thật của mọi sứ mệnh Sao Hỏa.',
        en: 'A Hohmann window opens on the 779.94-day synodic cycle. Going faster costs more delta-V, which means a bigger launcher or less cargo. Nothing is both fast and cheap, and that is the real Mars problem.'
      }
    },
    DELTA_V_BUDGET: {
      title: { vi: 'Delta-V là ngân sách, không phải thông số', en: 'Delta-V is a budget' },
      body: {
        vi: 'Tên lửa hạng trung chỉ có khoảng 4,1 km/s năng lực chuyển tiếp. Quỹ đạo năng lượng cao cần 5,1 km/s. Thiếu năng lực thì tàu không rời được quỹ đạo Trái Đất, không phải chỉ chậm hơn.',
        en: 'A medium launcher offers about 4.1 km/s of injected capability. A high-energy transfer needs 5.1 km/s. Short of it, the spacecraft does not leave Earth orbit at all.'
      }
    },
    DRY_MASS_MARGIN: {
      title: { vi: 'Vì sao JPL đòi 35% biên độ khô', en: 'Why JPL wants 35% dry mass margin' },
      body: {
        vi: 'Mọi hệ thống đều tăng cân từ khi thiết kế tới khi lắp ráp xong. CML 4 đòi biên độ lớn vì chi phí cắt cân sau này luôn đắt hơn dự phòng trước. Tàu không còn biên độ là tàu không còn chỗ sửa sai.',
        en: 'Every system gains mass between concept and integration. CML 4 demands large margin because cutting mass later always costs more than reserving it now. No margin means no room for error.'
      }
    },
    POWER_MARGIN: {
      title: { vi: 'Pin mặt trời và bão bụi Sao Hỏa', en: 'Solar arrays and Mars dust storms' },
      body: {
        vi: 'Bụi lơ lửng trong khí quyển Sao Hỏa chặn trực tiếp ánh sáng tới mảng pin, suy giảm có thể tới 30% trong nhiều tuần. RTG (đồng vị phóng xạ) không phụ thuộc ánh sáng nhưng cần phê duyệt an toàn hạt nhân khi phóng.',
        en: 'Airborne dust directly blocks light reaching the array, cutting output by up to 30% for weeks. An RTG does not depend on light, but it requires nuclear launch safety approval.'
      }
    },
    TELECOM_MARGIN: {
      title: { vi: 'Hai loại tuyến liên lạc', en: 'Two kinds of link' },
      body: {
        vi: 'Tuyến không gian sâu cần ít nhất 3 dB để đóng khung dữ liệu qua hàng trăm triệu km. Tuyến tầm gần lúc hạ cánh cần 6 dB vì phải khoá đèn hiệu dưới mặt đất trong điều kiện nhiễu. Băng X thường đủ xa nhưng thiếu gần.',
        en: 'The deep space link needs 3 dB minimum to close frames across hundreds of millions of km. The proximity link needs 6 dB to lock the surface beacon under noise. X-band is often fine far away and short up close.'
      }
    },
    EDL_ARCHITECTURE: {
      title: { vi: 'Khí quyển loãng 0,6% Trái Đất', en: 'An atmosphere 0.6% of Earth' },
      body: {
        vi: 'Khí quyển Sao Hỏa quá loãng để dù hãm tải nặng, nên Curiosity và Perseverance dùng động cơ hãm phản lực (sky crane). Túi khí chỉ hợp với tải nhẹ như Pathfinder.',
        en: 'The Martian atmosphere is too thin for parachutes to slow heavy payloads, which is why Curiosity and Perseverance used retro-propulsion. Airbags only work for light payloads like Pathfinder.'
      }
    },
    PLANETARY_PROTECTION: {
      title: { vi: 'Bảo vệ hành tinh', en: 'Planetary protection' },
      body: {
        vi: 'Tàu mang vi khuẩn Trái Đất lên Sao Hỏa sẽ làm hỏng chính thí nghiệm tìm sự sống, và làm ô nhiễm mẫu vật mang về. Đây là yêu cầu pháp lý theo Hiệp ước Vũ trụ 1967, không phải thủ tục hành chính.',
        en: 'Carrying Earth microbes to Mars would spoil the very search for life and contaminate returned samples. This is a legal requirement under the 1967 Outer Space Treaty, not paperwork.'
      }
    },
    LAUNCH_APPROVAL: {
      title: { vi: 'Phê duyệt an toàn hạt nhân', en: 'Nuclear launch approval' },
      body: {
        vi: 'Nguồn RTG chứa plutonium-238. Mỹ yêu cầu một quy trình phê duyệt liên ngành trước khi phóng, tính cả kịch bản phóng thất bại và tàu rơi về Trái Đất.',
        en: 'An RTG carries plutonium-238. The United States requires an interagency approval process before launch, including the failed-launch and Earth re-entry cases.'
      }
    }
  };

  function mount(root, engine) {
    var expanded = null;

    function render(full) {
      var checklist = full.computed.checklist;
      var compliance = full.state.compliance;
      var requiresNuclear = full.computed.metrics.requiresNuclearApproval;
      var ratioPct = Math.round(checklist.greenRatio * 100);

      var items = checklist.items.map(function (item) {
        var isExpanded = expanded === item.id;
        var row = U.el('button', {
          class: 'p2-check ' + U.ryg(item.status) + (isExpanded ? ' is-open' : ''),
          type: 'button',
          onclick: function () {
            expanded = isExpanded ? null : item.id;
            render(full);
          }
        }, [
          U.el('span', { class: 'p2-check-badge', text: item.status }),
          U.el('span', { class: 'p2-check-body' }, [
            U.el('span', { class: 'p2-check-cat', text: item.category }),
            U.el('span', { class: 'p2-check-label', text: item.label }),
            isExpanded ? U.el('span', { class: 'p2-check-detail', text: item.detail }) : null
          ])
        ]);

        if (!isExpanded) return U.el('div', { class: 'p2-check-wrap' }, [row]);

        var note = KNOWLEDGE[item.id];
        var lang = window.Phase2I18N ? window.Phase2I18N.getLang() : 'vi';
        return U.el('div', { class: 'p2-check-wrap' }, [
          row,
          U.el('div', { class: 'p2-knowledge' }, [
            note ? U.el('h4', { class: 'p2-knowledge-title', text: note.title[lang] || note.title.vi }) : null,
            note ? U.el('p', { class: 'p2-knowledge-body', text: note.body[lang] || note.body.vi }) : null,
            U.el('p', { class: 'p2-muted', text: item.detail }),
            item.status === 'R' ? U.el('button', {
              class: 'p2-btn p2-btn-sm', type: 'button', text: t('cml4.back'),
              onclick: function (event) {
                event.stopPropagation();
                expanded = null;
                engine.setCmlStep(2);
              }
            }) : null
          ])
        ]);
      });

      function toggle(key, label, note, disabled) {
        return U.el('label', { class: 'p2-switch' + (disabled ? ' is-disabled' : '') }, [
          U.el('input', {
            type: 'checkbox',
            checked: compliance[key] ? 'checked' : null,
            disabled: disabled ? 'disabled' : null,
            onchange: function (event) { engine.updateCompliance(key, event.target.checked); }
          }),
          U.el('span', { class: 'p2-switch-track' }, [U.el('span', { class: 'p2-switch-knob' })]),
          U.el('span', { class: 'p2-switch-text' }, [
            U.el('span', { class: 'p2-switch-label', text: label }),
            note ? U.el('span', { class: 'p2-switch-note', text: note }) : null
          ])
        ]);
      }

      U.clear(root).appendChild(
        U.el('section', { class: 'p2-panel' }, [
          U.el('div', { class: 'p2-panel-head' }, [
            U.el('h2', { class: 'p2-h2', text: t('cml4.heading') }),
            U.el('span', { class: 'p2-badge', text: 'CML 4' })
          ]),

          U.el('div', { class: 'p2-ratio ' + (checklist.canLaunch ? 'is-green' : (checklist.greenRatio >= 0.5 ? 'is-yellow' : 'is-red')) }, [
            U.el('div', { class: 'p2-ratio-head' }, [
              U.el('span', { text: t('cml4.ratio') }),
              U.el('span', { class: 'p2-num', text: checklist.greenCount + '/' + checklist.totalCount + ' · ' + ratioPct + '%' })
            ]),
            U.el('div', { class: 'p2-bar-track' }, [
              U.el('div', { class: 'p2-bar-fill', style: 'width:' + ratioPct + '%' })
            ]),
            U.el('span', { class: 'p2-gauge-hint', text: t('cml4.need80') })
          ]),

          U.el('div', { class: 'p2-checks' }, items),

          U.el('h3', { class: 'p2-h3', text: t('cml4.compliance') }),
          U.el('div', { class: 'p2-switches' }, [
            toggle('planetaryProtectionSterilized', t('cml4.pp'), null, false),
            toggle('launchApprovalSubmitted', t('cml4.approval'),
              requiresNuclear ? null : t('cml4.approvalNotNeeded'), !requiresNuclear)
          ]),

          U.el('div', { class: 'p2-actions' }, [
            U.el('button', {
              class: 'p2-btn', type: 'button', text: t('app.step2'),
              onclick: function () { engine.setCmlStep(2); }
            }),
            U.el('button', {
              class: 'p2-btn p2-btn-launch' + (checklist.canLaunch ? '' : ' is-locked'),
              type: 'button',
              disabled: checklist.canLaunch ? null : 'disabled',
              text: t('cml4.launch'),
              onclick: function () {
                if (!engine.launchMission()) {
                  root.classList.add('is-shake');
                  window.setTimeout(function () { root.classList.remove('is-shake'); }, 450);
                }
              }
            })
          ]),
          U.el('p', { class: 'p2-muted p2-tiny', text: checklist.canLaunch ? t('cml4.clickRed') : t('cml4.blocked') })
        ])
      );
    }

    var unsubscribe = engine.subscribe('state:changed', render);
    window.addEventListener('phase2:lang-changed', function () { render(engine.getFullState()); });
    render(engine.getFullState());
    return { destroy: unsubscribe };
  }

  window.Phase2Features = window.Phase2Features || {};
  window.Phase2Features.cml4Checklist = mount;
})();
