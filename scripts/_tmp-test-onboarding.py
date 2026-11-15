"""Test onboarding bằng CDP thô qua websockets, kết nối đúng page target."""
import json, subprocess, time, sys, os, urllib.request
import websockets, asyncio

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
PORT = 9231
USER = os.path.expandvars(r"%LOCALAPPDATA%\Temp\onb-test-profile-9231")

proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={USER}", "--no-first-run", "--window-size=1440,900",
    "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3.5)


def page_ws():
    for _ in range(20):
        try:
            lst = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list").read())
            for t in lst:
                if t.get("type") == "page" and "about:blank" in t.get("url", ""):
                    return t["webSocketDebuggerUrl"]
            for t in lst:
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("no page target")


def log(*a):
    print(*a, flush=True)


async def main():
    results = []
    errs = []
    async with websockets.connect(page_ws(), max_size=50 * 1024 * 1024) as ws:
        mid = [0]

        async def send(method, params=None):
            mid[0] += 1
            i = mid[0]
            await ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == i:
                    if "error" in msg:
                        return {"__error": msg["error"]}
                    return msg.get("result", {})
                if msg.get("method") == "Runtime.consoleAPICalled" and msg["params"]["type"] in ("error", "warning"):
                    args = msg["params"]["args"]
                    if args:
                        errs.append(str(args[0].get("value", args[0].get("description", "")))[:200])
                if msg.get("method") == "Runtime.exceptionThrown":
                    errs.append("EXC:" + str(msg["params"]["exceptionDetails"].get("exception", {}).get("description", ""))[:200])

        async def js(expr):
            r = await send("Runtime.evaluate", {"expression": expr, "returnByValue": True,
                                                "awaitPromise": True, "userGesture": True})
            if "exceptionDetails" in r:
                errs.append("EVAL:" + json.dumps(r["exceptionDetails"])[:300])
                return None
            return r.get("result", {}).get("value")

        async def click(x, y):
            await send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
            await send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y,
                                                    "button": "left", "clickCount": 1})
            await send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y,
                                                    "button": "left", "clickCount": 1})

        async def goto(url, wait=6):
            await send("Page.navigate", {"url": url})
            await asyncio.sleep(wait)

        await send("Page.enable")
        await send("Runtime.enable")
        await send("Log.enable")

        # ---- T0: nạp trang ----
        await goto("http://127.0.0.1:8391/nasa", 7)
        ready = await js("document.readyState")
        dj = await js("typeof window.__devJump")
        results.append(("T0 nạp trang + devJump", ready == "complete" and dj == "function", [ready, dj]))
        await js("localStorage.clear(); 'ok'")

        # ---- T1: thẻ tự hiện lần đầu ----
        await js("(() => { window.__devJump('base',{day:1}); return 'ok'; })()")
        await asyncio.sleep(4)
        st = await js("""(() => {
          const root = document.querySelector('.onb-root');
          if (!root) return {none: true};
          const card = root.querySelector('.onb-card');
          const go = root.querySelector('.onb-go');
          const r = go.getBoundingClientRect();
          const topEl = document.elementFromPoint(Math.round(r.left+r.width/2), Math.round(r.top+r.height/2));
          const cr = card.getBoundingClientRect();
          const dims = [...root.querySelectorAll('.onb-dim')];
          return {
            count: document.querySelectorAll('.onb-root').length,
            hidden: root.hidden,
            title: root.querySelector('.onb-title').textContent,
            countTxt: root.querySelector('.onb-count').textContent,
            goText: go.textContent,
            goH: Math.round(r.height),
            blocks: [...root.querySelectorAll('.onb-block-h')].map(e=>e.textContent),
            topElAtGo: topEl ? topEl.tagName + '.' + topEl.className : 'none',
            cardZ: getComputedStyle(card).zIndex,
            cardRect: {t: Math.round(cr.top), l: Math.round(cr.left), w: Math.round(cr.width), h: Math.round(cr.height)},
            dimCount: dims.length,
            dimCss: dims.map(d=>d.style.cssText),
            ringHidden: root.querySelector('.onb-ring').hidden,
            bg: getComputedStyle(card).backgroundColor,
            laterH: Math.round(root.querySelector('.onb-later').getBoundingClientRect().height)
          };
        })()""")
        t1_ok = bool(st) and not st.get("none") and st["hidden"] is False and st["count"] == 1
        results.append(("T1 thẻ tự hiện lần đầu", t1_ok, st))
        results.append(("T1b làm tối cả màn (spotlight all)",
                        bool(st) and st["ringHidden"] is True and st["dimCount"] == 4
                        and st["dimCss"][1].startswith("left: 0px; top: 0px; width: 0px"),
                        {"ringHidden": st and st.get("ringHidden"), "dimCss": st and st.get("dimCss")}))

        # ---- T8: nguyên văn ----
        EXPECT = "Chào mừng đến với ngôi nhà duy nhất của bạn trên Sao Hỏa"
        results.append(("T8 tiêu đề khớp nguyên văn", bool(st) and st.get("title") == EXPECT,
                        {"got": st and st.get("title"), "len": len(st.get("title") or "")}))

        # ---- T2: bấm nút, lưu trạng thái ----
        gr = await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); const r=g.getBoundingClientRect(); return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)}; })()""")
        await click(gr["x"], gr["y"])
        await asyncio.sleep(1.2)
        after = await js("""({hidden: document.querySelector('.onb-root').hidden, seen: localStorage.getItem('smdg.tutorialsSeen')})""")
        results.append(("T2 bấm nút đóng ghi id vào localStorage",
                        bool(after) and after["hidden"] is True and after["seen"] == '["hab_intro"]', after))

        # ---- T3: tải lại không hiện lại ----
        await goto("http://127.0.0.1:8391/nasa", 7)
        await js("(() => { window.__devJump('base',{day:1}); return 'ok'; })()")
        await asyncio.sleep(3.5)
        again = await js("""(() => { const r=document.querySelector('.onb-root');
          return r ? {hidden: r.hidden, title: r.querySelector('.onb-title').textContent} : {none:true}; })()""")
        results.append(("T3 tải lại thẻ không hiện lại",
                        bool(again) and (again.get("none") or again.get("hidden") is True), again))

        # ---- T4: sổ tay ----
        await js("""(() => { const b=document.querySelector('[data-act="guide"]'); if (b) b.click(); return 'ok'; })()""")
        await asyncio.sleep(1.8)
        book = await js("""(() => {
          const bk = document.querySelector('.onb-book');
          if (!bk) return {none: true};
          const items = [...bk.querySelectorAll('.onb-book-item')];
          return {
            items: items.length,
            groups: [...bk.querySelectorAll('.onb-book-gh')].map(e=>e.textContent),
            titles: items.map(e=>e.querySelector('.onb-book-txt').textContent),
            flags: items.map(e=>e.querySelector('.onb-book-flag').textContent),
            itemH: Math.round(items[0].getBoundingClientRect().height)
          };
        })()""")
        results.append(("T4 sổ tay liệt kê đủ 8 thẻ",
                        bool(book) and book.get("items") == 8
                        and len(book.get("groups") or []) == 2, book))

        if book and book.get("items") == 8:
            await js("""(() => { document.querySelectorAll('.onb-book-item')[2].click(); return 'ok'; })()""")
            await asyncio.sleep(1.4)
            card = await js("""(() => { const r=document.querySelector('.onb-root');
              return r ? {hidden: r.hidden, title: r.querySelector('.onb-title').textContent, mode: r.dataset.mode} : {none:true}; })()""")
            results.append(("T4b bấm thẻ trong sổ tay mở được",
                            bool(card) and card.get("hidden") is False and card.get("mode") == "read", card))
            await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
            await asyncio.sleep(0.9)
            back = await js("""(() => { const b=document.querySelector('.onb-book'); return b ? {back:true} : {none:true}; })()""")
            results.append(("T4c đóng thẻ quay lại sổ tay", bool(back) and back.get("back") is True, back))
            await js("""(() => { const x=document.querySelector('.onb-book .onb-book-x'); if (x) x.click(); return 'ok'; })()""")
            await asyncio.sleep(0.6)

        # ---- T5 + T6: panel lifesupport, spotlight đúng nút ----
        await js("""(() => { const b=document.querySelector('.bs-hot[data-id="lifesupport"]'); if (b) b.click(); return 'ok'; })()""")
        await asyncio.sleep(2.5)
        spot = await js("""(() => {
          const root = document.querySelector('.onb-root');
          if (!root || root.hidden) return {none:true};
          const ring = root.querySelector('.onb-ring');
          const rs = ring.hidden ? null : ring.getBoundingClientRect();
          const tgt = document.querySelector('.bs-hot[data-id="lifesupport"]');
          const ts = tgt ? tgt.getBoundingClientRect() : null;
          return {
            title: root.querySelector('.onb-title').textContent,
            ring: rs ? {t: rs.top, l: rs.left, w: rs.width, h: rs.height} : null,
            target: ts ? {t: ts.top, l: ts.left, w: ts.width, h: ts.height} : null,
            dims: [...root.querySelectorAll('.onb-dim')].map(d=>d.style.cssText),
            cardRect: (()=>{const r=root.querySelector('.onb-card').getBoundingClientRect();return {t:Math.round(r.top),l:Math.round(r.left),w:Math.round(r.width),h:Math.round(r.height)};})()
          };
        })()""")
        ok5 = bool(spot) and not spot.get("none") and spot.get("title") == "Nhà máy tạo không khí và nước sạch"
        results.append(("T5 panel lifesupport hiện thẻ moxie_eclss", ok5, spot))

        err_px = None
        overlap = None
        if ok5 and spot.get("ring") and spot.get("target"):
            r, t = spot["ring"], spot["target"]
            err_px = max(abs(r["t"] - (t["t"] - 12)), abs(r["l"] - (t["l"] - 12)),
                         abs(r["w"] - (t["w"] + 24)), abs(r["h"] - (t["h"] + 24)))
            c = spot["cardRect"]
            overlap = not (c["t"] >= r["t"] + r["h"] or c["t"] + c["h"] <= r["t"])
        results.append(("T6 spotlight khớp phần tử đích (<8px)",
                        err_px is not None and err_px < 8, {"err_px": err_px, "ring": spot.get("ring"), "target": spot.get("target")}))
        results.append(("T6b thẻ không đè vùng sáng", overlap is not None and overlap is False, {"overlap": overlap}))
        await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
        await asyncio.sleep(0.9)

        # ---- T7: đổi ngôn ngữ ----
        await js("""(async () => { const i18n = await import('/nasa/i18n.js'); i18n.setLang('en'); return 'en'; })()""")
        await asyncio.sleep(0.9)
        await js("""(() => { const b=document.querySelector('[data-act="guide"]'); if (b) b.click(); return 'ok'; })()""")
        await asyncio.sleep(1.5)
        en_book = await js("""(() => { const b=document.querySelector('.onb-book');
          return b ? {title: b.querySelector('.onb-book-title').textContent, sub: b.querySelector('.onb-book-sub').textContent,
                      groups: [...b.querySelectorAll('.onb-book-gh')].map(e=>e.textContent),
                      first: b.querySelector('.onb-book-item .onb-book-txt').textContent} : {none:true}; })()""")
        results.append(("T7 sổ tay đổi sang EN",
                        bool(en_book) and en_book.get("title") == "Handbook"
                        and "Phase 1" in " ".join(en_book.get("groups") or []), en_book))
        await js("""(() => { document.querySelectorAll('.onb-book-item')[0].click(); return 'ok'; })()""")
        await asyncio.sleep(1.4)
        en_card = await js("""(() => { const r=document.querySelector('.onb-root');
          return r ? {title: r.querySelector('.onb-title').textContent, go: r.querySelector('.onb-go').textContent,
                      blocks: [...r.querySelectorAll('.onb-block-h')].map(e=>e.textContent),
                      count: r.querySelector('.onb-count').textContent, later: r.querySelector('.onb-later').textContent} : {none:true}; })()""")
        results.append(("T7b thẻ đổi hoàn toàn sang EN",
                        bool(en_card) and en_card.get("title") == "Welcome to your only home on Mars"
                        and en_card.get("go") == "Got it, let's check the Hab!"
                        and en_card.get("blocks") == ["How to", "NASA angle", "Survival tip"], en_card))
        await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
        await asyncio.sleep(0.6)
        await js("""(() => { const x=document.querySelector('.onb-book .onb-book-x'); if (x) x.click(); return 'ok'; })()""")
        await js("""(async () => { const i18n = await import('/nasa/i18n.js'); i18n.setLang('vi'); return 'vi'; })()""")
        await asyncio.sleep(0.6)

        # ---- T9a: 1440x900 ----
        await js("""(async () => { const m = await import('/nasa/onboarding.js'); await m.showTutorial({id:'hab_intro'}); return 'shown'; })()""")
        await asyncio.sleep(1)
        fit = await js("""(() => {
          const card = document.querySelector('.onb-root .onb-card');
          const r = card.getBoundingClientRect();
          const p = card.querySelector('.onb-block-p');
          return {t: Math.round(r.top), b: Math.round(r.bottom), l: Math.round(r.left), rr: Math.round(r.right),
                  vw: innerWidth, vh: innerHeight, scroll: card.scrollHeight, client: card.clientHeight,
                  inView: r.top >= 0 && r.bottom <= innerHeight + 1 && r.left >= 0 && r.right <= innerWidth + 1,
                  firstP: p ? p.textContent.slice(0, 30) : null, firstPH: p ? Math.round(p.getBoundingClientRect().height) : 0};
        })()""")
        results.append(("T9a 1440x900 thẻ không tràn", bool(fit) and fit["inView"] is True, fit))
        await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
        await asyncio.sleep(0.6)

        # ---- T9b: 390x844 ----
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True})
        await asyncio.sleep(1)
        await js("""(async () => { const m = await import('/nasa/onboarding.js'); await m.showTutorial({id:'hab_intro'}); return 'shown'; })()""")
        await asyncio.sleep(1.2)
        fit2 = await js("""(() => {
          const card = document.querySelector('.onb-root .onb-card');
          const r = card.getBoundingClientRect();
          return {t: Math.round(r.top), b: Math.round(r.bottom), l: Math.round(r.left), rr: Math.round(r.right),
                  vw: innerWidth, vh: innerHeight, scroll: card.scrollHeight, client: card.clientHeight,
                  canScroll: card.scrollHeight > card.clientHeight,
                  inView: r.top >= 0 && r.bottom <= innerHeight + 2 && r.left >= 0 && r.right <= innerWidth + 2,
                  hOverflow: document.documentElement.scrollWidth > innerWidth};
        })()""")
        results.append(("T9b 390x844 thẻ không tràn", bool(fit2) and fit2["inView"] is True
                        and fit2["hOverflow"] is False, fit2))
        await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
        await send("Emulation.clearDeviceMetricsOverride")
        await asyncio.sleep(0.8)

        # ---- T10: motion off ----
        await js("document.documentElement.classList.add('motion-off'); 'ok'")
        await js("""(async () => { const m = await import('/nasa/onboarding.js'); await m.showTutorial({id:'hab_intro'}); return 'shown'; })()""")
        await asyncio.sleep(0.5)
        motion = await js("""(() => {
          const card = document.querySelector('.onb-root .onb-card');
          const cs = getComputedStyle(card);
          return {opacity: cs.opacity, transition: cs.transitionDuration};
        })()""")
        results.append(("T10 motion-off không mờ dần", bool(motion) and motion["opacity"] == "1", motion))
        await js("document.documentElement.classList.remove('motion-off'); 'ok'")
        await js("""(() => { const g=document.querySelector('.onb-root .onb-go'); if (g) g.click(); return 'ok'; })()""")
        await asyncio.sleep(0.6)

        # ---- T11: console ----
        results.append(("T11 không lỗi console", len(errs) == 0, {"cdp": errs[:8]}))

    log(json.dumps(results, ensure_ascii=False, indent=1))


try:
    asyncio.run(main())
finally:
    proc.terminate()
