/**
 * Shelter — interactive polish + easter eggs
 */
(function () {
  "use strict";

  const QUIET_KEY = "shelter-quiet-room";
  const toastRoot = () => document.getElementById("toast-root");

  function showToast(message, kind) {
    const root = toastRoot();
    if (!root || !message) return;
    const el = document.createElement("div");
    el.className = "toast toast-" + (kind || "info");
    el.setAttribute("role", "status");
    el.textContent = message;
    root.appendChild(el);
    requestAnimationFrame(() => el.classList.add("is-visible"));
    setTimeout(() => {
      el.classList.remove("is-visible");
      setTimeout(() => el.remove(), 280);
    }, 3200);
  }

  /* —— Django messages → toasts —— */
  function promoteMessages() {
    document.querySelectorAll(".messages .message").forEach((msg) => {
      const kind = msg.classList.contains("message-success")
        ? "success"
        : msg.classList.contains("message-info")
          ? "info"
          : "info";
      showToast(msg.textContent.trim(), kind);
      msg.closest(".messages")?.classList.add("is-toastified");
    });
  }

  /* —— Shelf add/remove micro-feedback —— */
  function bindShelfForms() {
    document.querySelectorAll("form[action*='your-shelter/']").forEach((form) => {
      form.addEventListener("submit", () => {
        const isRemove = form.action.includes("/remove/");
        const card = form.closest(".book-card, .book-detail");
        if (card) {
          card.classList.add(isRemove ? "shelf-leaving" : "shelf-saving");
        }
        showToast(
          isRemove ? "Removing from Your Shelter…" : "Saving to Your Shelter…",
          isRemove ? "info" : "success"
        );
      });
    });
  }

  /* —— Card tilt —— */
  function bindTilt() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.matchMedia("(pointer: coarse)").matches) return;

    document.querySelectorAll(".book-card").forEach((card) => {
      const cover = card.querySelector(".book-card-cover");
      if (!cover) return;
      card.classList.add("has-tilt");

      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        const rx = (0.5 - y) * 10;
        const ry = (x - 0.5) * 12;
        cover.style.transform = `perspective(700px) rotateX(${rx}deg) rotateY(${ry}deg) scale(1.02)`;
      });
      card.addEventListener("mouseleave", () => {
        cover.style.transform = "";
      });
    });
  }

  /* —— Quiet room (5× brand click) —— */
  function applyQuietRoom(on, announce) {
    document.documentElement.classList.toggle("quiet-room", on);
    try {
      localStorage.setItem(QUIET_KEY, on ? "1" : "0");
    } catch (_) {}
    if (announce) {
      showToast(
        on ? "You found the quiet room." : "Back to the open catalog.",
        "success"
      );
    }
  }

  function bindBrandEaster() {
    const brand = document.querySelector(".brand");
    if (!brand) return;
    let clicks = 0;
    let timer = null;
    try {
      if (localStorage.getItem(QUIET_KEY) === "1") applyQuietRoom(true, false);
    } catch (_) {}

    brand.addEventListener("click", (e) => {
      // Allow normal navigation on first intentional click path, but count multi-clicks
      clicks += 1;
      clearTimeout(timer);
      timer = setTimeout(() => {
        clicks = 0;
      }, 900);
      if (clicks >= 5) {
        e.preventDefault();
        clicks = 0;
        const next = !document.documentElement.classList.contains("quiet-room");
        applyQuietRoom(next, true);
      }
    });
  }

  /* —— Quiet hours (22:00–06:00 local) —— */
  function applyQuietHours() {
    const hour = new Date().getHours();
    const quiet = hour >= 22 || hour < 6;
    document.documentElement.classList.toggle("quiet-hours", quiet);
    const kicker = document.querySelector(".hero-kicker");
    if (kicker && quiet && !kicker.dataset.quietSet) {
      kicker.dataset.quietSet = "1";
      kicker.dataset.original = kicker.textContent;
      kicker.textContent = "Quiet hours · the catalog still watches";
    }
  }

  /* —— Hero orbs sequence G-T-M-S —— */
  function bindOrbs() {
    const orbs = document.querySelectorAll(".hero-orbs .orb");
    if (!orbs.length) return;
    const expected = ["G", "T", "M", "S"];
    let progress = 0;

    orbs.forEach((orb) => {
      orb.setAttribute("role", "button");
      orb.setAttribute("tabindex", "0");
      orb.removeAttribute("aria-hidden");
      const letter = (orb.dataset.letter || orb.textContent || "").trim().toUpperCase();
      orb.dataset.letter = letter;

      const activate = () => {
        if (letter === expected[progress]) {
          progress += 1;
          orb.classList.add("orb-lit");
          if (progress === expected.length) {
            progress = 0;
            unlockHiddenShelf();
            orbs.forEach((o) => o.classList.remove("orb-lit"));
          }
        } else {
          progress = letter === expected[0] ? 1 : 0;
          orbs.forEach((o) => o.classList.remove("orb-lit"));
          if (progress === 1) orb.classList.add("orb-lit");
        }
      };

      orb.addEventListener("click", (e) => {
        e.preventDefault();
        activate();
      });
      orb.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
    });
  }

  function unlockHiddenShelf() {
    let panel = document.getElementById("hidden-shelf");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "hidden-shelf";
      panel.className = "hidden-shelf is-open";
      panel.innerHTML = `
        <div class="hidden-shelf-inner">
          <p class="hero-kicker">Hidden shelf</p>
          <h2>The Quiet Room</h2>
          <p class="lede">A title only the orbs reveal — not in the public catalog, not in seed data.</p>
          <p class="meta">The Keeper · Hidden · Easter egg</p>
        </div>`;
      const hero = document.querySelector(".hero");
      if (hero && hero.parentNode) {
        hero.parentNode.insertBefore(panel, hero.nextSibling);
      } else {
        document.querySelector("main")?.prepend(panel);
      }
    } else {
      panel.classList.add("is-open");
    }
    showToast("Hidden shelf unlocked.", "success");
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  /* —— Tonight's pick —— */
  function bindTonightPick() {
    const btn = document.getElementById("tonight-pick-btn");
    const stage = document.getElementById("tonight-pick-stage");
    if (!btn || !stage) return;

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Drawing…";
      stage.classList.remove("is-revealed");
      stage.classList.add("is-flipping");
      try {
        const res = await fetch("/api/books/pick/");
        if (!res.ok) throw new Error("empty");
        const book = await res.json();
        setTimeout(() => {
          stage.innerHTML = renderPickCard(book);
          stage.classList.remove("is-flipping");
          stage.classList.add("is-revealed");
          btn.disabled = false;
          btn.textContent = "Draw again";
        }, 420);
      } catch (_) {
        stage.innerHTML = `<p class="empty">No books to pick yet.</p>`;
        stage.classList.remove("is-flipping");
        btn.disabled = false;
        btn.textContent = "Try again";
      }
    });
  }

  function renderPickCard(book) {
    const authors = (book.authors || []).join(", ") || "Unknown author";
    const cover = book.cover_url
      ? `<img src="${escapeAttr(book.cover_url)}" alt="Cover of ${escapeAttr(book.title)}" width="200" height="300">`
      : `<span class="cover-initial" aria-hidden="true">${escapeHtml((book.title || "?")[0])}</span>`;
    return `
      <a class="tonight-card" href="/books/${escapeAttr(book.slug)}/">
        <div class="tonight-cover ${book.cover_url ? "has-image" : ""}">${cover}</div>
        <div>
          <p class="meta">Tonight’s pick</p>
          <h3>${escapeHtml(book.title)}</h3>
          <p class="meta">${escapeHtml(authors)}</p>
          ${book.category ? `<span class="category-pill">${escapeHtml(book.category)}</span>` : ""}
        </div>
      </a>`;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  /* —— Live search on book list —— */
  function bindLiveSearch() {
    const form = document.querySelector("form.filters");
    const grid = document.getElementById("book-grid-live");
    const empty = document.getElementById("book-grid-empty");
    const search = form?.querySelector('input[name="q"]');
    if (!form || !grid || !search) return;

    let timer = null;
    let lastQ = search.value;

    const run = async () => {
      const q = search.value.trim();
      const category = form.querySelector('select[name="category"]')?.value || "";
      const sort = form.querySelector('select[name="sort"]')?.value || "newest";
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      // API sort is limited; we only use q for live filter and keep server for full sort on submit
      try {
        const res = await fetch("/api/books/?" + params.toString());
        if (!res.ok) return;
        const data = await res.json();
        let results = data.results || [];
        if (category) {
          results = results.filter(
            (b) => String(b.category_slug || "").toLowerCase() === category
          );
        }
        if (sort === "title") {
          results = [...results].sort((a, b) => a.title.localeCompare(b.title));
        } else if (sort === "title_desc") {
          results = [...results].sort((a, b) => b.title.localeCompare(a.title));
        }
        paintLiveGrid(grid, results);
        if (empty) empty.hidden = results.length > 0;
        grid.hidden = results.length === 0;
        const pager = document.getElementById("book-pagination");
        if (pager) pager.hidden = true;
      } catch (_) {
        /* fall back to form submit */
      }
    };

    const schedule = () => {
      clearTimeout(timer);
      timer = setTimeout(run, 280);
    };

    search.addEventListener("input", () => {
      if (search.value === lastQ) return;
      lastQ = search.value;
      schedule();
    });
    form.querySelector('select[name="category"]')?.addEventListener("change", schedule);
    form.querySelector('select[name="sort"]')?.addEventListener("change", schedule);
  }

  function paintLiveGrid(grid, books) {
    if (!books.length) {
      grid.innerHTML = "";
      return;
    }
    grid.innerHTML = books
      .map((book) => {
        const authors = (book.authors || []).join(", ") || "Unknown author";
        const cover = book.cover_url
          ? `<img src="${escapeAttr(book.cover_url)}" alt="Cover of ${escapeAttr(book.title)}" width="400" height="600" loading="lazy">`
          : `<span class="cover-initial" aria-hidden="true">${escapeHtml((book.title || "?")[0])}</span>`;
        return `<li class="book-card has-tilt">
          <a class="card-link" href="/books/${escapeAttr(book.slug)}/">
            <div class="book-card-cover ${book.cover_url ? "has-image" : ""}">${cover}</div>
            <div class="book-card-body">
              <h3>${escapeHtml(book.title)}</h3>
              ${book.subtitle ? `<p class="subtitle">${escapeHtml(book.subtitle)}</p>` : ""}
              <p class="meta">${escapeHtml(authors)}</p>
              <div class="card-footer">
                <span class="category-pill">${escapeHtml(book.category || "")}</span>
                ${book.is_featured ? '<span class="badge">Featured</span>' : ""}
              </div>
            </div>
          </a>
        </li>`;
      })
      .join("");
    bindTilt();
  }

  /* —— Reading mode —— */
  function bindReadingMode() {
    const article = document.querySelector(".book-detail");
    const toggle = document.getElementById("reading-mode-toggle");
    const bar = document.getElementById("read-progress");
    if (!article || !toggle) return;

    const KEY = "shelter-reading-mode";
    try {
      if (localStorage.getItem(KEY) === "1") {
        document.documentElement.classList.add("reading-mode");
        toggle.setAttribute("aria-pressed", "true");
        toggle.textContent = "Exit reading mode";
      }
    } catch (_) {}

    toggle.addEventListener("click", () => {
      const on = document.documentElement.classList.toggle("reading-mode");
      toggle.setAttribute("aria-pressed", on ? "true" : "false");
      toggle.textContent = on ? "Exit reading mode" : "Reading mode";
      try {
        localStorage.setItem(KEY, on ? "1" : "0");
      } catch (_) {}
    });

    if (bar) {
      const onScroll = () => {
        const desc = article.querySelector(".description");
        if (!desc) return;
        const rect = desc.getBoundingClientRect();
        const total = desc.offsetHeight - window.innerHeight * 0.35;
        const scrolled = Math.min(
          Math.max(-rect.top + 80, 0),
          Math.max(total, 1)
        );
        const pct = Math.min(100, Math.round((scrolled / Math.max(total, 1)) * 100));
        bar.style.width = pct + "%";
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
  }

  /* —— Keyboard shortcuts —— */
  function bindKeys() {
    let gPending = false;
    let gTimer = null;

    document.addEventListener("keydown", (e) => {
      const tag = (e.target && e.target.tagName) || "";
      const typing =
        /^(INPUT|TEXTAREA|SELECT)$/.test(tag) || e.target?.isContentEditable;
      if (typing) return;

      if (e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const search = document.querySelector('input[name="q"][type="search"], input[name="q"]');
        if (search) {
          e.preventDefault();
          search.focus();
          search.select();
          showToast("Search focused · press Esc to leave", "info");
        }
        return;
      }

      if (e.key === "Escape") {
        document.getElementById("stack-modal")?.close();
        return;
      }

      if (e.key === "g" || e.key === "G") {
        gPending = true;
        clearTimeout(gTimer);
        gTimer = setTimeout(() => {
          gPending = false;
        }, 700);
        return;
      }
      if (gPending) {
        gPending = false;
        clearTimeout(gTimer);
        if (e.key === "h" || e.key === "H") {
          e.preventDefault();
          window.location.href = "/";
        } else if (e.key === "b" || e.key === "B") {
          e.preventDefault();
          window.location.href = "/books/";
        } else if (e.key === "s" || e.key === "S") {
          e.preventDefault();
          window.location.href = "/your-shelter/";
        }
      }
    });
  }

  /* —— Footer double-click stack modal —— */
  function bindStackModal() {
    const trigger = document.getElementById("stack-easter");
    const modal = document.getElementById("stack-modal");
    if (!trigger || !modal) return;

    trigger.addEventListener("dblclick", (e) => {
      e.preventDefault();
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
      showToast("Stack card unlocked.", "success");
    });
    modal.querySelector("[data-close-modal]")?.addEventListener("click", () => {
      if (typeof modal.close === "function") modal.close();
      else modal.removeAttribute("open");
    });
  }

  /* —— Console signature —— */
  function consoleHello() {
    const style =
      "color:#1e4d42;font-family:Georgia,serif;font-size:14px;font-weight:600";
    console.log(
      "%cWelcome to Shelter.\nBuilt with Django · not a SPA · still has secrets.",
      style
    );
    console.log(
      "%cHints: click Shelter. five times · orbs G→T→M→S · double-click the disclaimer · GET /api/books/?easter=true · keys: /  g h  g b",
      "color:#6b756f;font-size:11px"
    );
  }

  document.addEventListener("DOMContentLoaded", () => {
    promoteMessages();
    bindShelfForms();
    bindTilt();
    bindBrandEaster();
    applyQuietHours();
    bindOrbs();
    bindTonightPick();
    bindLiveSearch();
    bindReadingMode();
    bindKeys();
    bindStackModal();
    consoleHello();
  });
})();
