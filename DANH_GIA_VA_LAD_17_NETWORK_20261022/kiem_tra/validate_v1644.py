"""Discrete scan model from V1644 screenshots; NOT a Siemens runtime or compiler."""
from dataclasses import dataclass,field
from pathlib import Path
import itertools,random,json
ROOT=Path(__file__).resolve().parent
@dataclass
class PLC:
    optimized:bool=False
    first:bool=True
    edge_memory:bool=False
    armed:bool=False
    permit:bool=False
    fault_memory:bool=False
    step:int=0
    next_step:int=0
    elapsed:list=field(default_factory=lambda:[0]*5)
    def scan(self,auto=False,water=True,overload=False,estop=False,stop=False,reset=False,clock=7*3600,rtc=0,dt=10):
        first=self.first
        if first:
            self.armed=False;self.permit=False;self.step=0;self.next_step=0
        init_alias=first # ordinary coil in current NW1
        rtc_ok=rtc in (0,1)
        morning=rtc_ok and 6*3600<=clock<8*3600
        evening=rtc_ok and 17*3600<=clock<20*3600+30*60
        in_schedule=morning or evening
        safe=not estop and water and not overload
        fault=not safe or (auto and not rtc_ok)
        reset_request=reset and not (first if self.optimized else init_alias)
        acknowledge=reset_request and safe and rtc_ok and not fault
        self.fault_memory=(self.fault_memory or fault) and not acknowledge
        if not auto:self.armed=True
        cancel=not auto or not safe or not rtc_ok or self.fault_memory or reset_request or (first if self.optimized else init_alias)
        rising=auto and not self.edge_memory
        self.edge_memory=auto
        self.permit=(self.permit or (rising and self.armed and not cancel)) and not cancel
        if self.permit:self.armed=False
        running=self.permit and in_schedule and not cancel
        self.next_step=self.step
        if running and self.step==0:self.next_step=1
        # All five calls see current step BEFORE the commit, each called once.
        for n in range(1,6):
            clear=self.step!=n or not running
            if not self.optimized:clear=clear or reset_request
            timer_in=running and self.step==n and not stop
            if clear:self.elapsed[n-1]=0
            elif timer_in:self.elapsed[n-1]=min(10000,self.elapsed[n-1]+dt)
            done=self.elapsed[n-1]>=10000
            if done and not stop and running:self.next_step=n%5+1
        if running and not stop:self.step=self.next_step
        clear_steps=not running or (reset_request and not self.optimized)
        if clear_steps:self.step=0;self.next_step=0
        v=(running and 1<=self.step<=4 and not stop,
           running and 2<=self.step<=5 and not stop,
           running and 3<=self.step<=4 and not stop,
           running and 4<=self.step<=5 and not stop)
        # New V1644 order is valves FIRST, then pump.
        pump=any(v) and running and safe and not stop
        selected_et=self.elapsed[self.step-1] if running and 1<=self.step<=5 else 0
        remaining=10-selected_et//1000
        if not running or (self.optimized and not 1<=self.step<=5):remaining=0
        self.first=False
        return dict(step=self.step,next_step=self.next_step,elapsed=tuple(self.elapsed),
            remaining=remaining,van=tuple(map(int,v)),pump=int(pump),alarm=int(self.fault_memory),
            running=bool(running),permit=self.permit,armed=self.armed,edge=self.edge_memory,
            rtc_ok=rtc_ok,safe=safe,fault=bool(fault),reset=bool(reset_request),cancel=bool(cancel))

def paired():return PLC(False),PLC(True)
def tick(pair,**kw):
    a,b=[p.scan(**kw) for p in pair]
    control_a={k:v for k,v in a.items() if k!='remaining'}
    control_b={k:v for k,v in b.items() if k!='remaining'}
    assert control_a==control_b, {'input':kw,'current':a,'proposal':b}
    if a['running'] and not 1<=a['step']<=5:
        assert a['remaining']==10 and b['remaining']==0
    else:assert a['remaining']==b['remaining']
    return b

def started(**kw):
    p=paired();tick(p,auto=False,**kw);r=tick(p,auto=True,**kw)
    assert r['step']==1 and r['pump']==1
    return p
results=[]
def test(name,fn):
    detail=fn();results.append(dict(test=name,status='PASS',detail=detail))

def schedule():
    count=0
    for second in range(86400):
        h,m=second//3600,(second%3600)//60
        original=(h>=6 and h<8) or ((h>=17 and h<20) or (h==20 and m<30))
        expected=21600<=second<28800 or 61200<=second<73800
        assert original==expected;count+=1
    return {'seconds_checked':count,'windows':'[06:00,08:00),[17:00,20:30)'}
