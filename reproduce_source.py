"""Reproduce the report from published, author-derived graph inputs. Python 3.10+."""
from pathlib import Path
import csv, json, heapq, math, subprocess, sys
P=Path(__file__).resolve().parent
O=P/'results';O.mkdir(exist_ok=True)

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

edges=read(P/'data/local_metric_edges.csv')
def graph(stairs=True,failed=()):
    a={n:[] for e in edges for n in (e['start'],e['end'])}
    for e in edges:
        if e['serial'] in failed or (e['kind']=='STAIR' and not stairs):continue
        a[e['start']].append((e['end'],float(e['horizontal_m']),e['serial']))
    return a
def shortest(a,s):
    d={s:0.};prev={};q=[(0.,s)]
    while q:
        v,u=heapq.heappop(q)
        if v!=d[u]:continue
        for n,w,serial in a[u]:
            if v+w<d.get(n,math.inf):
                d[n]=v+w;prev[n]=(u,serial);heapq.heappush(q,(v+w,n))
    return d,prev
def route(prev,s,t):
    out=[]
    while t!=s:
        a,e=prev[t];out.append([a,t,e]);t=a
    return out[::-1]
def fw_check(a):
    ns=list(a);ix={n:i for i,n in enumerate(ns)};N=len(ns)
    d=[[0. if i==j else math.inf for j in range(N)] for i in range(N)]
    for u,es in a.items():
        for v,w,_ in es:d[ix[u]][ix[v]]=min(w,d[ix[u]][ix[v]])
    for k in range(N):
        for i in range(N):
            if math.isinf(d[i][k]):continue
            for j in range(N):d[i][j]=min(d[i][j],d[i][k]+d[k][j])
    count=0
    for u in ns:
        ds,_=shortest(a,u)
        for v in ns:
            x=ds.get(v,math.inf);y=d[ix[u]][ix[v]]
            assert (math.isinf(x) and math.isinf(y)) or abs(x-y)<1e-7,(u,v,x,y)
            count+=1
    return count

normal=graph();outage=graph(failed=('0103-814',));checks=0
for st in [True,False]:
    for fail in [(),('0103-813',),('0103-814',),('0103-813','0103-814')]:
        checks+=fw_check(graph(st,fail))

timing=[]
for origin,target,entry in [('TREAD2_BOTTOM_PLUS1','M1','E3_4'),('M1','TREAD2_BOTTOM_PLUS1','E3_5')]:
    d,p=shortest(normal,origin);e,ep=shortest(outage,origin)
    path=route(p,origin,target);assert any(x[2]=='0103-814' for x in path)
    prefix=shortest({u:[v for v in es if not v[2]] for u,es in normal.items()},origin)[0][entry]
    late=prefix+shortest(outage,entry)[0][target]
    timing.append(dict(origin=origin,target=target,normal=d[target],early=e[target],late=late,late_extra=late-e[target],early_path=route(ep,origin,target),normal_path=path))
assert abs(timing[1]['late_extra']-30.41354893781355)<1e-7
assert abs(timing[0]['late_extra']-.3533860764762764)<1e-7

s='TREAD2_BOTTOM_PLUS1';t='M3'
d,p=shortest(normal,s);e,ep=shortest(graph(False),s)
trade=dict(origin=s,target=t,stairs=d[t],no_stairs=e[t],extra=e[t]-d[t],stair_vertical_m=4.4)
assert abs(trade['extra']-8.614186569741165)<1e-7
assert 'TREAD2_BOTTOM_PLUS1' not in shortest(graph(False,('0103-814',)),'M1')[0]

ds=[]
for i in range(4):
    s=f'TREAD{i}_BOTTOM_PLUS1'
    ds.append(shortest(outage,s)[0]['M2']-shortest(normal,s)[0]['M2'])
bounds=dict(lower=min(ds),upper=max(ds),condition='All four upper routes remain available with the same unknown upper walking lengths; stairs permitted; conditional model only.')
assert abs(bounds['lower']-8.203515519955154)<1e-7
assert abs(bounds['upper']-15.621541492240866)<1e-7

for script,args in [('check_access_connector_sensitivity.py',['--el1-b2-access']),('audit_expanded_access_independent.py',[])]:
    subprocess.run([sys.executable,str(P/'research/design_round2'/script),*args],check=True,cwd=P)
maint=json.loads((P/'research/design_round2/expanded_access_maintenance_checks.json').read_text(encoding='utf8'))
result=dict(timing=timing,tradeoff=trade,conditional_bound=bounds,local_Dijkstra_Floyd_checks=checks,maintenance=maint)
(O/'report_values.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':'PASS','local_route_cross_checks':checks,'maintenance_cross_checks':maint['independent_BFS_vs_Warshall'],'late_notice_extra_m':timing[1]['late_extra'],'stair_avoidance_extra_m':trade['extra']},ensure_ascii=False))
