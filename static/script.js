// ===== ZIVRAJ AI Learning Dashboard =====
const getChatAvatar = (sender) => {
    if (sender === 'bot') {
        return `<div class="msg-avatar bot-avatar"><img src="/static/images/logo.png" alt="ZIVRAJ AI" class="chat-logo-img"></div>`;
    }
    const initial = typeof USERNAME !== 'undefined' ? USERNAME.charAt(0).toUpperCase() : 'U';
    return `<div class="msg-avatar">${initial}</div>`;
};

let currentDomain = 'general';
let currentDomainData = null;
let userProgress = {};
let isStreaming = false;

// Quiz state
let quiz = { active: false, module: null, qIndex: 0, score: 0, total: 0, streak: 0, timerSec: 0, timerRef: null, waitingAnswer: false, questionType: null };

document.addEventListener('DOMContentLoaded', () => {
    setupDomainButtons();
    setupMobileMenu();
    loadProgress();
});

function setupDomainButtons() {
    document.querySelectorAll('.domain-btn[data-domain]').forEach(btn => {
        btn.addEventListener('click', () => selectDomain(btn.dataset.domain));
    });
}

function setupMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    if (!btn || !sidebar) return;

    // Create overlay backdrop for mobile sidebar
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.id = 'sidebar-overlay';
    document.body.appendChild(overlay);

    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // prevent background scroll
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    btn.addEventListener('click', () => {
        if (sidebar.classList.contains('open')) closeSidebar();
        else openSidebar();
    });

    // Close sidebar when tapping the overlay
    overlay.addEventListener('click', closeSidebar);

    // Close sidebar when pressing Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSidebar();
    });

    // Auto-close sidebar when selecting a domain on mobile
    document.querySelectorAll('.domain-btn').forEach(domainBtn => {
        domainBtn.addEventListener('click', () => {
            if (window.innerWidth <= 900) closeSidebar();
        });
    });

    // Fix mobile viewport height (handles browser chrome on iOS/Android)
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    setVH();
    window.addEventListener('resize', setVH);

    // Handle visual viewport changes (keyboard open/close)
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', () => {
            const vv = window.visualViewport;
            document.documentElement.style.setProperty('--vvh', `${vv.height}px`);
        });
    }

    // Expose closeSidebar globally for use in other functions
    window._closeSidebar = closeSidebar;
}


// ===== STREAMING ENGINE =====
function streamText(el, text, chatBox, speed = 25) {
    return new Promise(resolve => {
        const formatted = formatText(text);
        const chunks = [];
        const re = /(<br>|<[^>]+>)|(\S+)/g;
        let m;
        while ((m = re.exec(formatted)) !== null) chunks.push(m[0]);
        el.classList.add('streaming');
        let i = 0;
        const cursor = document.createElement('span');
        cursor.className = 'streaming-cursor';
        el.appendChild(cursor);
        function next() {
            if (i < chunks.length) {
                const c = chunks[i];
                cursor.insertAdjacentHTML('beforebegin', c.startsWith('<') ? c : c + ' ');
                i++;
                if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
                setTimeout(next, speed + Math.random() * 20);
            } else { cursor.remove(); el.classList.remove('streaming'); resolve(); }
        }
        next();
    });
}

function setSendDisabled(btnId, inputId, disabled) {
    const b = document.getElementById(btnId), inp = document.getElementById(inputId);
    if (b) b.disabled = disabled;
    if (inp) inp.disabled = disabled;
}

function formatText(t) { return t.replace(/\n/g, '<br>'); }

// ===== GENERAL CHAT =====
function addGeneralUserMessage(text) {
    const box = document.getElementById('general-chat-messages');
    const land = document.getElementById('chat-landing');
    if (land) land.style.display = 'none';
    const d = document.createElement('div'); d.className = 'user-message';
    d.innerHTML = `${getChatAvatar('user')}<div class="msg-bubble">${formatText(text)}</div>`;
    box.appendChild(d); box.scrollTop = box.scrollHeight;
}

