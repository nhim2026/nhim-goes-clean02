/* Ember Tarot film — shared deterministic helpers (no Math.random, no clocks). */
(function () {
  const EF = {};

  // Seeded PRNG (mulberry32)
  EF.rng = function (seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  // Drive a render(t) function from a timeline (t = local seconds).
  EF.drive = function (tl, duration, fn, at) {
    const o = { t: 0 };
    tl.fromTo(o, { t: 0 }, {
      t: duration, duration: duration, ease: "none",
      onUpdate: function () { fn(o.t); },
    }, at || 0);
    fn(0);
  };

  // ---------- Mascot cat (SVG) ----------
  EF.catSVG = function () {
    return `
<svg class="cat-svg" viewBox="0 0 320 380" xmlns="http://www.w3.org/2000/svg" overflow="visible">
  <g class="c-tail"><path d="M232 300 C300 296 312 230 286 196" fill="none" stroke="#F6EFDF" stroke-width="36" stroke-linecap="round"/><path d="M232 300 C300 296 312 230 286 196" fill="none" stroke="#24304F" stroke-width="24" stroke-linecap="round"/>
    <path d="M286 170 l6 14 l15 2 l-11 10 l3 15 l-13 -8 l-13 8 l3 -15 l-11 -10 l15 -2z" fill="#E8C27A"/></g>
  <g class="c-body">
    <ellipse cx="160" cy="292" rx="96" ry="72" fill="#24304F" stroke="#F6EFDF" stroke-width="6"/>
    <ellipse cx="160" cy="306" rx="56" ry="48" fill="#F6EFDF"/>
    <ellipse cx="116" cy="356" rx="30" ry="18" fill="#F6EFDF"/>
    <ellipse cx="204" cy="356" rx="30" ry="18" fill="#F6EFDF"/>
  </g>
  <g class="c-armL"><ellipse cx="86" cy="286" rx="26" ry="34" fill="#24304F" stroke="#F6EFDF" stroke-width="6"/><ellipse cx="80" cy="304" rx="16" ry="12" fill="#F6EFDF"/></g>
  <g class="c-armR"><ellipse cx="234" cy="286" rx="26" ry="34" fill="#24304F" stroke="#F6EFDF" stroke-width="6"/><ellipse cx="240" cy="304" rx="16" ry="12" fill="#F6EFDF"/></g>
  <g class="c-head">
    <g stroke="#F6EFDF" stroke-width="12" stroke-linejoin="round" fill="#F6EFDF"><path d="M66 128 L84 30 L146 92Z"/><path d="M254 128 L236 30 L174 92Z"/><ellipse cx="160" cy="150" rx="108" ry="90"/></g>
    <path d="M66 128 L84 30 L146 92Z" fill="#24304F"/><path d="M84 66 L90 46 L120 84Z" fill="#F2B8B5"/>
    <path d="M254 128 L236 30 L174 92Z" fill="#24304F"/><path d="M236 66 L230 46 L200 84Z" fill="#F2B8B5"/>
    <ellipse cx="160" cy="150" rx="108" ry="90" fill="#24304F"/>
    <path d="M168 78 A18 18 0 1 0 168 106 A14 14 0 1 1 168 78Z" fill="#E8C27A"/>
    <ellipse cx="160" cy="190" rx="48" ry="32" fill="#F6EFDF"/>
    <g class="c-eyes">
      <g class="c-eye"><ellipse cx="116" cy="148" rx="24" ry="27" fill="#F6EFDF"/><circle class="c-pupil" cx="119" cy="152" r="15" fill="#1A2238"/><circle cx="125" cy="144" r="5.5" fill="#fff"/><circle cx="114" cy="158" r="2.5" fill="#fff"/></g>
      <g class="c-eye"><ellipse cx="204" cy="148" rx="24" ry="27" fill="#F6EFDF"/><circle class="c-pupil" cx="207" cy="152" r="15" fill="#1A2238"/><circle cx="213" cy="144" r="5.5" fill="#fff"/><circle cx="202" cy="158" r="2.5" fill="#fff"/></g>
    </g>
    <path class="c-wink" d="M182 150 Q204 132 226 150" fill="none" stroke="#F6EFDF" stroke-width="7" stroke-linecap="round" opacity="0"/>
    <ellipse cx="86" cy="188" rx="17" ry="10" fill="#F2B8B5" opacity=".85"/>
    <ellipse cx="234" cy="188" rx="17" ry="10" fill="#F2B8B5" opacity=".85"/>
    <path d="M152 176 L168 176 L160 186Z" fill="#E59A97"/>
    <path class="c-mouth-closed" d="M146 190 q7 9 14 0 q7 9 14 0" fill="none" stroke="#24304F" stroke-width="4" stroke-linecap="round"/>
    <g class="c-mouth-open" opacity="0"><ellipse cx="160" cy="198" rx="13" ry="11" fill="#5A2232"/><ellipse cx="160" cy="203" rx="8" ry="5" fill="#E59A97"/></g>
    <g stroke="#F6EFDF" stroke-width="3" stroke-linecap="round" opacity=".8">
      <line x1="100" y1="196" x2="58" y2="190"/><line x1="100" y1="204" x2="60" y2="210"/>
      <line x1="220" y1="196" x2="262" y2="190"/><line x1="220" y1="204" x2="260" y2="210"/>
    </g>
  </g>
</svg>`;
  };

  // Mount the cat into a host (untimed wrapper) and return its parts.
  EF.mountCat = function (host) {
    host.innerHTML = EF.catSVG();
    const q = (s) => host.querySelector(s);
    const parts = {
      svg: q(".cat-svg"), head: q(".c-head"), body: q(".c-body"), tail: q(".c-tail"),
      armL: q(".c-armL"), armR: q(".c-armR"), eyes: q(".c-eyes"), wink: q(".c-wink"),
      eyeR: host.querySelectorAll(".c-eye")[1], open: q(".c-mouth-open"), closed: q(".c-mouth-closed"),
      pupils: host.querySelectorAll(".c-pupil"),
    };
    gsap.set(parts.head, { svgOrigin: "160 240" });
    gsap.set(parts.tail, { svgOrigin: "232 300" });
    gsap.set(parts.armL, { svgOrigin: "96 262" });
    gsap.set(parts.armR, { svgOrigin: "224 262" });
    gsap.set(parts.eyes, { svgOrigin: "160 150" });
    return parts;
  };

  // Mouth flaps during [s,e] segments (local time), deterministic 7.5 Hz with variation.
  EF.catTalk = function (tl, cat, segs) {
    segs.forEach(([s, e], k) => {
      const r = EF.rng(91 + k);
      let t = s;
      let open = true;
      while (t < e) {
        tl.set(cat.open, { opacity: open ? 1 : 0 }, t);
        tl.set(cat.closed, { opacity: open ? 0 : 1 }, t);
        t += open ? 0.08 + r() * 0.06 : 0.05 + r() * 0.05;
        open = !open;
      }
      tl.set(cat.open, { opacity: 0 }, e);
      tl.set(cat.closed, { opacity: 1 }, e);
    });
  };
  EF.catBlink = function (tl, cat, times) {
    times.forEach((t) => {
      tl.to(cat.eyes, { scaleY: 0.08, duration: 0.06, ease: "power2.in" }, t);
      tl.to(cat.eyes, { scaleY: 1, duration: 0.09, ease: "power2.out" }, t + 0.07);
    });
  };
  // Idle life: tail sway + head tilt, offset parts (character acting, not a UI loop)
  EF.catIdle = function (tl, cat, from, to, seed) {
    const r = EF.rng(seed || 5);
    for (let t = from; t < to; t += 0.5) {
      const a = (r() - 0.5) * 22;
      tl.to(cat.tail, { rotation: a, duration: 0.5, ease: "sine.inOut" }, t);
    }
    for (let t = from + 0.15; t < to; t += 1) {
      tl.to(cat.head, { rotation: (r() - 0.5) * 8, duration: 0.6, ease: "sine.inOut" }, t);
    }
  };

  // ---------- Star dust / sparkles on canvas ----------
  function star4(ctx, x, y, r, rot) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const rr = i % 2 === 0 ? r : r * 0.28;
      const a = (i * Math.PI) / 4;
      ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
    }
    ctx.closePath(); ctx.fill(); ctx.restore();
  }
  EF.star4 = star4;

  EF.starfield = function (canvas, opts) {
    const o = Object.assign({ n: 120, seed: 3, colors: ["#F6EFDF", "#E8C27A", "#C9D0A8"], drift: 18, big: 10, alpha: 1 }, opts || {});
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height, r = EF.rng(o.seed);
    const stars = Array.from({ length: o.n }, () => ({
      x: r() * W, y: r() * H, s: 1 + r() * 2.6, ph: r() * 6.28, sp: 1.5 + r() * 3.5,
      c: o.colors[Math.floor(r() * o.colors.length)], v: 0.4 + r(),
    }));
    const bigs = Array.from({ length: o.big }, () => ({
      x: r() * W, y: r() * H, s: 8 + r() * 14, ph: r() * 6.28, sp: 1 + r() * 2, c: o.colors[Math.floor(r() * 2)], rot: r(),
    }));
    return function (t, bursts) {
      ctx.clearRect(0, 0, W, H);
      for (const s of stars) {
        const a = 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(t * s.sp + s.ph));
        let y = (s.y - t * o.drift * s.v) % H; if (y < 0) y += H;
        ctx.globalAlpha = a * o.alpha; ctx.fillStyle = s.c;
        ctx.beginPath(); ctx.arc(s.x, y, s.s, 0, 6.283); ctx.fill();
      }
      for (const b of bigs) {
        const k = 0.5 + 0.5 * Math.sin(t * b.sp + b.ph);
        ctx.globalAlpha = k * 0.9 * o.alpha; ctx.fillStyle = b.c;
        star4(ctx, b.x, b.y, b.s * (0.5 + 0.5 * k), b.rot + t * 0.6);
      }
      if (bursts) EF.drawBursts(ctx, t, bursts);
      ctx.globalAlpha = 1;
    };
  };

  // bursts: [{t, x, y, n, spread, colors, seed}]
  EF.drawBursts = function (ctx, t, bursts) {
    for (const b of bursts) {
      const u = t - b.t; const life = b.life || 1.1;
      if (u < 0 || u > life) continue;
      const r = EF.rng(b.seed || Math.floor(b.t * 1000));
      const n = b.n || 18, cols = b.colors || ["#E8C27A", "#F6EFDF", "#F2B8B5", "#C9D0A8"];
      for (let i = 0; i < n; i++) {
        const ang = r() * 6.283, sp = (b.spread || 260) * (0.4 + r() * 0.8);
        const e = 1 - Math.pow(1 - Math.min(1, u / life), 3);
        const x = b.x + Math.cos(ang) * sp * e;
        const y = b.y + Math.sin(ang) * sp * e + 120 * u * u;
        const size = (b.size || 16) * (0.5 + r()) * (1 - u / life);
        ctx.globalAlpha = Math.max(0, 1 - u / life); ctx.fillStyle = cols[i % cols.length];
        star4(ctx, x, y, size, r() * 3 + u * 4);
      }
    }
    ctx.globalAlpha = 1;
  };

  window.EF = EF;
})();
