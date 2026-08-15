export type Role = "GK" | "LB" | "CB" | "RB" | "CM" | "LW" | "ST" | "RW";
export type Player = { id:string; name:string; country:string; year:number; position:Role; alt:Role[]; club:string; rating:number; stats:{ clubGoals:number; clubAssists:number; trophies:number; cups:number; internationalGoals:number; caps:number } };
export type Squad = { id:string; country:string; year:number; flag:string; players:Player[] };
export type Slot = { id:string; role:Role; label:string };
