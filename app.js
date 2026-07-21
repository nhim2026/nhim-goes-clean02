const STORAGE='nhim-goes:v1.1';
const defaultState={
  sentences:[],
  mistakes:[],
  journal:[],
  preferences:{
    reviewSize:5,
    dailyTarget:10,
    uiLanguage:'vi',
    speakingPace:'slow',
    correctionDensity:'standard'
  },
  activeTab:'learn'
};

function load(){
  try{
    const existing=JSON.parse(localStorage.getItem(STORAGE)||'{}');
    return {...structuredClone(defaultState),...existing,preferences:{...defaultState.preferences,...(existing.preferences||{})}};
  }catch{return structuredClone(defaultState)}
}
let state=load();
const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
function save(){localStorage.setItem(STORAGE,JSON.stringify(state))}
function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function log(type,text){state.journal.unshift({id:crypto.randomUUID(),type,text,at:new Date().toISOString()});save()}
function dueItems(){return state.sentences.filter(x=>!x.nextReviewAt||x.nextReviewAt<=Date.now()).slice(0,state.preferences.reviewSize)}
function streak(){const days=new Set(state.journal.map(x=>new Date(x.at).toDateString()));let n=0,d=new Date();while(days.has(d.toDateString())){n++;d.setDate(d.getDate()-1)}return n}
function todayCount(){const t=new Date().toDateString();return state.journal.filter(x=>new Date(x.at).toDateString()===t).length}
function toast(msg){const el=document.createElement('div');el.className='toast';el.textContent=msg;document.body.append(el);setTimeout(()=>el.remove(),1800)}
function openSheet(html){$('#sheet').innerHTML=`<div class="sheet-handle"></div>${html}`;$('#sheet').classList.remove('hidden');$('#sheetBackdrop').classList.remove('hidden')}
function closeSheet(){$('#sheet').classList.add('hidden');$('#sheetBackdrop').classList.add('hidden')}
$('#sheetBackdrop').addEventListener('click',closeSheet);

function pageHeader(eyebrow,title,sub=''){
  return `<header class="page-header"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1>${sub?`<div class="sub">${sub}</div>`:''}</div><div class="avatar">N</div></header>`;
}

function weekBars(){
  const labels=['T2','T3','T4','T5','T6','T7','CN'];
  const now=new Date();const day=(now.getDay()+6)%7;
  const counts=labels.map((_,i)=>{
    const d=new Date(now);d.setDate(now.getDate()-(day-i));
    const key=d.toDateString();
    return state.journal.filter(x=>new Date(x.at).toDateString()===key).length;
  });
  const max=Math.max(1,...counts);
  return counts.map((c,i)=>`<div class="bar-wrap"><div class="bar ${i===day?'active':''}" style="height:${Math.max(10,c/max*76)}px"></div><div class="bar-label">${labels[i]}</div></div>`).join('');
}

