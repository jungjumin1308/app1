'use strict';
// 소리산책 — 외부 라이브러리·서버·음원 파일 없이 동작합니다.
const $ = id => document.getElementById(id);
let audio, master, generation = 0, timers = [], voices = [], mode = 'rhythm';
let targets = [], taps = [], accepting = false, pitchRound = 0, correct = 0, pair = [], answered = false;
let best = {rhythm:0,pitch:0};
try { const saved = JSON.parse(localStorage.getItem('soundwalk-v1') || '{}'); for (const key of ['rhythm','pitch']) {const n=Number(saved?.[key]);best[key]=Number.isFinite(n)?Math.max(0,Math.min(key==='rhythm'?100:5,n)):0;} } catch (_) { $('storage-note').textContent='이 브라우저에서는 기록을 저장할 수 없어 현재 실행 중에만 유지돼요.'; }
function renderBest(){ $('best-rhythm').textContent=best.rhythm+'점'; $('best-pitch').textContent=best.pitch+' / 5'; }
function save(){renderBest();try{localStorage.setItem('soundwalk-v1',JSON.stringify(best));}catch(_){$('storage-note').textContent='저장이 제한되어 기록은 현재 실행 중에만 유지돼요.';}}
renderBest();
async function soundReady(){
 const AudioClass=window.AudioContext||window.webkitAudioContext;
 if(!AudioClass) throw new Error('이 브라우저는 소리 기능을 지원하지 않아요. 최신 Chrome 또는 Safari로 열어 주세요.');
 if(!audio){audio=new AudioClass();master=audio.createGain();master.connect(audio.destination);}
 master.gain.value=Number($('volume').value)/100*.35;
 await audio.resume();
 if(audio.state!=='running')throw new Error('소리를 시작하지 못했어요. 기기의 소리 설정을 확인한 후 다시 눌러 주세요.');
}
function tone(freq,when,duration=.22,type='sine'){
 const osc=audio.createOscillator(),gain=audio.createGain(); osc.type=type;osc.frequency.value=freq;
 gain.gain.setValueAtTime(0,when);gain.gain.linearRampToValueAtTime(.8,when+.012);gain.gain.exponentialRampToValueAtTime(.001,when+duration);
 osc.connect(gain);gain.connect(master);osc.start(when);osc.stop(when+duration+.02);voices.push(osc);
 osc.onended=()=>{osc.disconnect();gain.disconnect();voices=voices.filter(v=>v!==osc);};
}
function at(time,fn){const token=generation;timers.push(setTimeout(()=>{if(token===generation)fn();},Math.max(0,(time-audio.currentTime)*1000)));}
function cancel(){generation++;timers.forEach(clearTimeout);timers=[];voices.forEach(v=>{try{v.stop();}catch(_){}});voices=[];accepting=false;$('tap').disabled=true;$('rhythm-start').disabled=false;$('pitch-start').disabled=false;$('first').disabled=true;$('second').disabled=true;$('replay').disabled=true;$('next').hidden=true;}
function stopped(){cancel();$('rhythm-status').textContent='쉬었다가 다시 시작해도 좋아요.';$('pitch-status').textContent='게임을 멈췄어요. 시작 버튼으로 다시 도전해요.';}
$('stop').onclick=stopped;
for(const name of ['rhythm','pitch'])$('tab-'+name).onclick=()=>{cancel();mode=name;for(const n of ['rhythm','pitch']){$(n).hidden=n!==name;$('tab-'+n).setAttribute('aria-selected',String(n===name));}$('rhythm-status').textContent='시작 버튼을 누르면 리듬을 들려드려요.';$('pitch-status').textContent='시작 버튼을 누르면 두 소리를 들려드려요.';};
$('volume').oninput=()=>{$('volume-label').textContent=$('volume').value+'%';if(master)master.gain.value=Number($('volume').value)/100*.35;};
$('rhythm-start').onclick=async()=>{
 cancel();const token=generation;$('rhythm-start').disabled=true;
 try{await soundReady();if(token!==generation)return;
 const level=$('difficulty').value,bpm={easy:60,normal:80,hard:100}[level],beat=60/bpm;
 const patterns=level==='easy'?[[0,1,2,3]]:level==='normal'?[[0,1,2,3],[0,1,1.5,3]]:[[0,.5,2,3],[0,1.5,2,3.5]];
 const pattern=patterns[Math.floor(Math.random()*patterns.length)];
 const begin=audio.currentTime+.35,prep=begin+5*beat,start=prep+4*beat;
 $('rhythm-status').textContent='먼저 들어 보세요. 네 번의 소리가 나와요.';
 pattern.forEach(p=>tone(660,begin+p*beat,.15));
 for(let i=0;i<4;i++){tone(250,prep+i*beat,.08);at(prep+i*beat,()=>{$('rhythm-status').textContent='준비 박자 '+(i+1)+' / 4'+(i===3?' · 다음 박자부터 따라 쳐요!':'');});}
 targets=pattern.map(p=>start+p*beat);taps=[];
 at(start-.2,()=>{accepting=true;$('tap').disabled=false;});
 at(start,()=>{$('rhythm-status').textContent='지금! 들었던 리듬으로 네 번 눌러 주세요.';});
 at(targets[3]+Math.max(.5,beat),()=>{
 accepting=false;$('tap').disabled=true;$('rhythm-start').disabled=false;
 const used=new Set();let sum=0,hits=0;
 for(const t of taps){let idx=-1,d=.3;targets.forEach((target,i)=>{const diff=Math.abs(t-target);if(!used.has(i)&&diff<d){d=diff;idx=i;}});if(idx>=0){used.add(idx);sum+=1-d/.3;hits++;}}
 const extra=Math.max(0,taps.length-4),score=Math.max(0,Math.round(sum/4*100-extra*10));
 best.rhythm=Math.max(best.rhythm,score);save();$('rhythm-status').textContent=score+'점 · 네 박자 중 '+hits+'번 타이밍에 맞았어요. '+(score>=75?'멋진 리듬이에요!':'다시 들으며 천천히 도전해요!');
 });
 }catch(e){if(token===generation){cancel();$('rhythm-status').textContent=e.message;}}
};
function tap(){if(!accepting||!audio)return;taps.push(audio.currentTime);$('tap').textContent='톡! '+taps.length+'번';}
$('tap').addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();tap();});
// 키보드/보조기기의 합성 클릭은 pointerdown 없이 처리합니다.
$('tap').addEventListener('click',e=>{if(e.detail===0)tap();});
document.addEventListener('keydown',e=>{if(e.code==='Space'&&mode==='rhythm'&&accepting&&!['INPUT','SELECT','BUTTON'].includes(document.activeElement.tagName)){e.preventDefault();if(!e.repeat)tap();}});
const originalStart=$('rhythm-start').onclick;$('rhythm-start').onclick=function(){ $('tap').textContent='여기를 톡!';return originalStart();};
function playPair(){
 $('first').disabled=true;$('second').disabled=true;$('replay').disabled=true;
 const start=audio.currentTime+.15;
 $('pitch-status').textContent=pitchRound+' / 5문제 · 두 소리를 들어 보세요.';
 tone(pair[0],start,.55);tone(pair[1],start+.95,.55);
 at(start+1.6,()=>{if(answered)return;$('first').disabled=false;$('second').disabled=false;$('replay').disabled=false;$('pitch-status').textContent=pitchRound+' / 5문제 · 더 높은 소리는 어느 쪽인가요?';});
}
function newQuestion(){pitchRound++;answered=false;$('next').hidden=true;const base=[261.63,293.66,329.63,349.23][Math.floor(Math.random()*4)],semitones=[7,7,5,4,3][pitchRound-1];const high=base*Math.pow(2,semitones/12);pair=Math.random()<.5?[base,high]:[high,base];playPair();}
$('pitch-start').onclick=async()=>{cancel();const token=generation;$('pitch-start').disabled=true;try{await soundReady();if(token!==generation)return;pitchRound=0;correct=0;$('pitch-score').textContent='0 / 5';newQuestion();}catch(e){if(token===generation){cancel();$('pitch-status').textContent=e.message;}}};
$('replay').onclick=async()=>{const token=generation;try{await soundReady();if(token===generation&&!answered)playPair();}catch(e){$('pitch-status').textContent=e.message;}};
function answer(index){if(answered||$('first').disabled)return;answered=true;const right=pair[0]>pair[1]?0:1;const ok=index===right;if(ok)correct++;$('first').disabled=true;$('second').disabled=true;$('replay').disabled=true;$('pitch-score').textContent=correct+' / 5';$('pitch-status').textContent=(ok?'정답이에요! ':'괜찮아요. ')+(right===0?'첫 번째':'두 번째')+' 소리가 더 높아요.';
 if(pitchRound<5){$('next').hidden=false;}else{best.pitch=Math.max(best.pitch,correct);save();$('pitch-start').disabled=false;$('pitch-status').textContent+=' 다섯 문제 완료! '+correct+'문제를 맞혔어요. 다시 도전해 볼까요?';}}
$('first').onclick=()=>answer(0);$('second').onclick=()=>answer(1);
$('next').onclick=async()=>{const token=generation;try{await soundReady();if(token===generation)newQuestion();}catch(e){$('pitch-status').textContent=e.message;}};
$('reset').onclick=()=>{if(window.confirm('이 브라우저의 최고 기록을 지울까요?')){best={rhythm:0,pitch:0};save();}};
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopped();});
