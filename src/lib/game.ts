import { Player, Role, Slot, Squad } from "@/data/types";
export const slots:Slot[]=[{id:"lw",role:"LW",label:"Left wing"},{id:"st",role:"ST",label:"Striker"},{id:"rw",role:"RW",label:"Right wing"},{id:"cm1",role:"CM",label:"Midfield"},{id:"cm2",role:"CM",label:"Midfield"},{id:"cm3",role:"CM",label:"Midfield"},{id:"lb",role:"LB",label:"Left back"},{id:"cb1",role:"CB",label:"Centre back"},{id:"cb2",role:"CB",label:"Centre back"},{id:"rb",role:"RB",label:"Right back"},{id:"gk",role:"GK",label:"Goalkeeper"}];
export const fits=(player:Player,role:Role)=>player.position===role||player.alt.includes(role);
export const availableSlots=(player:Player,xi:Record<string,Player>)=>slots.filter(s=>!xi[s.id]&&fits(player,s.role));
export const drawSquad=(all:Squad[],previous?:string)=>{const pool=all.filter(s=>s.id!==previous);return pool[Math.floor(Math.random()*pool.length)]??all[0]};
export type Result={score:number;tier:string;wins:number;losses:number};
export const calculate=(xi:Record<string,Player>):Result=>{const entries=Object.entries(xi);const avg=entries.reduce((n,[id,p])=>n+p.rating+(fits(p,slots.find(s=>s.id===id)!.role)?0:-4),0)/11;const score=Math.round(avg*10)/10;const [tier,wins]=score>=87?["S",8]:score>=84?["A+",7]:score>=81?["A",6]:score>=78?["B+",5]:score>=75?["B",4]:score>=72?["C",3]:["D",2];return{score,tier,wins,losses:8-wins}};
