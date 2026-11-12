"""Ready-made tasks. Each one reads or posts a small, bounded amount and stops on verification pages.

Ported from browser-own-profile (same page logic, first real runs 12-13/10/2026); the engine is now agent-browser.
"""

import os
import time
from urllib.parse import quote

from . import parse
from .guard import LIMITS, SITES, Blocked, find, fold


def _cap(n, key):
    return max(1, min(int(n), LIMITS[key]))


# Product tours (react-joyride) cover the page after an upload (seen 12/11/2026 on TikTok Studio:
# "New editing features added ... Got it"). The grey overlay comes first, the box with the button a few
# seconds later, and a JS .click() did not close it: wait for the button, press it with a real click,
# check the overlay is gone. Only buttons INSIDE the tour box (id react-joyride-step-N) are pressed.
_TOUR_JS = r"""(() => {
  const ok = /^(got it|ok|okay|skip|close|done|đã hiểu|bỏ qua|đóng|xong)$/i;
  document.querySelectorAll('[data-bok-tour]').forEach(x => x.removeAttribute('data-bok-tour'));
  const overlay = !!document.querySelector('.react-joyride__overlay, .react-joyride__spotlight');
  const btns = [...document.querySelectorAll('[id^="react-joyride-step"] button, .react-joyride__tooltip button')]
    .filter(x => ok.test((x.innerText || x.getAttribute('aria-label') || '').trim()));
  const b = btns.find(x => !/^close$|^đóng$/i.test((x.innerText || x.getAttribute('aria-label') || '').trim())) || btns[0];
  if (!b) return {overlay, name: ''};
  b.setAttribute('data-bok-tour', '1');
  return {overlay, name: (b.innerText || b.getAttribute('aria-label')).trim()};
})()"""


def _dismiss_tours(kit, wait=12, quiet=3):
    """Close page tours. Returns once no tour is showing (after at least `quiet` s), at most `wait` s."""
    start = time.time()
    while time.time() - start < wait:
        state = kit.browser.eval(_TOUR_JS) or {}
        if state.get("name"):
            kit.note("đóng", f"bảng hướng dẫn của trang ('{state['name']}')")
            try:
                kit.browser._run("click", '[data-bok-tour="1"]')
            except Exception:
                pass
            time.sleep(1.5)
            continue
        if not state.get("overlay") and time.time() - start >= quiet:
            return
        time.sleep(1)
    if (kit.browser.eval(_TOUR_JS) or {}).get("overlay"):
        raise RuntimeError("bảng hướng dẫn của trang vẫn che màn hình, không đóng được")


def shopee_search(kit, keyword, min_price=None, max_price=None, limit=10):
    """Top-selling Shopee products for a keyword (read only). Needs `login --site shopee` first."""
    limit = _cap(limit, "shopee_products")
    url = f"https://shopee.vn/search?keyword={quote(keyword)}&sortBy=sales&order=desc"
    if min_price:
        url += f"&minPrice={int(min_price)}"
    if max_price:
        url += f"&maxPrice={int(max_price)}"
    kit.open(url, settle=5)
    text = kit.read_text()
    return parse.shopee_products(text, limit), text


def tiktok_comments(kit, video_url, limit=30):
    """Top-level comments of ONE TikTok video (read only). Works best with main=True (your own Chrome)."""
    limit = _cap(limit, "tiktok_comments")
    if not video_url.startswith("https://www.tiktok.com/"):
        raise ValueError("cần link video TikTok dạng https://www.tiktok.com/@kenh/video/...")
    kit.open(video_url, settle=4)
    snap = kit.snapshot()
    tabs = find(snap, kind="click", names=("Comments", "Bình luận"))
    tabs = [e for e in tabs if e.get("role") in ("button", "tab")]
    if tabs:  # switches the side panel only; nothing is sent
        kit.note("bấm", f"tab '{tabs[0]['name']}' (chỉ đổi khung hiển thị)")
        kit.browser.click(tabs[0]["id"], expect_name=tabs[0]["name"])
        time.sleep(3)
    text = kit.read_text()
    if not any(parse.COMMENTS_HEADER.match(line.strip()) for line in text.splitlines()):
        # Seen 12/10/2026: with a fresh separate profile TikTok shows an empty panel (or a slider check);
        # the person's long-used main Chrome got the comments.
        kit.note("không có bình luận", "khung Comments trống")
        raise Blocked("TikTok không tải bình luận cho Chrome này (hay gặp ở Chrome riêng). "
                      "Cách cuối: --main (Chrome chính, cần bật remote debugging và bấm Allow).")
    rows = parse.tiktok_comments(text, limit)
    for _ in range(LIMITS["scroll_rounds"]):
        if len(rows) >= limit:
            break
        snap = kit.snapshot()
        # Scroll over an element that sits inside the comment list (a reply link), not the video area.
        anchors = [e for e in snap["elements"] if parse.VIEW_REPLIES.match(e.get("name", ""))
                   or parse.REPLY.match(e.get("name", ""))]
        if not anchors:
            break
        kit.scroll(anchors[-1], times=5)
        text = kit.read_text()
        more = parse.tiktok_comments(text, limit)
        if len(more) <= len(rows):
            break
        rows = more
    return rows, text


