"""뮤직 플레이 — Streamlit 음악 미니게임

실행: pip install -r requirements.txt && streamlit run app.py
배포: GitHub 저장소에 이 두 파일을 올린 뒤 Streamlit Community Cloud에서
      app.py를 선택해 배포하세요. GitHub Pages만으로는 Streamlit이 실행되지 않습니다.
QR: 배포 후 사이드바에 공개 앱 주소를 입력하여 QR PNG를 받으세요.
기록: 서버/계정이 아닌 접속 기기의 브라우저 localStorage에 저장합니다.
      시크릿 모드, 사이트 데이터 삭제, 다른 브라우저에서는 유지되지 않을 수 있습니다.
게임 판정은 브라우저에서 수행하여 Streamlit 서버 왕복 지연을 피합니다.
"""
import io
from urllib.parse import urlparse

import qrcode
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="뮤직 플레이", page_icon="🎵", layout="centered")
st.markdown("""<style>
.block-container{padding-top:1.6rem;padding-bottom:1rem;max-width:850px}
[data-testid="stAppViewContainer"]{background:#f6f7fb}
</style>""", unsafe_allow_html=True)
st.title("🎵 뮤직 플레이")
st.caption("귀로 듣고, 손으로 연주하는 음악 미니게임 · 휴대폰에서도 즐겨보세요")
with st.sidebar:
    st.header("📱 QR로 접속")
    st.write("GitHub에 업로드한 뒤 Streamlit Community Cloud에서 먼저 배포하세요.")
    url = st.text_input("배포한 앱의 공개 주소", placeholder="https://your-app.streamlit.app")
    if url:
        parsed = urlparse(url.strip())
        if parsed.scheme in ("http", "https") and parsed.netloc:
            image = qrcode.make(url.strip())
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            st.image(buffer.getvalue(), caption="휴대폰 카메라로 스캔하세요")
            st.download_button("QR 이미지 내려받기", buffer.getvalue(), "music-app-qr.png", "image/png")
        else:
            st.warning("https:// 로 시작하는 올바른 주소를 입력하세요.")
    st.divider()
    st.caption("소리는 게임 시작 또는 듣기 버튼을 눌러 활성화됩니다. 무음 모드를 해제하고 기기 음량도 확인하세요.")
    st.caption("최고 기록은 현재 기기·브라우저에만 저장됩니다. 공동 순위표가 아닙니다.")