function learnView(){
  const due=dueItems().length,done=todayCount(),target=state.preferences.dailyTarget,progress=Math.min(100,Math.round(done/target*100));
  return `
    ${pageHeader('Nhím Goes','Hôm nay','Một chút mỗi ngày, miễn là đúng thứ bạn cần.')}
    <section class="card hero">
      <div class="hero-top">
        <div>
          <div class="eyebrow" style="color:rgba(255,255,255,.6)">Daily focus</div>
          <div class="hero-number">${due}</div>
          <div>câu đang chờ bạn ôn</div>
        </div>
        <div class="progress-ring" style="--progress:${progress}%"><span>${progress}%</span></div>
      </div>
      <div class="row" style="margin-top:18px">
        <button class="primary-btn" id="startReview">${due?'Bắt đầu ôn':'Ôn lại câu đã lưu'}</button>
        <span class="pill" style="background:rgba(255,255,255,.14);color:white">🔥 ${streak()} ngày</span>
      </div>
    </section>

    <div class="section-title"><h2>Luyện nhanh</h2><small>Chọn theo nhu cầu</small></div>
    <section class="grid-2">
      <button class="quick-card" data-action="capture">
        <span class="icon-box">＋</span><div><h3>Lưu câu mới</h3><p>Giữ lại câu bạn thật sự muốn dùng.</p></div>
      </button>
      <button class="quick-card" data-action="fix">
        <span class="icon-box">✎</span><div><h3>Fix my English</h3><p>Sửa câu và giải thích ngắn gọn.</p></div>
      </button>
      <button class="quick-card" data-action="chat">
        <span class="icon-box">◌</span><div><h3>AI Chat</h3><p>Nói chuyện ngắn, sửa lỗi vừa đủ.</p></div>
      </button>
      <button class="quick-card" data-action="library">
        <span class="icon-box">◫</span><div><h3>My English</h3><p>Xem lại toàn bộ câu của riêng bạn.</p></div>
      </button>
    </section>

    <div class="section-title"><h2>Tuần này</h2><small>${done}/${target} hoạt động hôm nay</small></div>
    <section class="card"><div class="week-bars">${weekBars()}</div></section>

    <div class="section-title"><h2>Tiếp theo</h2></div>
    <section class="card list">
      <div class="list-row"><div class="list-icon">◎</div><div class="list-main"><div class="list-title">Review queue</div><div class="list-sub">${due} câu đến hạn · session ${state.preferences.reviewSize} câu</div></div><span class="chev">›</span></div>
      <div class="list-row"><div class="list-icon">✦</div><div class="list-main"><div class="list-title">Hành trình của bạn</div><div class="list-sub">${state.journal.length} hoạt động đã ghi nhận</div></div><span class="chev">›</span></div>
    </section>
    <button class="fab" data-action="capture" aria-label="Lưu câu mới">＋</button>
  `;
}

function libraryView(){
  const items=state.sentences.map(x=>`<div class="list-row sentence-item" data-id="${x.id}"><div class="list-icon">Aa</div><div class="list-main"><div class="list-title">${esc(x.text)}</div><div class="list-sub">${x.nextReviewAt?'Ôn lại '+new Date(x.nextReviewAt).toLocaleDateString('vi-VN'):'Sẵn sàng ôn'}</div></div><span class="chev">›</span></div>`).join('');
  return `
    ${pageHeader('Library','My English','Không phải một kho lưu trữ — đây là tiếng Anh của riêng bạn.')}
    <input class="search" id="search" placeholder="Tìm câu, cụm từ...">
    <div class="tag-row" style="margin:12px 0 18px"><button class="tag active">Tất cả</button><button class="tag">Cần ôn</button><button class="tag">Mới</button></div>
    <section class="card list" id="libraryList">${items||'<div class="empty">Chưa có câu nào.<br><small>Hãy lưu câu đầu tiên từ màn hình Hôm nay.</small></div>'}</section>
    <button class="fab" data-action="capture" aria-label="Lưu câu mới">＋</button>
  `;
}

function journalView(){
  const items=state.journal.slice(0,30).map(x=>`<div class="timeline-item"><div class="timeline-date">${new Date(x.at).toLocaleString('vi-VN')}</div><div class="list-title">${x.type==='capture'?'Đã lưu một câu mới':x.type==='review'?'Đã hoàn thành một lượt ôn':x.type==='chat'?'Đã luyện hội thoại':'Hoạt động'}</div><div class="list-sub">${esc(x.text)}</div></div>`).join('');
  return `
    ${pageHeader('Journal','Hành trình','Nhìn lại những gì đang dần trở thành của bạn.')}
    <section class="stat-strip">
      <div class="stat"><strong>${state.sentences.length}</strong><span>Câu đã lưu</span></div>
      <div class="stat"><strong>${state.journal.filter(x=>x.type==='review').length}</strong><span>Lượt ôn</span></div>
      <div class="stat"><strong>${streak()}</strong><span>Streak</span></div>
    </section>
    <div class="section-title"><h2>Timeline</h2><small>Gần đây</small></div>
    <section class="card">${items||'<div class="empty">Chưa có gì để kể hôm nay.</div>'}</section>
  `;
}

