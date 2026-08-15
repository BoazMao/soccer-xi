export type Role = "GK" | "LB" | "CB" | "RB" | "CM" | "LW" | "ST" | "RW";
export type Player = { id:string; name:string; country:string; year:number; position:Role; alt:Role[]; club:string; rating:number; ratingSource?:string; sofifaId?:string; stats:{ clubGoals:number|null; clubAssists:number|null; trophies:number|null; cups:number|null; internationalGoals:number|null; caps:number|null } };
export type Squad = { id:string; country:string; year:number; flag:string; players:Player[] };
export type Slot = { id:string; role:Role; label:string; x:number; y:number };
export type FormationId = "4-3-3" | "4-4-2" | "4-2-3-1" | "3-4-3";
export type Formation = { id:FormationId; name:string; description:string; slots:Slot[] };
