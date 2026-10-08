import csv,re,collections,sys
E=list(csv.DictReader(open('data/entries.csv')))
T=list(csv.DictReader(open('data/timetable.csv')))
def n(s): return re.sub(r'\s+',' ',re.sub(r'\s*\(',' (',s.lower().replace('cham kiu','chum kiu').replace('estilo imitacion','estilos de imitación'))).strip(' .')
ev=[]
for i,t in enumerate(T):
    m=re.match(r'Grupo (\w) (Femenino|Masculino) (.*)',t['event'])
    if not m: continue
    rest=m.group(3); kind='Weapon' if re.match(r'Weapon\b',rest) else 'Barehand' if re.match(r'Barehand\b',rest) else ('Weapon' if 'weapon' in rest.lower() else 'Barehand')
    core=re.sub(r'^(Barehand|Weapon)\s+','',rest); core=n(re.sub(r'\((un|Un)ified\)|\bUnified\b|\bunified\b','',core))
    core=re.sub(r'\s*\(\s*\)','',core).strip()
    ev.append(dict(i=i,group='Group '+m.group(1),gender='Female' if m.group(2)=='Femenino' else 'Male',kind=kind,core=core,count=int(t['count'])))
SH_S={'shaolin dao','shaolin jian','other shaolin short weapons'}
SH_L={'shaolin staff','shaolin spear','other shaolin long weapons'}
LONG={'gun (cudgel/staff)','qiang (spear)','pudao','guandao (kwan dao)'}
SHORT={'dao (broadsword)','jian (straight sword)'}
SOUTH={'nandao (southern broadsword)','nangun (southern staff/cudgel)'}
def ekind(r): return 'Barehand' if r['type']=='Barehand' else 'Weapon'
def score(r,e):
    s=n(r['style']); c=e['core']; cat=n(r['category'])
    if s==c: return 100
    if len(c)>=5 and (c in s or s in c): return 80
    if 'nine-section' in s and 'jiujiebian' in c: return 60
    if s=='42-posture taijijian' and 'taijijian' in c: return 55
    if s=='dao (broadsword)' and c=='single weapon dao': return 90
    tj = s.startswith('taiji') or 'taijijian' in s
    if tj and 'taiji' in c: return 50
    if not tj:
        if 'shaolin' in c and 'short' in c and s in SH_S: return 50
        if 'shaolin' in c and 'long' in c and s in SH_L: return 50
        if 'shaolin' not in c and 'long' in c and s in LONG: return 50
        if 'shaolin' not in c and 'short' in c and s in SHORT: return 50
        if 'southern' in c and s in SOUTH: return 50
    if 'nine-section' in s and 'flexible' in c: return 40
    if not tj and 'shaolin' not in c and 'long' in c and s in SH_L: return 45
    if not tj and 'shaolin' not in c and 'short' in c and s in SH_S: return 45
    if cat=='shaolinquan routines' and 'shaolin' in c and 'shaolinquan' not in c: return 25
    if cat=='taijiquan routines': return 30 if 'taijiquan' in c and not re.match(r'(24|42|chen|yang) ',c) else 0
    for k in ['double-weapon','flexible','nanquan-type','other northern','shaolinquan']:
        if k in cat and k in c: return 30
    if cat.startswith('shaolin weapon') and c=='shaolin weapon routines': return 30
    if cat.startswith('single-weapon') and c=='single-weapon routines' and not tj: return 20
    if cat.startswith('single-weapon') and c=='other single weapons' and not tj: return 15
    return 0
asg={};amb=[];alts={}
for j,r in enumerate(E):
    cands=[(score(r,e),e) for e in ev if e['group']==r['group'] and e['gender']==r['gender'] and e['kind']==ekind(r)]
    cands=[c for c in cands if c[0]>0]
    if not cands: continue
    best=max(c[0] for c in cands); top=[e for sc,e in cands if sc==best]
    if len(top)>1: amb.append((r['group'],r['gender'],r['style'],[e['core'] for e in top]))
    asg[j]=top[0]; alts[j]=top
cnt=collections.Counter(e['i'] for e in asg.values())
print("UNMATCHED:"); [print(' ',r['group'],r['gender'],r['type'],r['category'],'|',r['style'],'|',r['athlete']) for j,r in enumerate(E) if j not in asg]
print("AMBIG:",sorted(set((a,b,c,tuple(d)) for a,b,c,d in amb)))
print("COUNT MISMATCH (pdf vs roster):")
for e in ev:
    if e['group']<'Group E' and cnt[e['i']]!=e['count']:
        print(f"  {T[e['i']]['day']} {T[e['i']]['start']} {e['group']} {e['gender']} {e['core']}: pdf {e['count']} roster {cnt[e['i']]} ->", sorted(set(E[j]['style'] for j,x in asg.items() if x is e)))
print('matched',len(asg),'of',len(E))

def key(e): return (T[e['i']]['day'],T[e['i']]['fop'],e['group'],e['gender'],e['kind'])
over={e['i'] for e in ev if cnt[e['i']]>e['count']+1}
def window(e):
    lo,hi=e['i'],e['i']; wid=False
    if e['i'] in over:
        for d in (-1,1):
            k=e['i']+d
            nb=next((x for x in ev if x['i']==k),None)
            if nb and key(nb)==key(e) and cnt[k]<=nb['count']-2: lo,hi=min(lo,k),max(hi,k); wid=True
    return lo,hi,wid
if len(sys.argv)>1:
    for j,r in enumerate(E):
        e=asg.get(j); note=''
        if e:
            tops=[x for x in alts.get(j,[e]) if key(x)==key(e)]
            lo=min(x['i'] for x in tops); hi=max(x['i'] for x in tops)
            a,b,wid=window(e); lo,hi=min(lo,a),max(hi,b)
            if lo!=hi or wid: note='Combined event in the timetable; could be anywhere in this window'
            r.update(ev_day=T[lo]['day'],ev_fop=T[lo]['fop'],ev_start=T[lo]['start'],ev_end=T[hi]['end'],ev_name=T[e['i']]['event'],ev_note=note)
        else:
            r.update(ev_day='',ev_fop='',ev_start='',ev_end='',ev_name='',ev_note='')
    with open('data/entries.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(E[0]));w.writeheader();w.writerows(E)