function settingsView(){
  return `
    ${pageHeader('Profile','Cá nhân','Điều chỉnh Nhím Goes theo đúng cách bạn muốn học.')}
    <section class="card" style="display:flex;align-items:center;gap:14px">
      <div class="avatar" style="width:58px;height:58px;border-radius:20px">N</div>
      <div><h2>Nhím</h2><div class="sub" style="margin-top:3px">B1 · Daily communication</div></div>
    </section>

    <div class="section-title"><h2>Learning</h2></div>
    <section class="setting-group">
      <div class="setting-row" data-setting="reviewSize"><div class="setting-icon">↻</div><div class="setting-copy"><div class="setting-title">Review session</div><div class="setting-sub">Số câu mỗi lần ôn</div></div><div class="setting-value">${state.preferences.reviewSize} câu ›</div></div>
      <div class="setting-row" data-setting="dailyTarget"><div class="setting-icon">◎</div><div class="setting-copy"><div class="setting-title">Mục tiêu mỗi ngày</div><div class="setting-sub">Nhẹ nhàng nhưng đều</div></div><div class="setting-value">${state.preferences.dailyTarget} hoạt động ›</div></div>
    </section>

    <div class="section-title"><h2>AI & Conversation</h2></div>
    <section class="setting-group">
      <div class="setting-row"><div class="setting-icon">◌</div><div class="setting-copy"><div class="setting-title">Tốc độ hội thoại</div><div class="setting-sub">Phù hợp với trình độ hiện tại</div></div><span class="pill">Chậm</span></div>
      <div class="setting-row"><div class="setting-icon">✎</div><div class="setting-copy"><div class="setting-title">Mức độ sửa lỗi</div><div class="setting-sub">Không ngắt mạch hội thoại quá nhiều</div></div><span class="pill">Vừa đủ</span></div>
    </section>

    <div class="section-title"><h2>Data & Backup</h2></div>
    <section class="setting-group">
      <button class="setting-row" id="exportBtn" style="width:100%;text-align:left;background:transparent;border:0"><div class="setting-icon">⇩</div><div class="setting-copy"><div class="setting-title">Export backup</div><div class="setting-sub">Tải dữ liệu về thiết bị</div></div><span class="chev">›</span></button>
      <button class="setting-row" id="importBtn" style="width:100%;text-align:left;background:transparent;border:0"><div class="setting-icon">⇧</div><div class="setting-copy"><div class="setting-title">Import backup</div><div class="setting-sub">Khôi phục dữ liệu đã lưu</div></div><span class="chev">›</span></button>
      <input id="importFile" type="file" accept="application/json" hidden>
      <button class="setting-row" id="resetBtn" style="width:100%;text-align:left;background:transparent;border:0"><div class="setting-icon">!</div><div class="setting-copy"><div class="setting-title" style="color:var(--danger)">Reset dữ liệu</div><div class="setting-sub">Xóa dữ liệu cục bộ trên thiết bị này</div></div><span class="chev">›</span></button>
    </section>

    <div class="section-title"><h2>App</h2></div>
    <section class="setting-group">
      <div class="setting-row"><div class="setting-icon">i</div><div class="setting-copy"><div class="setting-title">Nhím Goes</div><div class="setting-sub">Local-first personal English companion</div></div><span class="pill">v1.1</span></div>
      <div class="setting-row"><div class="setting-icon">◫</div><div class="setting-copy"><div class="setting-title">Storage</div><div class="setting-sub">${state.sentences.length} câu · ${state.journal.length} hoạt động</div></div><span class="chev">›</span></div>
    </section>
  `;
}

function render(){
  $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.tab===state.activeTab));
  $('#app').innerHTML=state.activeTab==='learn'?learnView():state.activeTab==='library'?libraryView():state.activeTab==='journal'?journalView():settingsView();
  bind();
}