def tiktok_studio_post(kit, video_path, caption, upload_timeout=300):
    """Upload YOUR video in TikTok Studio, fill the caption, ask before pressing Post. One post per run."""
    if not os.path.isfile(video_path):
        raise ValueError(f"không thấy file video: {video_path}")
    kit.open(SITES["tiktok-studio"]["url"], settle=4)
    # Seen 12/11/2026: the file input can take longer than the settle time to appear.
    inputs = kit.wait_for(lambda s: find(s, kind="upload") or None, timeout=20)
    if not inputs:
        raise Blocked("không thấy ô chọn video trên TikTok Studio (chưa đăng nhập hoặc trang đã đổi)")
    kit.upload(inputs[0], os.path.abspath(video_path))

    # TikTok pre-fills the description with the file name (seen 12/10/2026: a role=combobox editor named
    # 'video-thu' for video-thu.mp4); the location picker is also a combobox, so match on that name first.
    stem = fold(os.path.splitext(os.path.basename(video_path))[0])

    def caption_box(s):
        boxes = [e for e in find(s, kind="fill") if e.get("role") in ("textbox", "combobox")]
        named = [e for e in boxes if stem and stem in (fold(e.get("name", "")), fold(e.get("value", "")))]
        if named:
            return named[0]
        plain = [e for e in boxes if e.get("role") == "textbox" and "search" not in fold(e.get("name", ""))]
        return plain[0] if plain else None

    box = kit.wait_for(caption_box, timeout=60)
    if box is None:
        raise RuntimeError("không thấy ô mô tả sau khi tải video")
    _dismiss_tours(kit)  # the tour pops up a few seconds after the editor appears
    kit.fill(box, caption)
    if caption.strip()[:20] not in kit.read_text():
        raise RuntimeError("điền mô tả không thành công (ô mô tả vẫn chưa có nội dung mới)")

    def post_button(s):
        ready = find(s, kind="click", names=("Post", "Đăng"), enabled=True)
        return ready[0] if ready else None

    button = kit.wait_for(post_button, timeout=upload_timeout, every=5)
    if button is None:
        raise RuntimeError("nút Post chưa bật (video chưa tải xong?)")
    _dismiss_tours(kit)
    kit.click(button, confirm_with=f"đăng video {os.path.basename(video_path)} lên TikTok")
    time.sleep(3)

    def anyway_button(s):
        ready = find(s, kind="click", names=("Post anyway", "Post now", "Đăng ngay", "Vẫn đăng", "Tiếp tục đăng"), enabled=True)
        return ready[0] if ready else None

    try:
        anyway = kit.wait_for(anyway_button, timeout=10, every=2)
        if anyway:
            kit.note("bấm", f"'{anyway['name']}' (xác nhận đăng)")
            kit.browser.click(anyway["id"], expect_name=anyway["name"])
            time.sleep(5)
    except Exception:
        pass

    def success_page(s):
        txt = s.get("text", "").lower()
        url = s.get("url", "")
        if "content" in url or any(k in txt for k in ("manage your posts", "quản lý bài viết", "your video has been published", "video của bạn đã được xuất bản", "upload another video")):
            return True
        return None

    try:
        kit.wait_for(success_page, timeout=30, every=3)
    except Exception:
        pass

    return kit.read_text()[:500]


