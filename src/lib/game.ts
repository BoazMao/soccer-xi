import { Formation, FormationId, Player, Role, Slot, Squad } from "@/data/types";
const slot=(id:string,role:Role,label:string,x:number,y:number):Slot=>({id,role,label,x,y});
export const formations:Record<FormationId,Formation>={
 "4-3-3":{id:"4-3-3",name:"4 · 3 · 3",description:"Width and control",slots:[slot("lw","LW","Left wing",18,15),slot("st","ST","Striker",50,12),slot("rw","RW","Right wing",82,15),slot("cm1","CM","Midfield",25,42),slot("cm2","CM","Midfield",50,47),slot("cm3","CM","Midfield",75,42),slot("lb","LB","Left back",12,72),slot("cb1","CB","Centre back",37,68),slot("cb2","CB","Centre back",63,68),slot("rb","RB","Right back",88,72),slot("gk","GK","Goalkeeper",50,90)]},
 "4-4-2":{id:"4-4-2",name:"4 · 4 · 2",description:"Classic and balanced",slots:[slot("st1","ST","Striker",36,15),slot("st2","ST","Striker",64,15),slot("lw","LW","Left midfield",12,45),slot("cm1","CM","Central midfield",38,45),slot("cm2","CM","Central midfield",62,45),slot("rw","RW","Right midfield",88,45),slot("lb","LB","Left back",12,72),slot("cb1","CB","Centre back",37,68),slot("cb2","CB","Centre back",63,68),slot("rb","RB","Right back",88,72),slot("gk","GK","Goalkeeper",50,90)]},
 "4-2-3-1":{id:"4-2-3-1",name:"4 · 2 · 3 · 1",description:"Layers between the lines",slots:[slot("st","ST","Striker",50,10),slot("lw","LW","Left attack",18,34),slot("cam","CM","Attacking midfield",50,32),slot("rw","RW","Right attack",82,34),slot("cm1","CM","Holding midfield",35,55),slot("cm2","CM","Holding midfield",65,55),slot("lb","LB","Left back",12,76),slot("cb1","CB","Centre back",37,72),slot("cb2","CB","Centre back",63,72),slot("rb","RB","Right back",88,76),slot("gk","GK","Goalkeeper",50,92)]},
 "3-4-3":{id:"3-4-3",name:"3 · 4 · 3",description:"Brave and aggressive",slots:[slot("lw1","LW","Left wing",18,14),slot("st","ST","Striker",50,10),slot("rw1","RW","Right wing",82,14),slot("lw2","LW","Left midfield",10,47),slot("cm1","CM","Central midfield",37,48),slot("cm2","CM","Central midfield",63,48),slot("rw2","RW","Right midfield",90,47),slot("cb1","CB","Centre back",25,72),slot("cb2","CB","Centre back",50,68),slot("cb3","CB","Centre back",75,72),slot("gk","GK","Goalkeeper",50,91)]}
};
export const formationList=Object.values(formations);
export const fits=(player:Player,role:Role)=>player.position===role||player.alt.includes(role);
export const availableSlots=(player:Player,xi:Record<string,Player>,slots:Slot[])=>slots.filter(s=>!xi[s.id]&&fits(player,s.role));
export const drawSquad=(all:Squad[],previous?:string)=>{const pool=all.filter(s=>s.id!==previous);return pool[Math.floor(Math.random()*pool.length)]??all[0]};
export type Finish="champions"|"final"|"semifinal"|"quarterfinal"|"knockouts"|"group"|"qualifying"|"preliminary";
export type WeakestLink={player:Player;slot:Slot;impact:number;effectiveRating:number;secondary:boolean;status:"weak-link"|"vulnerable"|"balanced"};
export type Result={score:number;attack:number;defense:number;tier:string;finish:Finish;weakest:WeakestLink;imbalance:"attack"|"defense"|"balanced"};
export const scoringConfig={
 roleWeight:{GK:1.15,LB:1,CB:1.05,RB:1,CM:1.05,LW:1.1,ST:1.2,RW:1.1} satisfies Record<Role,number>,
 secondaryPositionPenalty:1.25,
 thresholds:[
  {minimum:85,tier:"S+",finish:"champions"},{minimum:84,tier:"A+",finish:"final"},
  {minimum:83,tier:"A",finish:"semifinal"},{minimum:81.5,tier:"B+",finish:"quarterfinal"},
  {minimum:79.5,tier:"B",finish:"knockouts"},{minimum:77,tier:"C",finish:"group"},
  {minimum:74,tier:"D",finish:"qualifying"},{minimum:-Infinity,tier:"F",finish:"preliminary"}
 ] as {minimum:number;tier:string;finish:Finish}[]
};
const round=(value:number)=>Math.round(value*10)/10;
const weightedAverage=(values:{value:number;weight:number}[])=>values.reduce((sum,item)=>sum+item.value*item.weight,0)/values.reduce((sum,item)=>sum+item.weight,0);
const clamp=(value:number,min:number,max:number)=>Math.min(max,Math.max(min,value));
const internationalAdjustment=(player:Player)=>{
 const caps=player.stats.caps==null?0:clamp((player.stats.caps-45)/90,-.35,.65);
 const goalScale=player.position==="ST"||player.position==="LW"||player.position==="RW"?28:player.position==="CM"?45:100;
 const goals=player.stats.internationalGoals==null?0:clamp(player.stats.internationalGoals/goalScale,0,1.1);
 return caps+goals+(/\(c\)$/i.test(player.name)?.2:0);
};
export const calculate=(xi:Record<string,Player>,slots:Slot[]):Result=>{
 const entries=Object.entries(xi).map(([id,player])=>{const assignedSlot=slots.find(item=>item.id===id)!;const secondary=player.position!==assignedSlot.role;const effectiveRating=player.rating+internationalAdjustment(player)-(secondary?scoringConfig.secondaryPositionPenalty:0);return{player,slot:assignedSlot,secondary,effectiveRating,weight:scoringConfig.roleWeight[assignedSlot.role]}});
 const weightedXI=weightedAverage(entries.map(item=>({value:item.effectiveRating,weight:item.weight})));
 const attacking=entries.map(item=>({value:item.effectiveRating,weight:["ST","LW","RW"].includes(item.slot.role)?1:item.slot.role==="CM"?.25:0})).filter(item=>item.weight);
 const defending=entries.map(item=>({value:item.effectiveRating,weight:["GK","LB","CB","RB"].includes(item.slot.role)?1:item.slot.role==="CM"?.25:0})).filter(item=>item.weight);
 const attack=weightedAverage(attacking);const defense=weightedAverage(defending);
 const impacts=entries.map(item=>({...item,impact:Math.max(0,weightedXI-item.effectiveRating)*item.weight+(item.secondary?.75:0)})).sort((a,b)=>b.impact-a.impact);
 const largestImpact=impacts[0]?.impact??0;const weakPenalty=largestImpact*.22+impacts.slice(1,3).reduce((sum,item)=>sum+item.impact*.06,0);
 const imbalanceGap=Math.abs(attack-defense);const score=round(weightedXI-weakPenalty-Math.max(0,imbalanceGap-4)*.1);
 const outcome=scoringConfig.thresholds.find(item=>score>=item.minimum)!;const weakestEntry=impacts[0];const status=largestImpact>=4?"weak-link":largestImpact>=2?"vulnerable":"balanced";
 return{score,attack:round(attack),defense:round(defense),tier:outcome.tier,finish:outcome.finish,weakest:{player:weakestEntry.player,slot:weakestEntry.slot,impact:round(largestImpact),effectiveRating:round(weakestEntry.effectiveRating),secondary:weakestEntry.secondary,status},imbalance:imbalanceGap<3?"balanced":attack>defense?"defense":"attack"};
};
