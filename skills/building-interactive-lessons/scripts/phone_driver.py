"""Use a built page like a person on a phone: each call does a few actions and saves one screenshot of the screen.

For user tests (SKILL.md step 5): a test persona sees the page only through these screenshots, never its files.
The page is set once per session with --page; later calls reuse it.

Usage (one or more actions per call, run in order):
    python3 phone_driver.py SESSION --page lesson.html open start
    python3 phone_driver.py SESSION open start            # go to the start page (or a chapter: open chapter-2, open next)
    python3 phone_driver.py SESSION down                  # scroll down about one screen
    python3 phone_driver.py SESSION up                    # scroll up about one screen
    python3 phone_driver.py SESSION click "Switch to door 2"   # tap the visible thing whose text matches best
    python3 phone_driver.py SESSION type "my answer"      # type into the text box on screen
    python3 phone_driver.py SESSION wait                  # wait 2 seconds (let an animation finish)
    python3 phone_driver.py SESSION look                  # just take a screenshot of the screen now

It prints the path of the screenshot (390 x 844, a phone screen). One page stays open per SESSION between calls, the
way a phone keeps a tab open: nothing you did on the page is lost between calls.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path.cwd() / "phone-sessions"

FIND_AND_MARK = """(wanted) => {
  const want = wanted.trim().toLowerCase();
  const all = [...document.querySelectorAll('button, a, summary, input, label, [role=button], .option, .chip, .blank')];
  const seen = all.filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; });
  const text = el => (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().toLowerCase();
  const onScreen = el => { const r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; };
  const score = el => (text(el) === want ? 0 : 1) * 1000 + (onScreen(el) ? 0 : 500) + text(el).length;
  const matches = seen.filter(el => text(el).includes(want)).sort((a, b) => score(a) - score(b));
  if (!matches.length) return null;
  if (!onScreen(matches[0])) matches[0].scrollIntoView({ block: 'center' });   // a thumb taps what it can see; nothing moves first
  matches[0].setAttribute('data-drive-target', '1');
  return text(matches[0]).slice(0, 60);
}"""


def serve(session):
    """Keep one phone-sized page open and run the actions each client call sends."""
    from playwright.sync_api import sync_playwright
    folder = HERE / session
    folder.mkdir(parents=True, exist_ok=True)
    page_path = Path((folder / "page.txt").read_text().strip())
    address = str(folder / "socket")
    if os.path.exists(address):
        os.remove(address)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(address)
    listener.listen(1)
    shots = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        context.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") else route.abort())
        tab = context.new_page()
        tab.goto(page_path.as_uri() + "#start")
        tab.wait_for_timeout(300)
        while True:
            connection, _ = listener.accept()
            actions = json.loads(connection.recv(1 << 20).decode())
            notes = []
            index = 0
            while index < len(actions):
                action = actions[index]
                index += 1
                if action == "open":
                    target = actions[index]; index += 1
                    chapters = tab.evaluate("() => LESSON.chapters.map(c => c.id)")
                    current = tab.evaluate("location.hash.replace('#', '') || 'start'")
                    order = ["start"] + chapters + ["field-guide"]
                    if target == "next":
                        target = order[min(order.index(current) + 1, len(order) - 1)] if current in order else "start"
                    elif target.startswith("chapter-") and target[8:].isdigit():
                        target = chapters[int(target[8:]) - 1]
                    elif target in ("guide", "field-guide"):
                        target = "field-guide"
                    tab.evaluate(f"location.hash = {json.dumps(target)}")
                    tab.wait_for_timeout(300)
                    tab.evaluate("window.scrollTo(0, 0)")
                elif action in ("down", "up"):
                    tab.evaluate(f"window.scrollBy(0, {700 if action == 'down' else -700})")
                    tab.wait_for_timeout(150)
                elif action == "click":
                    text = actions[index]; index += 1
                    if tab.evaluate(FIND_AND_MARK, text) is None:
                        notes.append(f"nothing on the page says '{text}'")
                    else:
                        tab.wait_for_timeout(100)
                        tab.locator("[data-drive-target='1']").first.click()
                        tab.evaluate("document.querySelectorAll('[data-drive-target]').forEach(el => el.removeAttribute('data-drive-target'))")
                        tab.wait_for_timeout(700)
                elif action == "type":
                    text = actions[index]; index += 1
                    found = tab.evaluate("""() => { const boxes = [...document.querySelectorAll('textarea')].filter(b => { const r = b.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && r.width > 0; });
                      if (!boxes.length) return false; boxes[0].setAttribute('data-drive-box', '1'); return true; }""")
                    if not found:
                        notes.append("no text box on screen")
                    else:
                        tab.locator("[data-drive-box='1']").first.fill(text)
                        tab.evaluate("document.querySelectorAll('[data-drive-box]').forEach(el => el.removeAttribute('data-drive-box'))")
                elif action == "wait":
                    tab.wait_for_timeout(2000)
                elif action == "look":
                    pass
                else:
                    notes.append(f"unknown action '{action}'")
            shots += 1
            shot = folder / f"screen-{shots:03d}.png"
            tab.screenshot(path=str(shot))
            bottom = tab.evaluate("innerHeight + scrollY >= document.documentElement.scrollHeight - 4")
            reply = "".join(f"NOTE   {note}\n" for note in notes) + f"SCREEN {shot}{'   (bottom of this page)' if bottom else ''}"
            connection.sendall(reply.encode())
            connection.close()


def main():
    if sys.argv[1] == "--serve":
        serve(sys.argv[2])
        return
    session, actions = sys.argv[1], sys.argv[2:]
    folder = HERE / session
    folder.mkdir(parents=True, exist_ok=True)
    if actions[:1] == ["--page"]:
        (folder / "page.txt").write_text(str(Path(actions[1]).resolve()))
        actions = actions[2:]
    if not (folder / "page.txt").exists():
        sys.exit("Start the session with --page PATH_TO_PAGE.html")
    address = str(folder / "socket")
    for attempt in range(60):
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(address)
            break
        except OSError:
            if attempt == 0:
                subprocess.Popen([sys.executable, __file__, "--serve", session], stdout=open(folder / "server.log", "a"),
                                 stderr=subprocess.STDOUT, start_new_session=True)
            time.sleep(0.5)
    else:
        sys.exit("could not reach the phone; see " + str(folder / "server.log"))
    client.sendall(json.dumps(actions).encode())
    chunks = []
    while True:
        chunk = client.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
    print(b"".join(chunks).decode())


if __name__ == "__main__":
    main()
