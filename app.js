const STORAGE = 'nhim-goes:v1.0.2';

const defaultState = {
  sentences: [],
  mistakes: [],
  journal: [],
  preferences: {reviewSize:5, dailyTarget:10},
  activeTab: 'learn'
};

function load() {
  try { return {...defaultState, ...JSON.parse(localStorage.getItem(STORAGE) || '{}')}; }
  catch { return structuredClone(defaultState); }
}
let state = load();

function save() {
  localStorage.setItem(STORAGE, JSON.stringify(state));
}

function log(type, text) {
  state.journal.unshift({id:crypto.randomUUID(), type, text, at:new Date().toISOString()});
  save();
}

function esc(s='') {
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function dueItems() {
  const now = Date.now();
  return state.sentences.filter(x => !x.nextReviewAt || x.nextReviewAt <= now).slice(0, state.preferences.reviewSize);
}

function schedule(item, rating) {
  const days = rating === 'again' ? 1 : rating === 'good' ? Math.max(2,(item.intervalDays||1)*2) : Math.max(4,(item.intervalDays||1)*3);
  item.intervalDays = Math.min(days,90);
  item.nextReviewAt = Date.now() + item.intervalDays*86400000;
  item.lastRating = rating;
  log('review', `${rating.toUpperCase()}: ${item.text}`);
}

function header(title, sub='') {
  return `<h1>${title}</h1>${sub?`<div class="sub">${sub}</div>`:''}`;
}

function learnView() {
  const due = dueItems();
  return `
    ${header('Nhím Goes','Học tiếng Anh theo những câu bạn thật sự muốn dùng.')}
    <section class="card">
      <h2>Capture</h2>
      <textarea id="captureText" placeholder="Nhập một câu tiếng Anh bạn muốn nhớ..."></textarea>
      <div class="row" style="margin-top:10px"><button id="saveSentence">Save sentence</button></div>
    </section>

    <section class="card">
      <h2>Review</h2>
      <div class="stat">${due.length}</div>
      <div class="small">câu đang đến hạn</div>
      ${due.length ? `<div class="review-word">${esc(due[0].text)}</div>
      <div class="row">
        <button data-rate="again" class="secondary">Again</button>
        <button data-rate="good">Good</button>
        <button data-rate="easy">Easy</button>
      </div>` : `<div class="empty">Không có câu nào cần ôn ngay.</div>`}
    </section>

    <section class="card">
      <h2>AI Fix</h2>
      <textarea id="fixText" placeholder="Nhập câu cần sửa..."></textarea>
      <div class="row" style="margin-top:10px"><button id="fixBtn">Fix my sentence</button></div>
      <div id="fixResult" class="item"></div>
    </section>

    <section class="card">
      <h2>AI Chat</h2>
      <textarea id="chatText" placeholder="Say something in English..."></textarea>
      <div class="row" style="margin-top:10px"><button id="chatBtn">Send</button></div>
      <div id="chatResult" class="item"></div>
    </section>
  `;
}

function libraryView() {
  const items = state.sentences.map(x => `<div class="item"><strong>${esc(x.text)}</strong><div class="small">Next review: ${x.nextReviewAt?new Date(x.nextReviewAt).toLocaleDateString():'now'}</div></div>`).join('');
  return `${header('My English','Những câu bạn đã lưu.')}
  <section class="card">
    <input id="search" placeholder="Search..." />
    <div id="libraryList">${items || '<div class="empty">Chưa có câu nào.</div>'}</div>
  </section>`;
}

function journalView() {
  const items = state.journal.map(x => `<div class="item"><span class="badge">${esc(x.type)}</span><div>${esc(x.text)}</div><div class="small">${new Date(x.at).toLocaleString()}</div></div>`).join('');
  return `${header('My Journey','Lịch sử học gần đây.')}<section class="card">${items || '<div class="empty">Chưa có hoạt động.</div>'}</section>`;
}

function settingsView() {
  return `${header('Settings','Dữ liệu được lưu cục bộ trên thiết bị này.')}
  <section class="card">
    <h2>Preferences</h2>
    <label>Review session size</label>
    <select id="reviewSize">
      ${[5,10,15].map(n=>`<option ${state.preferences.reviewSize===n?'selected':''}>${n}</option>`).join('')}
    </select>
  </section>
  <section class="card">
    <h2>Data</h2>
    <div class="row">
      <button id="exportBtn">Export JSON</button>
      <button id="importBtn" class="secondary">Import JSON</button>
      <input id="importFile" type="file" accept="application/json" hidden>
      <button id="resetBtn" class="secondary">Reset</button>
    </div>
  </section>
  <section class="card">
    <h2>Diagnostics</h2>
    <div class="item">Version <strong>1.0.2</strong></div>
    <div class="item">Sentences <strong>${state.sentences.length}</strong></div>
    <div class="item">Journal events <strong>${state.journal.length}</strong></div>
  </section>`;
}

function render() {
  document.querySelectorAll('.bottom-nav button').forEach(b=>b.classList.toggle('active', b.dataset.tab===state.activeTab));
  const app = document.querySelector('#app');
  app.innerHTML = state.activeTab==='learn' ? learnView() : state.activeTab==='library' ? libraryView() : state.activeTab==='journal' ? journalView() : settingsView();
  bind();
}

function bind() {
  document.querySelector('#saveSentence')?.addEventListener('click', () => {
    const text = document.querySelector('#captureText').value.trim();
    if (!text) return;
    const key = text.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
    if (state.sentences.some(x=>x.key===key)) return alert('Câu này đã tồn tại.');
    state.sentences.unshift({id:crypto.randomUUID(), text, key, createdAt:Date.now(), nextReviewAt:Date.now(), intervalDays:1});
    log('capture', text);
    render();
  });

  document.querySelectorAll('[data-rate]').forEach(btn=>btn.addEventListener('click',()=>{
    const item = dueItems()[0];
    if (!item) return;
    schedule(item, btn.dataset.rate);
    save(); render();
  }));

  document.querySelector('#fixBtn')?.addEventListener('click', async () => {
    const text = document.querySelector('#fixText').value.trim();
    if (!text) return;
    const out = document.querySelector('#fixResult');
    out.textContent = 'Checking...';
    try {
      const r = await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'fix',text})});
      const j = await r.json();
      out.innerHTML = `<strong>${esc(j.correction||text)}</strong><div>${esc(j.explanation||'')}</div>`;
    } catch { out.textContent='AI unavailable.'; }
  });

  document.querySelector('#chatBtn')?.addEventListener('click', async () => {
    const text = document.querySelector('#chatText').value.trim();
    if (!text) return;
    const out = document.querySelector('#chatResult');
    out.textContent='Thinking...';
    try {
      const r = await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'chat',messages:[{role:'user',content:text}]})});
      const j = await r.json();
      out.innerHTML = `<strong>${esc(j.reply||'')}</strong><div>${esc(j.nextQuestion||'')}</div>`;
      log('chat', text);
    } catch { out.textContent='AI unavailable.'; }
  });

  document.querySelector('#search')?.addEventListener('input', e => {
    const q = e.target.value.toLowerCase().trim();
    const list = state.sentences.filter(x=>x.text.toLowerCase().includes(q));
    document.querySelector('#libraryList').innerHTML = list.map(x=>`<div class="item"><strong>${esc(x.text)}</strong></div>`).join('') || '<div class="empty">Không tìm thấy.</div>';
  });

  document.querySelector('#reviewSize')?.addEventListener('change', e => {
    state.preferences.reviewSize = Number(e.target.value); save();
  });

  document.querySelector('#exportBtn')?.addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({app:'nhim-goes',schemaVersion:1,exportedAt:new Date().toISOString(),data:state},null,2)], {type:'application/json'});
    const a = document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`nhim-goes-backup-${new Date().toISOString().slice(0,10)}.json`; a.click(); URL.revokeObjectURL(a.href);
  });

  document.querySelector('#importBtn')?.addEventListener('click',()=>document.querySelector('#importFile').click());
  document.querySelector('#importFile')?.addEventListener('change', async e => {
    try {
      const j = JSON.parse(await e.target.files[0].text());
      if (j.app!=='nhim-goes' || !j.data) throw new Error();
      if (!confirm('Restore this backup and replace current data?')) return;
      state = {...defaultState, ...j.data}; save(); render();
    } catch { alert('Invalid backup file.'); }
  });

  document.querySelector('#resetBtn')?.addEventListener('click', () => {
    if (prompt('Type RESET to delete local data')!=='RESET') return;
    state = structuredClone(defaultState); save(); render();
  });
}

document.querySelectorAll('.bottom-nav button').forEach(btn=>btn.addEventListener('click',()=>{
  state.activeTab=btn.dataset.tab; save(); render();
}));

if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(()=>{});
render();
