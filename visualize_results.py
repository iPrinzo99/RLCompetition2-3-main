"""Create policy maps and a learning curve using Pillow and saved data."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from competition import Model
ROOT=Path(__file__).parent
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n):return ImageFont.truetype(FONT,n)
def map_panel(draw,box,policy,title,gaps=None):
    x,y=box;cell=24
    draw.text((x,y-45),title,font=font(19),fill='black')
    for r in range(20):
        for c in range(20):
            s=20*r+c;xx=x+c*cell;yy=y+r*cell
            if int(policy[s])<0:fill='#333333' if s!=19 else '#C5E5C1'
            else:fill='#FFD7AD' if gaps is not None and gaps[s]>1e-6 else '#FFFFFF'
            draw.rectangle((xx,yy,xx+cell,yy+cell),fill=fill,outline='#D4D4D4')
            if s==19:draw.text((xx+5,yy+3),'G',font=font(16),fill='black');continue
            if int(policy[s])<0:continue
            a=int(policy[s]);cx=xx+12;cy=yy+12;dx,dy=[(0,-7),(7,0),(0,7),(-7,0)][a]
            draw.line((cx-dx/2,cy-dy/2,cx+dx,cy+dy),fill='#333333',width=2)
            tip=(cx+dx,cy+dy)
            if dx:draw.line((tip[0]-np.sign(dx)*4,tip[1]-4,*tip),fill='#333333',width=2);draw.line((tip[0]-np.sign(dx)*4,tip[1]+4,*tip),fill='#333333',width=2)
            else:draw.line((tip[0]-4,tip[1]-np.sign(dy)*4,*tip),fill='#333333',width=2);draw.line((tip[0]+4,tip[1]-np.sign(dy)*4,*tip),fill='#333333',width=2)
    draw.rectangle((x,y+19*cell,x+cell,y+20*cell),outline='#15804A',width=3)

def main():
    data=json.loads((ROOT/'results/results.json').read_text());out=ROOT/'figures';out.mkdir(exist_ok=True)
    ref=np.load(ROOT/'results/reference.npz');m=Model();qstar=ref['q'];selected={}
    img=Image.new('RGB',(1130,1190),'white');draw=ImageDraw.Draw(img)
    for name,box in [('policy_iteration',(55,70)),('value_iteration',(610,70))]:
        p=np.load(ROOT/f'results/{name}.npz')['policy'];map_panel(draw,box,p,name.replace('_',' ').title())
    for alg,box in [('sarsa',(55,655)),('q_learning',(610,655))]:
        group=sorted([x for x in data['runs'] if x['algorithm']==alg and x['exploration']=='fixed'],key=lambda x:x['metrics']['start_gap'])
        run=group[len(group)//2];seed=run['seed'];selected[alg]=seed
        p=np.load(ROOT/f'results/{alg}_fixed_seed{seed}.npz')['policy'];g=np.zeros(400)
        pp=p[m.ids];g[m.ids]=qstar.max(axis=1)-qstar[np.arange(352),np.maximum(pp,0)]
        label='SARSA' if alg=='sarsa' else 'Q-learning'
        title=f'{label}   fixed epsilon   seed {seed}'
        map_panel(draw,box,p,title,g)
    draw.text((55,1150),'Orange = nonoptimal action against exact Q*   Dark = rock   G = goal   Green outline = start',font=font(17),fill='black')
    img.save(out/'policy_comparison.png')
    # Mean exact start value at recorded checkpoints; SD bands shown by vertical bars.
    im=Image.new('RGB',(1250,700),'white');d=ImageDraw.Draw(im);l,t,w,h=100,95,1050,470
    ylo=-100;yhi=35
    def xy(step,val):return (l+(np.log10(step)-4)/2*w,t+(yhi-val)/(yhi-ylo)*h)
    for val in [-100,-75,-50,-25,0,25]:
        yy=xy(10000,val)[1];d.line((l,yy,l+w,yy),fill='#DDDDDD');d.text((l-60,yy-10),str(val),font=font(19),fill='black')
    for step in [10000,50000,1000000]:
        xx=xy(step,0)[0];d.text((xx-35,t+h+14),f'{step:,}',font=font(19),fill='black')
    d.line((l,t,l,t+h,l+w,t+h),fill='black',width=2)
    y=xy(10000,float(ref['value'][m.start]))[1];d.line((l,y,l+w,y),fill='#222222',width=3)
    d.text((l+12,y-28),'Exact optimum 26.2828',font=font(18),fill='black')
    colors=['#2367A6','#E28818','#417E3D','#A24176']
    for color,(mode,alg) in zip(colors,[(a,b) for a in ['fixed','decay'] for b in ['sarsa','q_learning']]):
        runs=[r for r in data['runs'] if r['algorithm']==alg and r['exploration']==mode];points=[]
        for i in range(3):
            step=runs[0]['checkpoints'][i]['steps'];vals=np.array([r['checkpoints'][i]['value_start'] for r in runs]);pt=xy(step,vals.mean());points.append(pt)
            low=xy(step,max(ylo,vals.mean()-vals.std(ddof=1)))[1];high=xy(step,min(yhi,vals.mean()+vals.std(ddof=1)))[1]
            d.line((pt[0],low,pt[0],high),fill=color,width=3);d.ellipse((pt[0]-5,pt[1]-5,pt[0]+5,pt[1]+5),fill=color)
        d.line(points,fill=color,width=3)
    d.text((450,603),'Training transitions on a log scale',font=font(18),fill='black')
    d.text((100,25),'Learning curves    Mean exact greedy start value with one SD over ten training seeds',font=font(25),fill='black')
    for i,((mode,alg),color) in enumerate(zip([(a,b) for a in ['fixed','decay'] for b in ['sarsa','q_learning']],colors)):
        xx=100+(i%2)*540;yy=630+(i//2)*28;d.line((xx,yy+10,xx+30,yy+10),fill=color,width=4);d.text((xx+40,yy),('SARSA' if alg=='sarsa' else 'Q-learning')+'   '+mode+' exploration',font=font(19),fill='black')
    im.save(out/'learning_curves.png');(out/'representative_seeds.json').write_text(json.dumps(selected,indent=2))
    print('Figures saved; representative seeds',selected)

if __name__=='__main__':main()