function schedule(item,rating){
  const days=rating==='again'?1:rating==='good'?Math.max(2,(item.intervalDays||1)*2):Math.max(4,(item.intervalDays||1)*3);
  item.intervalDays=Math.min(days,90);item.nextReviewAt=Date.now()+item.intervalDays*86400000;item.lastRating=rating;log('review',`${rating.toUpperCase()}: ${item.text}`);save();
}

function captureSheet(){
  openSheet(`<div class="sheet-header"><div><div class="eyebrow">Capture</div><h2>Lưu một câu mới</h2></div><button class="close-btn">×</button></div><div class="field"><label class="label">Câu bạn muốn nhớ</label><textarea id="captureText" placeholder="Ví dụ: Could you speak a little more slowly?"></textarea></div><button class="primary-btn" style="width:100%" id="saveSentence">Lưu vào My English</button>`);
  $('.close-btn').onclick=closeSheet;
  $('#saveSentence').onclick=()=>{const text=$('#captureText').value.trim();if(!text)return;const key=text.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();if(state.sentences.some(x=>x.key===key))return toast('Câu này đã có rồi');state.sentences.unshift({id:crypto.randomUUID(),text,key,createdAt:Date.now(),nextReviewAt:Date.now(),intervalDays:1});log('capture',text);closeSheet();render();toast('Đã lưu câu mới')};
}

function fixSheet(){
  openSheet(`<div class="sheet-header"><div><div class="eyebrow">AI Fix</div><h2>Fix my English</h2></div><button class="close-btn">×</button></div><div class="field"><label class="label">Câu của bạn</label><textarea id="fixText" placeholder="Viết câu bạn muốn nói..."></textarea></div><button class="primary-btn" style="width:100%" id="fixBtn">Sửa giúp mình</button><div id="fixResult" style="margin-top:16px"></div>`);
  $('.close-btn').onclick=closeSheet;
  $('#fixBtn').onclick=async()=>{const text=$('#fixText').value.trim();if(!text)return;$('#fixResult').innerHTML='<div class="card">Đang kiểm tra...</div>';try{const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'fix',text})});const j=await r.json();$('#fixResult').innerHTML=`<div class="card"><div class="eyebrow">Natural version</div><h3>${esc(j.correction||text)}</h3><div class="sub">${esc(j.explanation||'')}</div></div>`}catch{$('#fixResult').innerHTML='<div class="card">AI hiện chưa sẵn sàng.</div>'}};
}

function chatSheet(){
  openSheet(`<div class="sheet-header"><div><div class="eyebrow">Conversation</div><h2>Nói chuyện một chút</h2></div><button class="close-btn">×</button></div><div class="field"><label class="label">Bạn muốn nói gì?</label><textarea id="chatText" placeholder="Tell me about your day..."></textarea></div><button class="primary-btn" style="width:100%" id="chatBtn">Gửi</button><div id="chatResult" style="margin-top:16px"></div>`);
  $('.close-btn').onclick=closeSheet;
  $('#chatBtn').onclick=async()=>{const text=$('#chatText').value.trim();if(!text)return;$('#chatResult').innerHTML='<div class="card">Đang nghĩ...</div>';try{const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'chat',messages:[{role:'user',content:text}]})});const j=await r.json();$('#chatResult').innerHTML=`<div class="card"><div class="eyebrow">Reply</div><h3>${esc(j.reply||'')}</h3><div class="sub">${esc(j.nextQuestion||'')}</div></div>`;log('chat',text)}catch{$('#chatResult').innerHTML='<div class="card">AI hiện chưa sẵn sàng.</div>'}};
}

