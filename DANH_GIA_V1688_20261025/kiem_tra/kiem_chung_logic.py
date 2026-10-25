"""Đối chiếu logic Boolean V1688; không chạy TIA, PLCSIM hoặc PLC.

Nguồn: biểu thức chép từ ảnh tại commit aae862c01ddf4d1225ce9127cda915b7a7da8b55.
Không sửa chương trình. Timer chỉ được xét thuộc tính reset/giữ Q, không mô phỏng
đồng hồ IEC timer hoặc độ trễ giao tiếp HMI. Không có kết quả nghiệm thu PLCSIM.
"""
from collections import deque
from itertools import product
from pathlib import Path
import json

B = (False, True)
INPUTS = list(product(B, repeat=5))


def scan(state, inputs, first=False, simplified=False):
    """State=(G,Q,edge_memory,latched_fault); input=(A,safe,rtc,reset,window)."""
    g, q, edge_memory, latched = state
    auto, safe, rtc, reset_hmi, window = inputs
    if first:
        g = q = False                 # NW1
    fault = not safe or (auto and not rtc)      # NW4
    reset = reset_hmi and not first            # NW5
    acknowledge = reset and safe and rtc
    latched = (latched or fault) and not acknowledge  # NW6, SR.R1 ưu tiên
    if not auto:
        g = True                     # NW7
    cancel = not auto or not safe or not rtc or latched or reset or first
    pulse = auto and not edge_memory  # NW8: P đứng đầu nhánh, cập nhật mọi scan
    edge_memory = auto
    if simplified:
        q = (q or pulse) and not cancel
        run = q and window and rtc
    else:
        q = (q or (pulse and g and not cancel)) and not cancel
        if q:
            g = False
        run = q and window and rtc and not cancel
    return (g, q, edge_memory, latched), (q, edge_memory, latched, run, cancel,
                                            fault, acknowledge, reset, pulse)


def reachable_equivalence():
    """All initial Boolean old states, all first-scan inputs, then graph closure."""
    reachable = set()
    queue = deque()
    first_cases = 0
    for state in product(B, repeat=4):
        for inputs in INPUTS:
            old_next, old_obs = scan(state, inputs, first=True)
            new_next, new_obs = scan(state, inputs, first=True, simplified=True)
            assert old_obs == new_obs, ('FirstScan', state, inputs, old_obs, new_obs)
            # G is intentionally absent from the reduced design; only shared states persist.
            assert old_next[1:] == new_next[1:]
            first_cases += 1
            if old_next not in reachable:
                reachable.add(old_next); queue.append(old_next)
    initial_reachable = len(reachable)
    transitions = 0
    while queue:
        state = queue.popleft()
        for inputs in INPUTS:
            old_next, old_obs = scan(state, inputs)
            new_next, new_obs = scan(state, inputs, simplified=True)
            assert old_obs == new_obs, (state, inputs, old_obs, new_obs)
            assert old_next[1:] == new_next[1:]
            # Inductive invariant: a rising AUTO accepted outside FirstScan has G=1.
            g_before_sr = state[0] or not inputs[0]
            if old_obs[-1] and not old_obs[4]:
                assert g_before_sr
            transitions += 1
            if old_next not in reachable:
                reachable.add(old_next); queue.append(old_next)
    return {'arbitrary_old_states': 16, 'input_combinations': 32,
            'first_scan_comparisons': first_cases,
            'states_after_first_scan': initial_reachable,
            'reachable_states': len(reachable), 'normal_transitions_compared': transitions,
            'different_observable_transitions': 0,
            'reachable_state_values_G_Q_edge_latch': [list(s) for s in sorted(reachable)]}


def contact_equivalence():
    counts = {}
    n = 0
    for q_old, pulse, g, cancel, window in product(B, repeat=5):
        before = (q_old or (pulse and g and not cancel)) and not cancel
        after = (q_old or (pulse and g)) and not cancel
        assert before == after
        assert (before and window and not cancel) == (after and window)
        n += 1
    counts['NW8_two_cancel_contacts_boolean_cases'] = n

    n = 0
    for step in range(1,6):
        for run, same_step, pause, q_old, reaches_pt in product(B, repeat=5):
            reset = not same_step or not run
            timer_in = run and same_step and not pause
            q_fresh = not reset and (q_old or (timer_in and reaches_pt))
            assert (q_fresh and not pause and run) == (q_fresh and not pause)
            n += 1
    counts['NW10_14_run_contact_after_timer_cases'] = n

    n = 0
    for run, pause, *per_valve_conditions in product(B, repeat=6):
        valves = [run and not pause and v for v in per_valve_conditions]
        assert (any(valves) and not pause) == any(valves)
        n += 1
    counts['NW16_pump_pause_contact_cases'] = n

    n = 0
    for run, pause in product(B, repeat=2):
        for step, proposed in product(range(-1,7), repeat=2):
            a, b = step, proposed
            if run and not pause: a = b
            if not run: a = 0
            if not run: b = 0
            c, d = step, proposed
            if run and not pause: c = d
            if not run: c = d = 0
            assert (a,b) == (c,d)
            n += 1
    counts['NW15_shared_reset_condition_cases'] = n
    return counts


def illustrative_trace():
    state=(False,False,False,False)
    trace=[]
    seq=[('RUN, AUTO=0', (False,True,True,False,True), True, True),
         ('Bật AUTO khi STOP đã=1', (True,True,True,False,True), False, True)]
    step=0
    for label, inputs, first, pause in seq:
        state, obs = scan(state,inputs,first=first)
        run=obs[3]
        proposed=1 if run and step==0 else step
        if run and not pause: step=proposed
        if not run: step=proposed=0
        # This trace starts at step0, so all timers have R=1; ET remains0.
        valves=[run and not pause and lo<=step<=hi for lo,hi in ((1,4),(2,5),(3,4),(4,5))]
        remaining=10 if run else 0
        trace.append({'event':label,'AUTO_request':inputs[0], 'hmi_stop':pause,
                      'permission_AUTO':obs[0],'TU_DONG_CHAY':run,'step':step,
                      'proposed_step':proposed,'elapsed_ms':0,'remaining_s':remaining,
                      'pump':any(valves),'valves':valves})
    assert trace[-1]['step']==0 and trace[-1]['remaining_s']==10
    assert not trace[-1]['pump'] and not any(trace[-1]['valves'])
    return trace


def main():
    result={
      'kind':'Kiem chung logic doc lap, khong phai TIA/PLCSIM',
      'source_commit':'aae862c01ddf4d1225ce9127cda915b7a7da8b55',
      'program_files_modified':False,
      'reachable_equivalence':reachable_equivalence(),
      'local_equivalence':contact_equivalence(),
      'display_step_zero_trace':illustrative_trace(),
      'limits':['Khong xac nhan cau hinh FirstScan, thoi gian IEC timer thuc, HMI Events hay day dien.',
                'Gia tri dau vao duoc giu nhat quan trong mot scan mo hinh; khong mo phong ghi bat dong bo/Force giua rung.',
                'Khong co chuong trinh khac ghi de bo nho canh, quyen AUTO hoac timer.',
                'Khong co ket qua kiem thu PLCSIM duoc ghi Dat tu mo hinh nay.']}
    dest=Path(__file__).with_name('ket_qua_logic.json')
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
