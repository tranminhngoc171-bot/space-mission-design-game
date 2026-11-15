
  /* Vercel phục vụ trang ở /nasa không có dấu / cuối. Khi đó đường dẫn
     tương đối "./story.js" bị hiểu thành "/story.js" và trả 404.
     Vì vậy mọi import phải dùng URL tuyệt đối dựng từ thư mục hiện tại. */
  const _p = location.pathname.split('/');
  if (_p[_p.length - 1].indexOf('.') !== -1) _p[_p.length - 1] = '';
  const BASE = location.origin + _p.join('/').replace(/\/?$/, '/');

  const { startStory }      = await import(BASE + 'story.js');
  const { startBase }       = await import(BASE + 'base.js');
  const { startComms }      = await import(BASE + 'comms.js');
  const { playIntro }       = await import(BASE + 'intro-video.js');
  const { applyToDom, onLangChange, t } = await import(BASE + 'i18n.js');
  const { loadSettings }    = await import(BASE + 'settings.js');
  const { initAudio, bindClickSounds, playClick } = await import(BASE + 'audio.js');
  const { openSettings }    = await import(BASE + 'settings-ui.js');

  /* cài đặt và âm thanh nạp trước khi người chơi bấm Bắt đầu,
     để nhạc nền và cỡ chữ đúng ngay từ khung đầu */
  loadSettings();
  initAudio();
  applyToDom();

  const boot = document.getElementById('boot');
  const btn  = document.getElementById('start');
  const gear = document.getElementById('settings-btn');

  /* Cờ đặt ở phạm vi ngoài, không đặt trong callback. Nếu đặt trong
     callback thì mỗi lần onFinish được gọi lại tạo một cờ mới, và cờ
     đó luôn là false, nên không chặn được gì. */
  let baseStarted = false;

  /* ---------- Giai đoạn 1: bảng điều khiển viễn thông ----------
     Màn đầu tiên sau khi tỉnh dậy: gọi cứu xong mới quản lý căn cứ.
     Cờ dưới đây để lần sau vào game không phải làm lại ba bước. */
  const STAGE1_KEY = 'smdg.stage1Done';

  function stage1Done() {
    try { return localStorage.getItem(STAGE1_KEY) === '1'; } catch (e) { return false; }
  }

  /* Mở bảng viễn thông trong một lớp phủ riêng.
     comms.js không có nút đóng nội bộ, nên nút "Bỏ qua" ở đây là lối
     thoát duy nhất. Cả hai đường ra (xong ba bước, hoặc bỏ qua) đều
     gọi comms.destroy() rồi gỡ lớp phủ trước khi đi tiếp, nhờ vậy
     không bao giờ còn khung trắng hay panel nằm lại trên màn căn cứ. */
  function openStage1({ onDone, onSkip }) {
    const host = document.createElement('div');
    host.className = 'comms-host';
    document.body.appendChild(host);

    const skip = document.createElement('button');
    skip.type = 'button';
    skip.className = 'comms-skip';
    skip.textContent = t('comms.skip');
    host.appendChild(skip);

    let closed = false;
    const comms = startComms({
      container: host,
      onDone: () => {
        if (closed) return;
        closed = true;
        /* Ghi cờ trước khi dọn, để lần tải lại trang sau không hỏi lại. */
        try { localStorage.setItem(STAGE1_KEY, '1'); } catch (e) { /* trình duyệt chặn ghi thì vẫn đi tiếp */ }
        if (comms && typeof comms.destroy === 'function') comms.destroy();
        host.remove();
        if (typeof onDone === 'function') onDone();
      },
    });

    skip.addEventListener('click', () => {
      playClick();
      if (closed) return;
      closed = true;
      if (comms && typeof comms.destroy === 'function') comms.destroy();
      host.remove();
      if (typeof onSkip === 'function') onSkip();
    });

    return {
      destroy: () => {
        if (closed) return;
        closed = true;
        if (comms && typeof comms.destroy === 'function') comms.destroy();
        host.remove();
      },
    };
  }

  /* Vào màn căn cứ. Tách riêng vì có hai đường vào: sau Giai đoạn 1,
     và vào thẳng khi cờ đã có sẵn. */
  function enterBase(playerName) {
    if (baseStarted) return;
    baseStarted = true;

    const host = document.createElement('div');
    host.className = 'base-host';
    document.body.appendChild(host);
    startBase({
      container: host,
      playerName,
      onExit: () => {
        host.remove();
        baseStarted = false;
        boot.style.display = '';
        delete btn.dataset.started;
      },
    });
  }

  /* Sau màn mở đầu: Giai đoạn 1 trước, căn cứ sau. */
  function afterStory(playerName) {
    if (stage1Done()) { enterBase(playerName); return; }
    openStage1({
      onDone: () => enterBase(playerName),
      onSkip: () => {
        /* Bỏ qua vẫn đánh dấu đã qua, để lần sau không bị chặn ở đây
           nữa. Ai muốn xem lại thì bấm nút trong màn căn cứ. */
        try { localStorage.setItem(STAGE1_KEY, '1'); } catch (e) { /* bỏ qua */ }
        enterBase(playerName);
      },
    });
  }

  gear.addEventListener('click', () => { playClick(); openSettings(); });

  btn.addEventListener('click', async () => {
    /* Chặn bấm hai lần. Không có cờ này, double-click tạo ra hai màn
       truyện chồng nhau và hai listener bàn phím cùng chạy. */
    if (btn.dataset.started === '1') return;
    btn.dataset.started = '1';

    playClick();
    boot.style.display = 'none';
    await playIntro();
    startStory({
      onFinish: ({ playerName }) => {
        /* Màn mở đầu xong thì mở Giai đoạn 1 rồi mới vào căn cứ.
           Cờ baseStarted ở phạm vi ngoài chặn trường hợp onFinish bị
           gọi hai lần, tránh hai màn căn cứ chồng lên nhau. */
        if (baseStarted) return;
        afterStory(playerName);
      },
    });
  });

  /* ---------- chơi lại Giai đoạn 1 từ màn căn cứ ----------
     base.js phát sự kiện này khi bấm thẻ "Chơi lại màn liên lạc".
     Dùng sự kiện thay vì import thẳng comms.js vào base.js để hai
     màn không phụ thuộc vòng vào nhau. Lớp phủ của comms nằm trên
     màn căn cứ (z-index 90), nhưng vẫn ẩn màn căn cứ đi để trình đọc
     màn hình không đọc lẫn hai lớp nội dung. */
  window.addEventListener('smdg:comms-replay', () => {
    if (!baseStarted) return;
    if (document.querySelector('.comms-host')) return;

    const baseHost = document.querySelector('.base-host');
    if (baseHost) baseHost.style.visibility = 'hidden';
    const restore = () => { if (baseHost) baseHost.style.visibility = ''; };

    openStage1({ onDone: restore, onSkip: restore });
  });

  bindClickSounds();

  /* đổi ngôn ngữ thì cập nhật cả khung khởi động và nút bỏ qua */
  onLangChange(() => {
    applyToDom();
    const sk = document.querySelector('.comms-skip');
    if (sk) sk.textContent = t('comms.skip');
  });