function addGeneralBotMessage(text, stream = true) {
    const box = document.getElementById('general-chat-messages');
    const land = document.getElementById('chat-landing');
    if (land) land.style.display = 'none';
    const d = document.createElement('div'); d.className = 'bot-message';
    d.innerHTML = `${getChatAvatar('bot')}<div class="msg-bubble bot-bubble"><div class="msg-text"></div></div>`;
    box.appendChild(d); box.scrollTop = box.scrollHeight;
    const mt = d.querySelector('.msg-text');
    if (stream) return streamText(mt, text, box);
    mt.innerHTML = formatText(text); return Promise.resolve();
}

async function sendGeneralMessage() {
    if (isStreaming) return;
    const inp = document.getElementById('general-input'), msg = inp.value.trim();
    if (!msg) return;
    isStreaming = true; setSendDisabled('general-send-btn','general-input',true);
    addGeneralUserMessage(msg); inp.value = '';
    const tid = 'typ-'+Date.now(), box = document.getElementById('general-chat-messages');
    const td = document.createElement('div'); td.className='bot-message'; td.id=tid;
    td.innerHTML=`${getChatAvatar('bot')}<div class="msg-bubble bot-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
    box.appendChild(td); box.scrollTop=box.scrollHeight;
    try {
        const r = await fetch('/get_response',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,domain:'general'})});
        const data = await r.json(); document.getElementById(tid).remove(); await addGeneralBotMessage(data.reply);
    } catch(e) { document.getElementById(tid).remove(); await addGeneralBotMessage('<i data-lucide="alert-circle" class="icon-inline"></i> Something went wrong.',false); }
    isStreaming=false; setSendDisabled('general-send-btn','general-input',false); document.getElementById('general-input').focus();
}

function handleGeneralKeyPress(e) { if(e.key==='Enter') sendGeneralMessage(); }
function askSuggestion(q) { document.getElementById('general-input').value=q; sendGeneralMessage(); }

function backToGeneralChat() {
    endQuiz();
    currentDomain='general'; currentDomainData=null;
    document.querySelectorAll('.domain-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('domain-btn-general').classList.add('active');
    if (window._closeSidebar) window._closeSidebar();
    else document.getElementById('sidebar').classList.remove('open');
    document.getElementById('general-chat-screen').style.display='flex';
    document.getElementById('workspace').style.display='none';
    document.getElementById('nav-current').textContent='General Chat';
}

// ===== DOMAIN SELECTION =====
async function selectDomain(domainKey) {
    endQuiz();
    document.querySelectorAll('.domain-btn').forEach(b=>b.classList.remove('active'));
    const ab=document.getElementById('domain-btn-'+domainKey); if(ab) ab.classList.add('active');
    if (window._closeSidebar) window._closeSidebar();
    else document.getElementById('sidebar').classList.remove('open');
    document.getElementById('general-chat-screen').style.display='none';
    document.getElementById('workspace').style.display='flex';
    try {
        const r=await fetch('/api/domain/'+domainKey), data=await r.json();
        currentDomain=domainKey; currentDomainData=data;
        document.getElementById('nav-current').textContent=data.domain;
        document.getElementById('badge-icon').textContent=data.icon;
        document.getElementById('badge-name').textContent=data.domain;
        const box=document.getElementById('chat-messages'); box.innerHTML='';
        await addBotMsg(data.welcome);
        showModulesInChat(data);
    } catch(e) { console.error(e); }
}

// ===== DOMAIN CHAT HELPERS =====
function addUserMsg(text) {
    const box=document.getElementById('chat-messages');
    const d=document.createElement('div'); d.className='user-message';
    d.innerHTML=`${getChatAvatar('user')}<div class="msg-bubble">${formatText(text)}</div>`;
    box.appendChild(d); box.scrollTop=box.scrollHeight;
}

function addBotMsg(text, stream=true) {
    const box=document.getElementById('chat-messages');
    const d=document.createElement('div'); d.className='bot-message';
    d.innerHTML=`${getChatAvatar('bot')}<div class="msg-bubble bot-bubble"><div class="msg-text"></div></div>`;
    box.appendChild(d); box.scrollTop=box.scrollHeight;
    const mt=d.querySelector('.msg-text');
    if(stream) return streamText(mt, text, box);
    mt.innerHTML=formatText(text); return Promise.resolve();
}

function addBotRawHTML(html) {
    const box=document.getElementById('chat-messages');
    const d=document.createElement('div'); d.className='bot-message';
    d.innerHTML=`${getChatAvatar('bot')}<div class="msg-bubble bot-bubble"><div class="msg-text">${html}</div></div>`;
    box.appendChild(d); box.scrollTop=box.scrollHeight;
}

// ===== SHOW MODULES AS CHAT CARDS =====
function showModulesInChat(domainData) {
    let cardsHTML = '<div class="chat-module-cards">';
    domainData.modules.forEach((mod, i) => {
        const unlocked = i===0 || isModuleUnlocked(domainData.modules, i);
        const completed = isModuleCompleted(mod.id);
        const icon = completed ? '<i data-lucide="check-circle-2"></i>' : (unlocked ? '<i data-lucide="unlock"></i>' : '<i data-lucide="lock"></i>');
        const cls = unlocked ? '' : ' locked';
        cardsHTML += `<button class="chat-module-btn${cls}" ${unlocked?`onclick="startQuiz(${i})"`:''}>
            <span class="mod-icon">${icon}</span>
            <div class="mod-info"><span class="mod-name">Module ${mod.level}: ${mod.name}</span><span class="mod-desc">${mod.questions.length} questions • ${mod.description}</span></div>
            <span class="mod-status">›</span></button>`;
    });
    cardsHTML += '</div>';
    addBotRawHTML('<i data-lucide="book-open" class="icon-inline"></i> Select a module to begin:<br>' + cardsHTML);
}

function isModuleUnlocked(modules, index) {
    if(index===0) return true;
    const prev=modules[index-1], pp=userProgress[prev.id];
    if(!pp) return false;
    return Math.round((pp.score/pp.total)*100) >= modules[index].unlock_score;
}
function isModuleCompleted(id) { return userProgress[id]!==undefined; }

// ===== QUIZ ENGINE (IN-CHAT) =====
function startQuiz(moduleIndex) {
    const mod = currentDomainData.modules[moduleIndex];
    quiz = { active:true, module:mod, moduleIndex, qIndex:0, score:0, total:mod.questions.length, streak:0, timerSec:0, timerRef:null, waitingAnswer:false, questionType:null };
    // Start timer
    quiz.timerRef = setInterval(()=>{ quiz.timerSec++; }, 1000);
    // Show progress bar
    const prog = document.getElementById('chat-quiz-progress');
    if(prog) prog.style.display='flex';
    updateQuizProgress();
    addBotMsg(`<i data-lucide="rocket" class="icon-inline"></i> Starting **${mod.name}** module! ${mod.questions.length} questions. Type a, b, c, or d to answer MCQs. Good luck!`).then(()=>{
        showQuestionInChat();
    });
}

function endQuiz() {
    if(quiz.timerRef) clearInterval(quiz.timerRef);
    quiz = { active:false, module:null, qIndex:0, score:0, total:0, streak:0, timerSec:0, timerRef:null, waitingAnswer:false, questionType:null };
    const prog = document.getElementById('chat-quiz-progress');
    if(prog) prog.style.display='none';
}

function updateQuizProgress() {
    const pt=document.getElementById('quiz-progress-text');
    const st=document.getElementById('quiz-score-text');
    if(pt) pt.textContent=`Question ${quiz.qIndex+1}/${quiz.total}`;
    if(st) st.textContent=`Score: ${quiz.score}/${quiz.qIndex}`;
}

function showQuestionInChat() {
    const q = quiz.module.questions[quiz.qIndex];
    if(!q) return;
    updateQuizProgress();
    quiz.questionType = q.type;
    const labels=['A','B','C','D'];
    if(q.type === 'mcq') {
        let optHTML='';
        q.options.forEach((o,i)=>{
            optHTML+=`<div class="chat-q-option"><span class="opt-key">${labels[i]}</span><span>${o}</span></div>`;
        });
        const html=`<div class="chat-question-card">
            <span class="chat-q-badge">Question ${quiz.qIndex+1}/${quiz.total}</span>
            <div class="chat-q-text">${q.question}</div>
            <div class="chat-q-options">${optHTML}</div>
            <div class="chat-q-hint"><i data-lucide="lightbulb" class="icon-xs"></i> Type a, b, c, or d to answer</div>
        </div>`;
        addBotRawHTML(html);
        quiz.waitingAnswer = true;
    } else {
        // Theory/coding/interview — show question, user types answer, then reveal
        const html=`<div class="chat-question-card">
            <span class="chat-q-badge">${q.type.toUpperCase()} — Question ${quiz.qIndex+1}/${quiz.total}</span>
            <div class="chat-q-text">${q.question}</div>
            <div class="chat-q-hint"><i data-lucide="edit-3" class="icon-xs"></i> Type your answer, then I'll show you the correct one. Or type <strong>skip</strong> to see the answer.</div>
        </div>`;
        addBotRawHTML(html);
        quiz.waitingAnswer = true;
    }
    const box=document.getElementById('chat-messages');
    box.scrollTop=box.scrollHeight;
}

function handleQuizAnswer(userInput) {
    const q = quiz.module.questions[quiz.qIndex];
    if(!q) return;

    if(q.type === 'mcq') {
        const clean = userInput.toLowerCase().trim();
        const map = {a:0, b:1, c:2, d:3};
        if(!(clean in map)) {
            addBotMsg('<i data-lucide="alert-circle" class="icon-inline"></i> Please type **a**, **b**, **c**, or **d** to answer.', false);
            return;
        }
        quiz.waitingAnswer = false;
        const selected = map[clean];
        const correct = q.answer;
        const labels=['A','B','C','D'];

        if(selected === correct) {
            quiz.score++;
            quiz.streak++;
            const msgs=['<i data-lucide="party-popper" class="icon-inline"></i> Correct!','<i data-lucide="sparkles" class="icon-inline"></i> Great job!','<i data-lucide="award" class="icon-inline"></i> Perfect!','<i data-lucide="flame" class="icon-inline"></i> On fire!','<i data-lucide="star" class="icon-inline"></i> Excellent!'];
            const msg = msgs[Math.floor(Math.random()*msgs.length)];
            const streakMsg = quiz.streak > 2 ? ` You're on a ${quiz.streak}-question streak! <i data-lucide="flame" class="icon-inline"></i>` : '';
            const html=`<div class="chat-result-card correct">
                <div class="chat-result-title">${msg}${streakMsg}</div>
                <div class="chat-result-explanation"><i data-lucide="lightbulb" class="icon-xs"></i> ${q.explanation||'Well done!'}</div>
            </div>`;
            addBotRawHTML(html);
        } else {
            quiz.streak = 0;
            const html=`<div class="chat-result-card wrong">
                <div class="chat-result-title"><i data-lucide="x-circle" class="icon-inline"></i> Incorrect — The answer is ${labels[correct]}: ${q.options[correct]}</div>
                <div class="chat-result-explanation"><i data-lucide="lightbulb" class="icon-xs"></i> ${q.explanation||''}</div>
            </div>`;
            addBotRawHTML(html);
        }
        advanceQuiz();
    } else {
        // Theory/coding/interview
        quiz.waitingAnswer = false;
        const skipped = userInput.toLowerCase().trim() === 'skip';
        const userAns = skipped ? '(Skipped)' : userInput;
        const html=`<div class="chat-result-card correct">
            <div class="chat-result-title"><i data-lucide="book-open" class="icon-inline"></i> Correct Answer:</div>
            <div style="font-size:13px;line-height:1.7;color:var(--text);white-space:pre-wrap;margin:8px 0;font-family:'JetBrains Mono',monospace">${formatText(q.answer)}</div>
            ${!skipped ? `<div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.06)"><strong style="color:var(--accent2)">Your answer:</strong><div style="color:var(--text2);margin-top:4px;white-space:pre-wrap">${formatText(userAns)}</div></div>` : ''}
            <div class="chat-q-hint" style="margin-top:10px">Did you get it right? Type <strong>yes</strong> or <strong>no</strong></div>
        </div>`;
        addBotRawHTML(html);
        quiz.waitingAnswer = true;
        quiz.questionType = 'self-rate';
    }
}

function handleSelfRate(input) {
    const clean = input.toLowerCase().trim();
    if(clean==='yes'||clean==='y') {
        quiz.score++; quiz.streak++;
        addBotMsg('<i data-lucide="check-circle-2" class="icon-inline"></i> Great! Marked as correct.', false);
    } else if(clean==='no'||clean==='n') {
        quiz.streak=0;
        addBotMsg('<i data-lucide="refresh-cw" class="icon-inline"></i> No worries! Review this topic later.', false);
    } else {
        addBotMsg('<i data-lucide="alert-circle" class="icon-inline"></i> Please type **yes** or **no**', false);
        return;
    }
    quiz.waitingAnswer = false;
    quiz.questionType = null;
    advanceQuiz();
}

function advanceQuiz() {
    quiz.qIndex++;
    updateQuizProgress();
    if(quiz.qIndex < quiz.total) {
        setTimeout(()=>showQuestionInChat(), 1500);
    } else {
        setTimeout(()=>completeQuizInChat(), 1500);
    }
}

async function completeQuizInChat() {
    clearInterval(quiz.timerRef);
    const total=quiz.total, sc=quiz.score;
    const acc = Math.round((sc/total)*100);
    const mins=String(Math.floor(quiz.timerSec/60)).padStart(2,'0');
    const secs=String(quiz.timerSec%60).padStart(2,'0');
    const timeStr=mins+':'+secs;

    let msg='', badges='';
    if(acc>=90) msg='<i data-lucide="trophy" class="icon-inline"></i> Outstanding! You\'ve mastered this module!';
    else if(acc>=70) msg='<i data-lucide="thumbs-up" class="icon-inline"></i> Great job! Solid understanding!';
    else if(acc>=50) msg='<i data-lucide="activity" class="icon-inline"></i> Good effort! Review and try again!';
    else msg='<i data-lucide="book" class="icon-inline"></i> Keep learning! Practice makes perfect!';

    if(acc===100) badges+='<span class="badge badge-gold"><i data-lucide="medal" class="icon-xs"></i> Perfect Score</span>';
    else if(acc>=80) badges+='<span class="badge badge-silver"><i data-lucide="award" class="icon-xs"></i> High Achiever</span>';
    else if(acc>=60) badges+='<span class="badge badge-bronze"><i data-lucide="star" class="icon-xs"></i> Passing Grade</span>';
    if(quiz.timerSec < total*15) badges+='<span class="badge badge-gold"><i data-lucide="zap" class="icon-xs"></i> Speed Demon</span>';

    const html=`<div class="chat-complete-card">
        <div style="color:var(--primary2); margin-bottom:8px; display:flex; justify-content:center;"><i data-lucide="trophy" style="width:48px;height:48px;"></i></div>
        <h2>Module Complete!</h2>
        <div class="chat-complete-stats">
            <div class="chat-complete-stat"><span class="ccs-value">${sc}/${total}</span><span class="ccs-label">Score</span></div>
            <div class="chat-complete-stat"><span class="ccs-value">${acc}%</span><span class="ccs-label">Accuracy</span></div>
            <div class="chat-complete-stat"><span class="ccs-value">${timeStr}</span><span class="ccs-label">Time</span></div>
        </div>
        <div class="chat-complete-msg">${msg}</div>
        ${badges?'<div class="chat-complete-badges">'+badges+'</div>':''}
        <div class="chat-complete-actions">
            <button class="primary-btn" onclick="restartCurrentQuiz()"><i data-lucide="refresh-cw" class="icon-xs" style="margin-right:4px;"></i> Restart</button>
            <button class="secondary-btn" onclick="showModulesAgain()"><i data-lucide="layers" class="icon-xs" style="margin-right:4px;"></i> All Modules</button>
        </div>
    </div>`;
    addBotRawHTML(html);

    // Save progress
    userProgress[quiz.module.id] = {domain:currentDomain, score:sc, total, accuracy:acc};
    try {
        await fetch('/api/save_progress',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({domain:currentDomain,module_id:quiz.module.id,score:sc,total,accuracy:acc})});
    } catch(e){}

    const prog=document.getElementById('chat-quiz-progress');
    if(prog) { 
        document.getElementById('quiz-progress-text').innerHTML='<i data-lucide="check-circle-2" class="icon-xs" style="margin-right:4px;"></i> Complete';
        document.getElementById('quiz-score-text').textContent=`${sc}/${total} (${acc}%)`;
    }
    quiz.active=false;
}

function restartCurrentQuiz() {
    if(!currentDomainData||!quiz.module) return;
    const idx = quiz.moduleIndex || 0;
    endQuiz();
    startQuiz(idx);
}

function showModulesAgain() {
    endQuiz();
    if(currentDomainData) {
        addBotMsg('<i data-lucide="book-open" class="icon-inline"></i> Here are the available modules:').then(()=>showModulesInChat(currentDomainData));
    }
}

// ===== SEND MESSAGE (handles quiz + normal chat) =====
async function sendMessage() {
    if(isStreaming) return;
    const inp=document.getElementById('user-input'), msg=inp.value.trim();
    if(!msg) return;
    inp.value='';

    // If quiz is active and waiting for answer
    if(quiz.active && quiz.waitingAnswer) {
        addUserMsg(msg);
        if(quiz.questionType==='self-rate') { handleSelfRate(msg); }
        else { handleQuizAnswer(msg); }
        return;
    }

    // Normal domain chat
    isStreaming=true; setSendDisabled('send-btn','user-input',true);
    addUserMsg(msg);
    const tid='typ-'+Date.now(), box=document.getElementById('chat-messages');
    const td=document.createElement('div'); td.className='bot-message'; td.id=tid;
    td.innerHTML=`${getChatAvatar('bot')}<div class="msg-bubble bot-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
    box.appendChild(td); box.scrollTop=box.scrollHeight;
    try {
        const r=await fetch('/get_response',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,domain:currentDomain||'python'})});
        const data=await r.json(); document.getElementById(tid).remove(); await addBotMsg(data.reply);
    } catch(e) { document.getElementById(tid).remove(); await addBotMsg('<i data-lucide="alert-circle" class="icon-inline"></i> Error.',false); }
    isStreaming=false; setSendDisabled('send-btn','user-input',false); document.getElementById('user-input').focus();
}

function handleKeyPress(e) { if(e.key==='Enter') sendMessage(); }

async function clearChat() {
    endQuiz();
    try { await fetch('/clear_chat',{method:'POST'}); } catch(e){}
    const box=document.getElementById('chat-messages'); box.innerHTML='';
    if(currentDomainData) { await addBotMsg(currentDomainData.welcome); showModulesInChat(currentDomainData); }
    else await addBotMsg('Hello! Select a domain.');
}

// ===== PROGRESS =====
async function loadProgress() {
    try { const r=await fetch('/api/get_progress'); userProgress=await r.json(); } catch(e){}
}

// Auto-initialize icons when DOM changes (debounced to prevent infinite loop)
document.addEventListener('DOMContentLoaded', () => {
    let iconTimeout = null;
    let isCreatingIcons = false;
    const observer = new MutationObserver(() => {
        if (isCreatingIcons) return; // skip mutations caused by createIcons itself
        if (iconTimeout) clearTimeout(iconTimeout);
        iconTimeout = setTimeout(() => {
            if (window.lucide) {
                isCreatingIcons = true;
                lucide.createIcons();
                isCreatingIcons = false;
            }
        }, 100);
    });
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    }
});