def facebook_post(kit, text, image=None):
    """Post text (and optionally one image) on YOUR Facebook feed, asking before pressing Post. One post per
    run."""
    if image is not None and not os.path.isfile(image):
        raise ValueError(f"không thấy file ảnh: {image}")
    kit.open(SITES["facebook"]["url"], settle=5)
    snap = kit.snapshot()
    openers = find(snap, kind="click", contains=("what's on your mind", "bạn đang nghĩ gì"))
    if not openers:
        raise Blocked("không thấy ô 'Bạn đang nghĩ gì?' (chưa đăng nhập Facebook hoặc trang đã đổi)")
    kit.note("bấm", f"'{openers[0]['name'][:40]}' (mở khung soạn bài)")
    kit.browser.click(openers[0]["id"], expect_name=openers[0]["name"])  # opens the composer only
    time.sleep(2)

    def composer(s):
        boxes = [e for e in find(s, kind="fill") if e.get("role") == "textbox"
                 and "search" not in fold(e.get("name", "")) and "tìm kiếm" not in fold(e.get("name", ""))]
        return boxes[-1] if boxes else None

    box = kit.wait_for(composer, timeout=15)
    if box is None:
        raise RuntimeError("không thấy ô soạn bài")
    kit.fill(box, text)
    time.sleep(1)
    if image is not None:
        snap = kit.snapshot()
        inputs = find(snap, kind="upload")
        if not inputs:  # the composer's file input appears after its Photo/video button
            pickers = find(snap, kind="click", contains=("photo/video", "ảnh/video"))
            if not pickers:
                raise RuntimeError("không thấy nút Ảnh/video trong khung soạn bài")
            kit.note("bấm", f"'{pickers[-1]['name']}' (mở chỗ thêm ảnh)")
            kit.browser.click(pickers[-1]["id"], expect_name=pickers[-1]["name"])
            time.sleep(2)
            inputs = find(kit.snapshot(), kind="upload")
        if not inputs:
            raise RuntimeError("không thấy ô chọn ảnh")
        # The last file input belongs to the open composer; the first one opens a second composer.
        kit.upload(inputs[-1], os.path.abspath(image))
        attached = kit.wait_for(lambda s: find(s, kind="click", contains=("remove post attachment",
                                                                         "gỡ tệp đính kèm")), timeout=30)
        if not attached:
            raise RuntimeError("ảnh chưa gắn vào bài (không thấy nút gỡ ảnh)")
        time.sleep(3)  # let the preview finish uploading

    def post_button(s):
        ready = find(s, kind="click", names=("Post", "Đăng"), enabled=True)
        return ready[-1] if ready else None

    button = kit.wait_for(post_button, timeout=30)
    if button is None:
        raise RuntimeError("không thấy nút Đăng")
    what = f"'{text[:60]}'" + (f" kèm ảnh {os.path.basename(image)}" if image else "")
    kit.click(button, confirm_with=f"đăng bài lên Facebook: {what}")
    time.sleep(4)
    return "đã bấm Đăng"


def instagram_post(kit, media_path, caption):
    """Post an image or video to YOUR Instagram feed, asking before pressing Share. One post per run."""
    if not os.path.isfile(media_path):
        raise ValueError(f"không thấy file phương tiện: {media_path}")
    kit.open(SITES["instagram"]["url"], settle=5)
    snap = kit.snapshot()
    openers = find(snap, kind="click", names=("Create", "Tạo", "New post"))
    if not openers:
        openers = find(snap, kind="click", contains=("create", "tạo"))
    if not openers:
        raise Blocked("không thấy nút 'Tạo' (chưa đăng nhập Instagram hoặc trang đã đổi)")
    kit.note("bấm", f"'{openers[0]['name']}' (mở khung tạo bài)")
    kit.browser.click(openers[0]["id"], expect_name=openers[0]["name"])
    time.sleep(2)

    inputs = find(kit.snapshot(), kind="upload")
    if not inputs:
        subposts = find(kit.snapshot(), kind="click", names=("Post", "Bài viết"))
        if subposts:
            kit.browser.click(subposts[0]["id"], expect_name=subposts[0]["name"])
            time.sleep(2)
            inputs = find(kit.snapshot(), kind="upload")
    if not inputs:
        raise RuntimeError("không thấy ô chọn file trên Instagram")
    kit.upload(inputs[-1], os.path.abspath(media_path))
    time.sleep(3)

    def next_btn(s):
        ready = find(s, kind="click", names=("Next", "Tiếp"), enabled=True)
        return ready[-1] if ready else None

    btn = kit.wait_for(next_btn, timeout=20)
    if btn:
        kit.note("bấm", f"'{btn['name']}' (bỏ qua cắt ảnh)")
        kit.browser.click(btn["id"], expect_name=btn["name"])
        time.sleep(2)

    btn2 = kit.wait_for(next_btn, timeout=20)
    if btn2:
        kit.note("bấm", f"'{btn2['name']}' (bỏ qua bộ lọc)")
        kit.browser.click(btn2["id"], expect_name=btn2["name"])
        time.sleep(2)

    def cap_box(s):
        boxes = [e for e in find(s, kind="fill") if e.get("role") in ("textbox", "combobox")]
        return boxes[-1] if boxes else None

    box = kit.wait_for(cap_box, timeout=15)
    if box:
        kit.fill(box, caption)
        time.sleep(1)

    def share_btn(s):
        ready = find(s, kind="click", names=("Share", "Chia sẻ"), enabled=True)
        return ready[-1] if ready else None

    share = kit.wait_for(share_btn, timeout=20)
    if not share:
        raise RuntimeError("không thấy nút Chia sẻ trên Instagram")
    kit.click(share, confirm_with=f"đăng bài lên Instagram: {os.path.basename(media_path)}")
    time.sleep(6)
    return "đã bấm Chia sẻ trên Instagram"