HTML = r'''
<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;color:#18243d;background:#f6f7fb}
.card{background:white;border:1px solid #e6e9f1;border-radius:22px;padding:22px;margin:0 0 16px;box-shadow:0 7px 24px #20305006}
h2{font-size:22px;margin:0 0 9px}p{line-height:1.65;margin:8px 0;color:#56627a}.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.control{flex:1;min-width:180px}label{display:block;font-weight:650;margin-bottom:8px}select,input[type=range]{width:100%;min-height:40px}select{border:1px solid #d8dfed;border-radius:10px;padding:8px;background:white;font-size:16px}
button{touch-action:manipulation;cursor:pointer;border:0;background:#eaf0fa;color:#223555;font:700 16px system-ui;padding:13px 18px;border-radius:12px;min-height:48px}
button.primary{background:#6246e5;color:white}button:disabled{opacity:.45;cursor:not-allowed}button:focus-visible{outline:3px solid #ec9e23;outline-offset:3px}
.tabs{display:flex;gap:8px;margin-bottom:16px}.tabs button{flex:1}.tabs .active{background:#192a49;color:white}
.badge{display:inline-block;border-radius:20px;background:#efebff;color:#5940cd;padding:6px 12px;font-size:13px;font-weight:700}
.status{padding:14px;background:#f2f5fb;border-radius:12px;min-height:76px;line-height:1.65;margin:15px 0}
.dots{display:flex;gap:12px;justify-content:center;margin:20px 0}.dot{width:36px;height:36px;border-radius:50%;background:#e5e9f2;transition:background .07s,transform .07s}.dot.on{background:#7856f2;transform:scale(1.15)}
#tap{width:100%;min-height:105px;background:#6246e5;color:white;font-size:25px;user-select:none;-webkit-user-select:none}
#tap:disabled{background:#a9a0cf}.choices button{flex:1;min-width:120px}.small{font-size:13px;color:#67728a}.scores{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}#notice{color:#9c431c}progress{width:100%;height:12px;accent-color:#6246e5}
@media(max-width:420px){.card{padding:16px}h2{font-size:20px}.control{min-width:140px}button{padding:12px}}
</style></head><body>
<div class="card"><div class="row">
<div class="control"><label for="tempo">⏱ 빠르기</label><select id="tempo"><option value="70">천천히 · 70 BPM</option><option value="100" selected>보통 · 100 BPM</option><option value="130">빠르게 · 130 BPM</option></select></div>
<div class="control"><label for="volume">🔊 음량 <span id="volLabel">50%</span></label><input id="volume" type="range" min="0" max="100" value="50"></div>
</div><p class="small">빠르기는 리듬 간격과 두 소리 사이의 간격에 적용됩니다. 게임 진행 중에는 변경할 수 없습니다.</p></div>
<div class="tabs" role="group" aria-label="게임 선택"><button id="rhythmTab" class="active">🥁 리듬 따라 하기</button><button id="pitchTab">🎹 높은 음 찾기</button></div>
<div class="card" id="rhythmPanel">
<span class="badge">LISTEN & TAP</span><h2 style="margin-top:12px">네 번의 소리를 따라 해요</h2>
<p>소리를 끝까지 듣고, 기억한 간격대로 버튼을 네 번 눌러보세요. 첫 번째 누르기는 시작 기준이므로 서두르지 않아도 됩니다.</p>
<div class="dots" id="dots" aria-hidden="true"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
<div class="row"><button id="rhythmStart" class="primary">새 리듬 듣기</button><button id="rhythmReplay" disabled>다시 듣기</button></div>
<div class="status" id="rhythmStatus" role="status" aria-live="polite">준비되면 ‘새 리듬 듣기’를 눌러주세요.</div>
<button id="tap" disabled>여기를 톡! 👆</button><p class="small">리듬 입력: 화면 터치 · 마우스 클릭 · 버튼에 초점을 맞춘 뒤 Enter 또는 Space. 소리가 재생되는 동안은 입력할 수 없습니다.</p>
</div>
<div class="card" id="pitchPanel" hidden>
<span class="badge">5 QUESTIONS</span><h2 style="margin-top:12px">어느 소리가 더 높을까요?</h2>
<p>두 소리를 듣고 더 높은 소리를 골라주세요. 큰 소리가 아니라, 더 가늘고 높은 소리를 찾는 게임이에요.</p>
<progress id="pitchProgress" value="0" max="5" aria-label="완료한 문제 수"></progress>
<div class="status" id="pitchStatus" role="status" aria-live="polite">총 5문제입니다. 준비되면 시작하세요.</div>
<div class="row"><button id="pitchStart" class="primary">5문제 시작</button><button id="pitchListen" disabled>두 소리 다시 듣기</button></div>
<div class="row choices" style="margin-top:14px"><button id="first" disabled>① 첫 번째 소리</button><button id="second" disabled>② 두 번째 소리</button></div>
<button id="next" hidden style="width:100%;margin-top:14px">다음 문제 →</button>
</div>
<div class="card"><h2>🏆 나의 최고 기록</h2><div class="scores"><p>리듬 <strong id="rhythmBest">0</strong> / 100점</p><p>높은 음 <strong id="pitchBest">0</strong> / 5문제</p></div><p class="small">리듬은 세 간격의 상대 오차로 채점합니다. 빠르기별 기록이 아닌 전체 최고 기록입니다.</p><p class="small" id="storageInfo">이 기기·브라우저에 자동 저장됩니다.</p><button id="reset">기록 초기화</button><p id="notice" role="alert"></p></div>
<script>
'use strict';
const $=id=>document.getElementById(id);
let ctx, gain, mode='rhythm', busy=false, token=0, timers=[], rhythm=[], taps=[], rhythmState='idle', pitchState='idle', question=0, correct=0, pair=[], answer=0;
let best={rhythm:0,pitch:0}; const KEY='music-play-best-v1';
try{const s=JSON.parse(localStorage.getItem(KEY)||'{}');for(const k of ['rhythm','pitch'])if(Number.isFinite(s[k]))best[k]=Math.max(0,Math.min(k==='rhythm'?100:5,Math.round(s[k])))}catch(e){$('storageInfo').textContent='저장소를 사용할 수 없어 이번 접속 동안만 기록됩니다.'}
function renderBest(){$('rhythmBest').textContent=best.rhythm;$('pitchBest').textContent=best.pitch}renderBest();
function save(){renderBest();try{localStorage.setItem(KEY,JSON.stringify(best))}catch(e){$('storageInfo').textContent='저장이 차단되어 이번 접속 동안만 기록됩니다.'}}
function later(fn,ms){const t=setTimeout(fn,ms);timers.push(t);return t}
function clearTimers(){timers.forEach(clearTimeout);timers=[]}
async function audio(){const A=window.AudioContext||window.webkitAudioContext;if(!A)throw Error('이 브라우저는 소리 재생을 지원하지 않습니다. 최신 Chrome 또는 Safari를 사용해주세요.');if(!ctx){ctx=new A();gain=ctx.createGain();gain.gain.value=Number($('volume').value)/100*.35;gain.connect(ctx.destination)}if(ctx.state!=='running')await ctx.resume();if(ctx.state!=='running')throw Error('소리를 활성화하지 못했습니다. 기기 무음 모드와 브라우저 권한을 확인해주세요.')}
function tone(freq,time,duration=.18){const o=ctx.createOscillator(),g=ctx.createGain();o.type='sine';o.frequency.value=freq;g.gain.setValueAtTime(0,time);g.gain.linearRampToValueAtTime(1,time+.012);g.gain.exponentialRampToValueAtTime(.001,time+duration);o.connect(g);g.connect(gain);o.start(time);o.stop(time+duration+.02);o.onended=()=>{o.disconnect();g.disconnect()}}
$('volume').oninput=()=>{$('volLabel').textContent=$('volume').value+'%';if(gain)gain.gain.setTargetAtTime(Number($('volume').value)/100*.35,ctx.currentTime,.02)};
function lock(v){busy=v;$('tempo').disabled=v;$('rhythmTab').disabled=v;$('pitchTab').disabled=v}
function error(e){clearTimers();lock(false);$('notice').textContent=e.message||'소리 재생에 실패했습니다. 다시 시도해주세요.';rhythmState='idle';pitchState='idle';$('rhythmStart').disabled=false;$('rhythmReplay').disabled=true;$('pitchStart').disabled=false;$('pitchListen').disabled=true;$('tap').disabled=true;choices(false)}
function switchMode(m){if(busy)return;mode=m;$('rhythmPanel').hidden=m!=='rhythm';$('pitchPanel').hidden=m!=='pitch';$('rhythmTab').classList.toggle('active',m==='rhythm');$('pitchTab').classList.toggle('active',m==='pitch')}
$('rhythmTab').onclick=()=>switchMode('rhythm');$('pitchTab').onclick=()=>switchMode('pitch');
function flash(i){const d=$('dots').children[i];d.classList.add('on');later(()=>d.classList.remove('on'),160)}
async function playRhythm(fresh){
 if(busy)return;lock(true);$('notice').textContent='';$('rhythmStart').disabled=true;$('rhythmReplay').disabled=true;$('tap').disabled=true;clearTimers();
 try{await audio();if(fresh){const beat=60/Number($('tempo').value);rhythm=[0];for(let i=1;i<4;i++)rhythm.push(rhythm[i-1]+beat*[.5,1,1.5][Math.floor(Math.random()*3)])}
 taps=[];rhythmState='listening';$('rhythmStatus').textContent='잘 들어보세요! 네 번의 소리가 나옵니다.';const start=ctx.currentTime+.15;
 rhythm.forEach((t,i)=>{tone(i===0?660:520,start+t,.12);later(()=>flash(i),(t+.15)*1000)});
 later(()=>{rhythmState='tapping';$('tap').disabled=false;$('rhythmStatus').textContent='이제 따라 해보세요! 첫 번째 누르기로 시작합니다. (0 / 4)';$('tap').focus();
 later(()=>{if(rhythmState==='tapping'){rhythmState='idle';$('tap').disabled=true;$('rhythmStatus').textContent='입력 시간이 지났어요. 새 리듬이나 다시 듣기로 재도전하세요.';finishRhythm()}},30000)
 },(rhythm[3]+.65)*1000);
 }catch(e){error(e)}
}
function finishRhythm(){lock(false);$('rhythmStart').disabled=false;$('rhythmReplay').disabled=false}
$('rhythmStart').onclick=()=>playRhythm(true);$('rhythmReplay').onclick=()=>playRhythm(false);
function tap(){if(rhythmState!=='tapping')return;const t=performance.now();if(taps.length&&t-taps[taps.length-1]<65)return;taps.push(t);flash(taps.length-1);$('rhythmStatus').textContent=`따라 하는 중… (${taps.length} / 4)`;
 if(taps.length===4){rhythmState='done';clearTimers();for(const d of $('dots').children)d.classList.remove('on');$('tap').disabled=true;let err=0;for(let i=1;i<4;i++){const expected=(rhythm[i]-rhythm[i-1])*1000;err+=Math.abs(taps[i]-taps[i-1]-expected)/expected}const score=Math.round(100*Math.max(0,1-err/3));if(score>best.rhythm){best.rhythm=score;save()}$('rhythmStatus').textContent=`${score>=85?'훌륭해요! 🎉':score>=60?'좋아요! 👏':'한 번 더 도전해봐요! 🎵'} ${score} / 100점 · 평균 간격 오차 ${Math.round(err/3*100)}%`;finishRhythm()}}
// pointerdown measures touch timing without a server round trip; click handles keyboard/assistive activation.
$('tap').addEventListener('pointerdown',e=>{if(e.isPrimary&&e.button===0){e.preventDefault();tap()}});
$('tap').addEventListener('click',e=>{if(e.detail===0)tap()});
function choices(on){$('first').disabled=!on;$('second').disabled=!on}
function makeQuestion(){const base=[261.63,293.66,329.63,349.23,392,440][Math.floor(Math.random()*6)];const high=base*Math.pow(2,[2,3,5,7][Math.floor(Math.random()*4)]/12);answer=Math.random()<.5?0:1;pair=answer===0?[high,base]:[base,high]}
async function listen(){if(pitchState==='playing')return;pitchState='playing';lock(true);choices(false);$('pitchListen').disabled=true;$('pitchStart').disabled=true;$('notice').textContent='';
 try{await audio();const gap=60/Number($('tempo').value)+.35;const start=ctx.currentTime+.15;tone(pair[0],start,.4);tone(pair[1],start+gap,.4);$('pitchStatus').textContent=`${question+1} / 5번 문제 · 첫 번째 소리…`;later(()=>{$('pitchStatus').textContent=`${question+1} / 5번 문제 · 두 번째 소리…`},(gap+.15)*1000);later(()=>{pitchState='answering';choices(true);$('pitchListen').disabled=false;$('pitchStatus').textContent=`${question+1} / 5번 문제 · 어느 소리가 더 높았나요?`},(gap+.7)*1000)}catch(e){error(e)}}
$('pitchStart').onclick=()=>{if(busy)return;question=0;correct=0;$('pitchProgress').value=0;$('next').hidden=true;makeQuestion();listen()};
$('pitchListen').onclick=()=>{if(pitchState==='answering')listen()};
function choose(index){if(pitchState!=='answering')return;pitchState='answered';choices(false);$('pitchListen').disabled=true;const yes=index===answer;if(yes)correct++;question++;$('pitchProgress').value=question;
 const feedback=`${yes?'정답이에요! 🎉':'아쉬워요!'} ${answer===0?'첫 번째':'두 번째'} 소리가 더 높아요.`;
 if(question===5){$('pitchStatus').textContent=feedback+` 최종 결과: 5문제 중 ${correct}문제 정답!`;if(correct>best.pitch){best.pitch=correct;save()}$('pitchStart').textContent='다시 5문제 도전';$('pitchStart').disabled=false;$('next').hidden=true;lock(false)}else{$('pitchStatus').textContent=feedback+` 현재 ${correct} / ${question}문제 정답`;$('next').hidden=false}}
$('first').onclick=()=>choose(0);$('second').onclick=()=>choose(1);$('next').onclick=()=>{if(pitchState!=='answered'||question>=5)return;$('next').hidden=true;makeQuestion();listen()};
$('reset').onclick=()=>{if(confirm('이 브라우저의 최고 기록을 초기화할까요?')){best={rhythm:0,pitch:0};save()}};
// Background tabs suspend audio/timers on mobile. Invalidate the current round rather than score a distorted performance.
document.addEventListener('visibilitychange',()=>{if(document.hidden&&busy){token++;clearTimers();if(ctx){ctx.close();ctx=null;gain=null}rhythmState='idle';pitchState='idle';lock(false);$('tap').disabled=true;choices(false);$('rhythmStart').disabled=false;$('rhythmReplay').disabled=!rhythm.length;$('pitchStart').disabled=false;$('pitchListen').disabled=true;$('next').hidden=true;$('notice').textContent='화면을 벗어나 진행 중인 게임을 중단했어요. 다시 시작해주세요.';for(const d of $('dots').children)d.classList.remove('on')}});
</script></body></html>
'''
components.html(HTML, height=1080, scrolling=True)
st.caption("🎧 조용한 곳에서 적당한 음량으로 사용하세요. 실제 소리·터치 지연은 기기와 블루투스 연결에 따라 달라질 수 있습니다.")
