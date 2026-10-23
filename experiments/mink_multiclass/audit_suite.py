"""Audit each completed case once, without adding simulation attempts."""
import argparse,json,subprocess,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output if a.output.is_absolute() else ROOT/a.output
cases=json.loads((ROOT/'experiments/mink_multiclass/suite.json').read_text())['cases']
started=time.monotonic()
for case in cases:
 name=case['case_id'];marker=out/(name+'.completed.json')
 while not marker.exists():
  if time.monotonic()-started>4800:raise SystemExit('Audit wait limit')
  time.sleep(2.)
 directory=out/name;trial=directory/'trial_01'
 if not (trial/'result.json').exists():continue
 with (out/(name+'.audit.log')).open('w') as log:
  r=subprocess.run(['/isaac-sim/python.sh',str(ROOT/'experiments/mink_wholebody/path_audit.py'),str(trial)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180.)
 print('[AUDIT]',name,r.returncode,flush=True)
print('[AUDITS_COMPLETE]',flush=True)