test('Hai ca và toàn bộ mốc giây trong ngày',schedule)

def truth_outputs():
    count=0
    patterns={1:(1,0,0,0),2:(1,1,0,0),3:(1,1,1,0),4:(1,1,1,1),5:(0,1,0,1)}
    for step,run,stop,safe in itertools.product(range(-2,9),(False,True),(False,True),(False,True)):
        actual=tuple(int(run and not stop and lo<=step<=hi) for lo,hi in ((1,4),(2,5),(3,4),(4,5)))
        expected=patterns.get(step,(0,0,0,0)) if run and not stop else (0,0,0,0)
        assert actual==expected
        assert (any(actual) and run and safe and not stop)==(bool(any(expected)) and safe)
        count+=1
    return {'combinations':count,'patterns':patterns}
test('Giải mã van và bơm, kể cả bước ngoài 1–5',truth_outputs)

def sequence():
    p=started();seen=[1];changes=[];last=1
    for i in range(1,6001):
        r=tick(p,auto=True)
        assert r['pump']==1
        if r['step']!=last:
            assert r['step']==last%5+1
            seen.append(r['step']);changes.append(i*10);last=r['step']
    assert seen[:6]==[1,2,3,4,5,1]
    return {'first_steps':seen[:7],'transition_times_ms_model':changes[:6]}
test('Chu trình năm bước, bơm không mất lệnh khi chuyển bước',sequence)

def pause_resume():
    p=started()
    for _ in range(420):r=tick(p,auto=True)
    before=(r['step'],r['elapsed'],r['remaining'])
    for _ in range(2000):
        r=tick(p,auto=True,stop=True)
        assert (r['step'],r['elapsed'],r['remaining'])==before
        assert not r['pump'] and not any(r['van']) and r['running']
    r=tick(p,auto=True,stop=False)
    assert r['step']==before[0] and r['elapsed'][0]==4210 and r['pump']
    return {'pause_after_ms':4200,'pause_duration_ms':20000,'resume_elapsed_ms':r['elapsed'][0]}
test('STOP giữ bước/ET/giây rồi tiếp tục',pause_resume)

def near_end():
    p=started()
    for _ in range(999):r=tick(p,auto=True)
    assert r['elapsed'][0]==9990
    for _ in range(100):
        r=tick(p,auto=True,stop=True);assert r['step']==1 and r['elapsed'][0]==9990
    r=tick(p,auto=True);assert r['step']==2 and r['remaining']==10
    return 'Dừng ở9990ms không chuyển; tiếp tục chỉ chuyển1→2.'
test('STOP sát thời điểm timer hoàn thành',near_end)

def off_while_paused():
    p=started()
    for _ in range(200):tick(p,auto=True)
    tick(p,auto=True,stop=True)
    r=tick(p,auto=False,stop=True)
    assert r['step']==0 and r['remaining']==0 and not any(r['elapsed']) and not r['pump']
    r=tick(p,auto=True,stop=True);assert r['step']==0 and not r['pump']
    r=tick(p,auto=True,stop=False);assert r['step']==1 and r['remaining']==10
    return 'TẮT ưu tiên xóa; AUTO khiSTOPcòn1 chưa xuất tải.'
test('TẮT trong lúc STOP',off_while_paused)

def auto_while_stopped():
    p=paired();tick(p,auto=False,stop=True)
    r=tick(p,auto=True,stop=True)
    assert r['step']==0 and r['remaining']==0 and not r['pump']
    r=tick(p,auto=True,stop=False)
    assert r['step']==1 and r['remaining']==10 and r['pump']
    return 'Sửa hiển thị: bước0 khiSTOPgiữ→0giây; bỏSTOP→bước1/10giây.'
test('Hiển thị bước0 khi bậtAUTO lúcSTOPđanggiữ',auto_while_stopped)

def fault_case(key,value):
    p=started()
    for _ in range(310):tick(p,auto=True)
    r=tick(p,auto=True,**{key:value})
    assert r['step']==0 and not any(r['elapsed']) and not r['pump'] and not any(r['van']) and r['alarm']
    r=tick(p,auto=True,reset=True,**{key:value});assert r['alarm'] and not r['permit']
    r=tick(p,auto=True);assert r['alarm'] and not r['pump']
    r=tick(p,auto=True,reset=True);assert not r['alarm'] and r['step']==0 and not r['pump']
    r=tick(p,auto=True);assert not r['pump']
    tick(p,auto=False);r=tick(p,auto=True);assert r['step']==1 and r['pump']
    return 'Dừng cùngscan; nhớlỗi không tựxóa; RESETkhi hếtlỗi; TẮT→AUTO mới chạy.'