function reviewSheet(){
  const item=dueItems()[0]||state.sentences[0];
  if(!item)return toast('Chưa có câu nào để ôn');
  openSheet(`<div class="sheet-header"><div><div class="eyebrow">Review</div><h2>Nhớ câu này không?</h2></div><button class="close-btn">×</button></div><div class="card review-card"><div class="small">English</div><div class="review-word">${esc(item.text)}</div><div class="rating-grid"><button class="ghost-btn" data-rate="again">Again</button><button class="secondary-btn" data-rate="good">Good</button><button class="primary-btn" data-rate="easy">Easy</button></div></div>`);
  $('.close-btn').onclick=closeSheet;
  $$('[data-rate]').forEach(b=>b.onclick=()=>{schedule(item,b.dataset.rate);closeSheet();render();toast('Đã cập nhật lịch ôn')});
}

function bind(){
  $$('[data-action="capture"]').forEach(x=>x.onclick=captureSheet);
  $$('[data-action="fix"]').forEach(x=>x.onclick=fixSheet);
  $$('[data-action="chat"]').forEach(x=>x.onclick=chatSheet);
  $$('[data-action="library"]').forEach(x=>x.onclick=()=>{state.activeTab='library';save();render()});
  $('#startReview')?.addEventListener('click',reviewSheet);

  $('#search')?.addEventListener('input',e=>{
    const q=e.target.value.toLowerCase().trim();
    const items=state.sentences.filter(x=>x.text.toLowerCase().includes(q));
    $('#libraryList').innerHTML=items.map(x=>`<div class="list-row"><div class="list-icon">Aa</div><div class="list-main"><div class="list-title">${esc(x.text)}</div></div></div>`).join('')||'<div class="empty">Không tìm thấy.</div>';
  });

  $$('[data-setting="reviewSize"]').forEach(x=>x.onclick=()=>{
    openSheet(`<div class="sheet-header"><h2>Review session</h2><button class="close-btn">×</button></div><div class="tag-row">${[5,10,15].map(n=>`<button class="tag ${state.preferences.reviewSize===n?'active':''}" data-size="${n}">${n} câu</button>`).join('')}</div>`);
    $('.close-btn').onclick=closeSheet;$$('[data-size]').forEach(b=>b.onclick=()=>{state.preferences.reviewSize=Number(b.dataset.size);save();closeSheet();render()});
  });

  $$('[data-setting="dailyTarget"]').forEach(x=>x.onclick=()=>{
    openSheet(`<div class="sheet-header"><h2>Mục tiêu mỗi ngày</h2><button class="close-btn">×</button></div><div class="tag-row">${[5,10,15,20].map(n=>`<button class="tag ${state.preferences.dailyTarget===n?'active':''}" data-target="${n}">${n}</button>`).join('')}</div>`);
    $('.close-btn').onclick=closeSheet;$$('[data-target]').forEach(b=>b.onclick=()=>{state.preferences.dailyTarget=Number(b.dataset.target);save();closeSheet();render()});
  });

  $('#exportBtn')?.addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify({app:'nhim-goes',schemaVersion:1,exportedAt:new Date().toISOString(),data:state},null,2)],{type:'application/json'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`nhim-goes-backup-${new Date().toISOString().slice(0,10)}.json`;a.click();URL.revokeObjectURL(a.href);
  });
  $('#importBtn')?.addEventListener('click',()=>$('#importFile').click());
  $('#importFile')?.addEventListener('change',async e=>{try{const j=JSON.parse(await e.target.files[0].text());if(j.app!=='nhim-goes'||!j.data)throw new Error();if(!confirm('Khôi phục backup này và thay dữ liệu hiện tại?'))return;state={...structuredClone(defaultState),...j.data,preferences:{...defaultState.preferences,...(j.data.preferences||{})}};save();render();toast('Đã khôi phục dữ liệu')}catch{alert('File backup không hợp lệ')}});
  $('#resetBtn')?.addEventListener('click',()=>{if(prompt('Gõ RESET để xóa dữ liệu')!=='RESET')return;state=structuredClone(defaultState);save();render();toast('Đã reset dữ liệu')});
}

$$('.nav-item').forEach(btn=>btn.addEventListener('click',()=>{state.activeTab=btn.dataset.tab;save();render()}));
if('serviceWorker'in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
render();
