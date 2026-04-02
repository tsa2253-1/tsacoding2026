"use strict";

/* ── Dark Mode ──────────────────────────────────────────────── */
(function () {
  const html   = document.documentElement;
  const toggle = document.getElementById("darkToggle");
  const icon   = document.getElementById("darkIcon");
  const saved  = localStorage.getItem("stempath-theme");
  const sys    = window.matchMedia("(prefers-color-scheme: dark)").matches;

  apply(saved === "dark" || (!saved && sys));

  if (toggle) toggle.addEventListener("click", () => {
    const dark = html.dataset.theme !== "dark";
    apply(dark);
    localStorage.setItem("stempath-theme", dark ? "dark" : "light");
  });

  function apply(dark) {
    html.dataset.theme = dark ? "dark" : "light";
    if (icon) {
      icon.className = dark ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
    if (toggle) toggle.setAttribute("aria-pressed", String(dark));
  }
})();

/* ── Mobile Nav ─────────────────────────────────────────────── */
(function () {
  const tog  = document.getElementById("navToggle");
  const menu = document.getElementById("navLinks");
  if (!tog || !menu) return;
  tog.addEventListener("click", () => {
    const open = menu.classList.toggle("open");
    tog.setAttribute("aria-expanded", String(open));
  });
})();

/* ── Score Bars (Intersection Observer) ────────────────────── */
(function () {
  const bars = document.querySelectorAll(".score-fill[data-score]");
  if (!bars.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        setTimeout(() => { e.target.style.width = e.target.dataset.score + "%"; }, 80);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  bars.forEach(b => { b.style.width = "0%"; obs.observe(b); });
})();

/* ── Card Filter + Search ───────────────────────────────────── */
(function () {
  const grid    = document.getElementById("cardGrid");
  const search  = document.getElementById("searchInput");
  const chips   = document.querySelectorAll(".chip[data-tag]");
  const clearBtn = document.getElementById("clearChips");
  const noRes   = document.getElementById("noResults");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll("[data-tags]"));
  let activeTag = null, query = "";

  function refresh() {
    let vis = 0;
    cards.forEach(card => {
      const tags  = (card.dataset.tags || "").toLowerCase();
      const title = (card.dataset.title || "").toLowerCase();
      const skills= (card.dataset.skills || "").toLowerCase();
      const hay   = `${tags} ${title} ${skills}`;
      const show  = (!activeTag || tags.includes(activeTag)) &&
                    (!query    || hay.includes(query));
      card.style.display = show ? "" : "none";
      if (show) vis++;
    });
    if (noRes) noRes.style.display = vis === 0 ? "" : "none";
  }

  chips.forEach(c => c.addEventListener("click", () => {
    const tag = c.dataset.tag;
    if (activeTag === tag) {
      activeTag = null;
      chips.forEach(x => { x.classList.remove("active"); x.setAttribute("aria-pressed","false"); });
    } else {
      chips.forEach(x => { x.classList.remove("active"); x.setAttribute("aria-pressed","false"); });
      activeTag = tag;
      c.classList.add("active");
      c.setAttribute("aria-pressed","true");
    }
    refresh();
  }));

  if (clearBtn) clearBtn.addEventListener("click", () => {
    activeTag = null; query = "";
    chips.forEach(x => { x.classList.remove("active"); x.setAttribute("aria-pressed","false"); });
    if (search) search.value = "";
    refresh();
  });

  if (search) {
    let timer;
    search.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => { query = search.value.trim().toLowerCase(); refresh(); }, 200);
    });
  }
})();

/* ── Roadmap Checklist ──────────────────────────────────────── */
(function () {
  document.querySelectorAll(".checklist li").forEach(li => {
    li.setAttribute("role", "checkbox");
    li.setAttribute("aria-checked", "false");
    li.setAttribute("tabindex", "0");

    function toggle() {
      const done = li.classList.toggle("done");
      const ring = li.querySelector(".check-ring");
      if (ring) ring.innerHTML = done ? '<i class="fa-solid fa-check"></i>' : "";
      li.setAttribute("aria-checked", String(done));
    }

    li.addEventListener("click", toggle);
    li.addEventListener("keydown", e => {
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggle(); }
    });
  });
})();

/* ── Quiz helpers: select all / clear ──────────────────────── */
(function () {
  document.querySelectorAll("[data-quiz-action]").forEach(btn => {
    btn.addEventListener("click", () => {
      const section = btn.closest(".quiz-section");
      if (!section) return;
      const all = btn.dataset.quizAction === "all";
      section.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = all);
    });
  });
})();

/* ── Tooltips (Bootstrap) ───────────────────────────────────── */
(function () {
  if (typeof bootstrap === "undefined") return;
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
    .forEach(el => new bootstrap.Tooltip(el));
})();

/* ── Smooth anchor nav ──────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener("click", e => {
    const t = document.querySelector(a.getAttribute("href"));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: "smooth", block: "start" }); }
  });
});
