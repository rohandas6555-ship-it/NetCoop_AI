from app.config.thresholds import THRESHOLDS

def _num(row, key):
    try: return float(row.get(key))
    except (TypeError, ValueError): return None

def analyze_performance(records):
    findings=[]; evidence=[]; affected=set()
    for r in records:
        device=str(r.get('device_id') or r.get('hostname') or 'unknown-device')
        latency=_num(r,'latency_ms'); jitter=_num(r,'jitter_ms'); loss=_num(r,'packet_loss_pct')
        utilization=_num(r,'link_utilization_pct'); drops=_num(r,'queue_drops')
        if latency is not None and latency >= THRESHOLDS["latency_ms"]:
            findings.append(f'{device}: high latency ({latency:g} ms)'); evidence.append({'device_id':device,'metric':'latency_ms','value':latency,'threshold':THRESHOLDS["latency_ms"]}); affected.add(device)
        if loss is not None and loss >= THRESHOLDS["packet_loss_pct"]:
            findings.append(f'{device}: elevated packet loss ({loss:g}%)'); evidence.append({'device_id':device,'metric':'packet_loss_pct','value':loss,'threshold':THRESHOLDS["packet_loss_pct"]}); affected.add(device)
        if utilization is not None and utilization >= THRESHOLDS["link_utilization_pct"]:
            findings.append(f'{device}: high link utilization ({utilization:g}%)'); evidence.append({'device_id':device,'metric':'link_utilization_pct','value':utilization,'threshold':THRESHOLDS["link_utilization_pct"]}); affected.add(device)
        if jitter is not None and jitter >= THRESHOLDS["jitter_ms"]:
            findings.append(f'{device}: high jitter ({jitter:g} ms)'); evidence.append({'device_id':device,'metric':'jitter_ms','value':jitter,'threshold':THRESHOLDS["jitter_ms"]}); affected.add(device)
        if drops is not None and drops > 0:
            findings.append(f'{device}: queue drops detected ({drops:g})'); evidence.append({'device_id':device,'metric':'queue_drops','value':drops,'threshold':0}); affected.add(device)
    from app.llm.groq_service import analyze_performance_with_groq
    llm_analysis = analyze_performance_with_groq(records, findings, evidence)
    return {'agent':'performance_agent','status':'findings' if findings else 'clear','findings':findings,'evidence':evidence,'affected_devices':sorted(affected),'llm_analysis':llm_analysis}
