"""Independent conservative URDF OBB audit of recorded executed trajectories.
Each collision primitive/mesh is enclosed by a local box. SAT checks arm boxes
against body/leg boxes; this can flag conservative false positives, never authorizes
passing through the robot. Ground checks transform all box corners to world.
"""
import sys,json,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np,trimesh
from experiments.mink_wholebody.mink_adapter import URDFKinematics,origin,quat_matrix
from taskb_student.constants import URDF_PATH

def separated(ca,ra,ha,cb,rb,hb):
    axes=[*ra.T,*rb.T]
    axes.extend(np.cross(a,b) for a in ra.T for b in rb.T)
    d=cb-ca
    for axis in axes:
        norm=np.linalg.norm(axis)
        if norm<1e-10: continue
        axis=axis/norm
        radius=np.abs(axis@ra)@ha+np.abs(axis@rb)@hb
        if abs(axis@d)>radius+1e-6: return True
    return False

fk=URDFKinematics();boxes={};floor_points={}
for link in fk.tree.findall('link'):
    name=link.get('name');items=[];surface=[]
    for collision in link.findall('collision'):
        geo=collision.find('geometry');shape=next(iter(geo))
        center=np.zeros(3);vertices=None
        if shape.tag=='box': half=np.fromstring(shape.get('size'),sep=' ')/2
        elif shape.tag=='cylinder': half=np.array([float(shape.get('radius'))]*2+[float(shape.get('length'))/2])
        elif shape.tag=='sphere': half=np.ones(3)*float(shape.get('radius'))
        elif shape.tag=='mesh':
            mesh=trimesh.load(URDF_PATH.parent/shape.get('filename'),force='mesh',process=False)
            scale=np.fromstring(shape.get('scale','1 1 1'),sep=' ')
            vertices=np.asarray(mesh.vertices)*scale
            bounds=np.array(mesh.bounds)*scale
            center=bounds.mean(axis=0);half=(bounds[1]-bounds[0])/2
        else: continue
        t=origin(collision);items.append((t[:3,:3]@center+t[:3,3],t[:3,:3],half))
        if vertices is None:
            vertices=np.array(list(itertools.product([-1,1],repeat=3)))*half+center
        surface.append(vertices@t[:3,:3].T+t[:3,3])
    boxes[name]=items;floor_points[name]=np.concatenate(surface) if surface else np.zeros((0,3))
arms=['link02','link03','link04','link05','link06','gripperStator','gripperMover']
obstacles=[name for name in boxes if name in ['base','head_Link','tail_link'] or any(name.startswith(p+'_') for p in ['FR','FL','RR','RL'])]
signs=np.array(list(itertools.product([-1,1],repeat=3)))
reports=[]
directories=[]
for dirname in sys.argv[1:]:
    parent=Path(dirname)
    directories.extend([parent] if (parent/'controller.jsonl').exists() else sorted(parent.glob('trial_*')))
for directory in directories:
    events=[];minimum_floor=100.;tested=0
    rows=[json.loads(s) for s in (directory/'controller.jsonl').read_text().splitlines()]
    # Include every fifth control step, every state transition, and final sample.
    indices=set(range(0,len(rows),5));indices.add(len(rows)-1)
    indices.update(i for i in range(1,len(rows)) if rows[i]['state']!=rows[i-1]['state'])
    for index in sorted(indices):
        row=rows[index];frames=fk.frames(np.array(row['joint_actual']))
        rbase=quat_matrix(row['base_quat']);root=np.array(row['root_position']);world_boxes={}
        for name,items in boxes.items():
            if name not in frames: continue
            f=frames[name];world_boxes[name]=[(f[:3,:3]@c+f[:3,3],f[:3,:3]@r,h) for c,r,h in items]
        for arm in arms:
            for ac,ar,ah in world_boxes.get(arm,[]):
                corners=(signs*ah)@ar.T+ac
                f=frames[arm];wr=rbase@f[:3,:3];wt=root+rbase@f[:3,3]
                floor=float((floor_points[arm]@wr[2,:]+wt[2]).min());minimum_floor=min(minimum_floor,floor)
                if floor<.002: events.append({'time':row['sim_time'],'arm':arm,'obstacle':'ground','minimum_z':floor})
                for obstacle in obstacles:
                    for bc,br,bh in world_boxes.get(obstacle,[]):
                        tested+=1
                        if not separated(ac,ar,ah,bc,br,bh):
                            events.append({'time':row['sim_time'],'arm':arm,'obstacle':obstacle})
    report={'run':str(directory),'sampled_frames':len(indices),'obb_pair_tests':tested,'minimum_arm_ground_clearance_m':minimum_floor,'conservative_overlap_count':len(events),'events':events[:100],'clear':not events,'method':'Exact transformed collision-mesh vertex minimum against ground; conservative local URDF OBBs and 15-axis SAT against body and all leg links. Sampled executed trajectory, fixed mount excluded.'}
    (directory/'path_audit.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True);reports.append(report)