for key,value,label in [('water',False,'Thiếu nước'),('overload',True,'Quá tải'),('estop',True,'Dừng khẩn'),('rtc',-32640,'Lỗi đọc RTC')]:
    test(label,lambda k=key,v=value:fault_case(k,v))

def reset_running():
    p=started()
    for _ in range(223):tick(p,auto=True)
    r=tick(p,auto=True,reset=True,stop=False)
    assert r['reset'] and r['step']==0 and r['remaining']==0 and not r['permit']
    for _ in range(40):assert not tick(p,auto=True,reset=True)['pump']
    for _ in range(40):assert not tick(p,auto=True)['pump']
    tick(p,auto=False);r=tick(p,auto=True);assert r['pump']
    return 'RESET nhận khiAUTO1,STOP0; nhảRESET không tự khởi động.'
test('RESET giữa lúc đang chạy và giữ nút RESET',reset_running)

def boundaries():
    for boundary in (8*3600,20*3600+30*60):
        p=started(clock=boundary-1)
        for _ in range(321):tick(p,auto=True,clock=boundary-1)
        r=tick(p,auto=True,clock=boundary)
        assert r['step']==0 and not any(r['elapsed']) and r['remaining']==0 and not r['pump'] and r['permit']
        r=tick(p,auto=True,clock=17*3600 if boundary==8*3600 else 6*3600)
        assert r['step']==1 and r['remaining']==10 and r['pump']
    return '08:00 và20:30 xóa; ca sau bắt đầu bước1 khiquyềnAUTO vẫn còn.'
test('Hết ca và vào ca tiếp theo',boundaries)

def pause_across_end():
    p=started(clock=28799)
    for _ in range(250):tick(p,auto=True,clock=28799)
    r=tick(p,auto=True,stop=True,clock=28800)
    assert r['step']==0 and r['remaining']==0 and not any(r['elapsed'])
    return 'Hếtca ưu tiên xóa dùSTOP đanggiữ.'
test('STOP kéo dài qua thời điểm hết ca',pause_across_end)

def startup():
    p=paired()
    for _ in range(30):
        r=tick(p,auto=True);assert not r['pump'] and not r['permit']
    tick(p,auto=False);r=tick(p,auto=True);assert r['pump'] and r['step']==1
    return 'AUTOgiữ1 từkhởiđộng khôngtựchạy; cầnTẮT→AUTO.'
test('Khóa khởi động khi AUTO đang bật',startup)

def invalid_steps():
    p=started()
    for s in (-2,-1,6,7,8):
        for q in p:q.step=s
        r=tick(p,auto=True)
        assert not any(r['van']) and not r['pump']
    return 'Giátrị ngoài1–5 không mởvan/bơm; cầnRESET đểkhôi phục.'
test('Ngõ ra khi bước bị ghi giá trị bất thường',invalid_steps)

def equivalence_random():
    rng=random.Random(1644);p=paired();kw=dict(auto=False,water=True,overload=False,estop=False,stop=False,reset=False,clock=25200,rtc=0)
    boolean=('auto','water','overload','estop','stop','reset')
    for i in range(30000):
        if i%7==0:
            key=rng.choice(boolean);kw[key]=not kw[key]
        if i%37==0:kw['clock']=rng.choice([21599,21600,28799,28800,61199,61200,73799,73800,25200])
        if i%43==0:kw['rtc']=rng.choice([0,1,-32640])
        if i%997==0:
            for q in p:q.first=True
        tick(p,**kw,dt=rng.choice([5,10,20,50]))
    return {'paired_scans':30000,'random_seed':1644,'compared':'steps,5ET,outputs,remaining,permit,latches,reset,RTC,safety'}
test('So sánh V1644 và bản17 qua chuỗi tín hiệu thay đổi',equivalence_random)
report={'source_commit':'dffa0dd8752a838d4b986bcf3dc6072befdaf487','kind':'Discrete scan model, not Siemens runtime',
        'limitations':['Timer integrates an abstract dt per enabled scan; not a Siemens TONR execution/timing test.',
                       'HMI Events/Animations/connections and native compilation cannot be tested from screenshots.',
                       'No proof covers unseen OBs, HMI writes to internal states, force tables or actual hardware.'],
        'changes_checked':['KHỞI TẠO CHỜ alias replaced by configured FirstScan at visible read sites.',
                           'reset_request parallel branches removed after upstream reset cancels run.',
                           'Network7+8 merged without reordering.',
                           'Intentional display correction: step outside1..5 =>0seconds; valid paused step keeps remaining time.'],
        'passed':len(results),'failed':0,'tests':results}
(ROOT/'ket_qua_mo_hinh.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':len(results),'failed':0,'names':[r['test'] for r in results]},ensure_ascii=False,indent=2))
