import { Player, Role, Squad } from "./types";
import generatedSquads from "./generatedSquads.json";

type Seed = [string, Role, string, number, Role[]?];
const make = (country:string, year:number, rows:Seed[]):Player[] => rows.map(([name,position,club,rating,alt],i) => ({
  id:`${country}-${year}-${i}`, name,country,year,position,club,rating,alt:alt??[],
  stats:{ clubGoals: Math.max(0, Math.round((rating-68)*(i%5+1)*1.7)), clubAssists:Math.max(0,Math.round((rating-70)*(i%4+1)*1.15)), trophies:Math.max(0,Math.round((rating-72)/3)+(i%3)), cups:Math.max(0,Math.round((rating-73)/5)), internationalGoals: position==="GK"?0:Math.max(0,Math.round((rating-72)*(i%4)/3)), caps:Math.max(1,Math.round((rating-66)*(i%3+2))) }
}));

const curatedSquads:Squad[] = [
 {id:"esp-2010",country:"Spain",year:2010,flag:"🇪🇸",players:make("Spain",2010,[
  ["Iker Casillas","GK","Real Madrid",90],["Pepe Reina","GK","Liverpool",84],["Víctor Valdés","GK","Barcelona",84],
  ["Joan Capdevila","LB","Villarreal",80],["Carles Puyol","CB","Barcelona",86],["Gerard Piqué","CB","Barcelona",84],["Raúl Albiol","CB","Real Madrid",81],["Carlos Marchena","CB","Valencia",81],["Sergio Ramos","RB","Real Madrid",86,["CB"]],["Álvaro Arbeloa","RB","Real Madrid",79,["LB"]],
  ["Xabi Alonso","CM","Real Madrid",87],["Sergio Busquets","CM","Barcelona",82],["Cesc Fàbregas","CM","Arsenal",86],["Andrés Iniesta","CM","Barcelona",89,["LW"]],["Javi Martínez","CM","Athletic Club",80],["Juan Mata","LW","Valencia",82,["CM"]],["David Silva","CM","Valencia",86,["LW"]],["Xavi","CM","Barcelona",90],
  ["Jesús Navas","RW","Sevilla",82],["Pedro","RW","Barcelona",81,["LW"]],["Fernando Llorente","ST","Athletic Club",81],["Fernando Torres","ST","Liverpool",88],["David Villa","ST","Valencia",88,["LW"]]
 ])},
 {id:"ger-2014",country:"Germany",year:2014,flag:"🇩🇪",players:make("Germany",2014,[
  ["Manuel Neuer","GK","Bayern Munich",90],["Roman Weidenfeller","GK","Borussia Dortmund",83],["Ron-Robert Zieler","GK","Hannover 96",79],
  ["Jérôme Boateng","CB","Bayern Munich",83,["RB"]],["Erik Durm","LB","Borussia Dortmund",73,["RB"]],["Kevin Großkreutz","RB","Borussia Dortmund",77,["CM"]],["Benedikt Höwedes","CB","Schalke 04",82,["LB"]],["Mats Hummels","CB","Borussia Dortmund",85],["Philipp Lahm","RB","Bayern Munich",87,["CM"]],["Per Mertesacker","CB","Arsenal",83],["Shkodran Mustafi","CB","Sampdoria",76,["RB"]],
  ["Julian Draxler","CM","Schalke 04",80,["LW"]],["Mario Götze","CM","Bayern Munich",85,["RW"]],["Sami Khedira","CM","Real Madrid",84],["Christoph Kramer","CM","Borussia Mönchengladbach",76],["Toni Kroos","CM","Bayern Munich",85],["Mesut Özil","CM","Arsenal",86,["RW"]],["Bastian Schweinsteiger","CM","Bayern Munich",88],
  ["Matthias Ginter","CB","Freiburg",74,["CM"]],["Miroslav Klose","ST","Lazio",81],["Thomas Müller","RW","Bayern Munich",86,["ST"]],["Lukas Podolski","LW","Arsenal",83,["ST"]],["André Schürrle","LW","Chelsea",81,["RW"]]
 ])},
 {id:"fra-2018",country:"France",year:2018,flag:"🇫🇷",players:make("France",2018,[
  ["Hugo Lloris","GK","Tottenham Hotspur",88],["Steve Mandanda","GK","Marseille",83],["Alphonse Areola","GK","Paris Saint-Germain",81],
  ["Lucas Hernández","LB","Atlético Madrid",80,["CB"]],["Presnel Kimpembe","CB","Paris Saint-Germain",83],["Benjamin Mendy","LB","Manchester City",81],["Benjamin Pavard","RB","Stuttgart",79,["CB"]],["Adil Rami","CB","Marseille",79],["Djibril Sidibé","RB","Monaco",81],["Samuel Umtiti","CB","Barcelona",87],["Raphaël Varane","CB","Real Madrid",86],
  ["N'Golo Kanté","CM","Chelsea",89],["Blaise Matuidi","CM","Juventus",85,["LW"]],["Steven Nzonzi","CM","Sevilla",81],["Paul Pogba","CM","Manchester United",88],["Corentin Tolisso","CM","Bayern Munich",83],
  ["Nabil Fekir","CM","Lyon",85,["RW"]],["Olivier Giroud","ST","Chelsea",82],["Antoine Griezmann","ST","Atlético Madrid",88,["RW"]],["Thomas Lemar","LW","Monaco",83],["Kylian Mbappé","RW","Paris Saint-Germain",87,["ST"]],["Florian Thauvin","RW","Marseille",84],["Ousmane Dembélé","RW","Barcelona",83,["LW"]]
 ])},
 {id:"arg-2022",country:"Argentina",year:2022,flag:"🇦🇷",players:make("Argentina",2022,[
  ["Emiliano Martínez","GK","Aston Villa",84],["Franco Armani","GK","River Plate",79],["Gerónimo Rulli","GK","Villarreal",81],
  ["Marcos Acuña","LB","Sevilla",85],["Juan Foyth","RB","Villarreal",80,["CB"]],["Lisandro Martínez","CB","Manchester United",84,["LB"]],["Nahuel Molina","RB","Atlético Madrid",78],["Gonzalo Montiel","RB","Sevilla",79],["Nicolás Otamendi","CB","Benfica",81],["Germán Pezzella","CB","Real Betis",78],["Cristian Romero","CB","Tottenham Hotspur",83],["Nicolás Tagliafico","LB","Lyon",81],
  ["Thiago Almada","CM","Atlanta United",76],["Rodrigo De Paul","CM","Atlético Madrid",84],["Enzo Fernández","CM","Benfica",80],["Alexis Mac Allister","CM","Brighton",78],["Exequiel Palacios","CM","Bayer Leverkusen",80],["Leandro Paredes","CM","Juventus",81],["Guido Rodríguez","CM","Real Betis",81],
  ["Julián Álvarez","ST","Manchester City",79,["RW"]],["Ángel Correa","RW","Atlético Madrid",83,["ST"]],["Ángel Di María","RW","Juventus",84,["LW"]],["Paulo Dybala","ST","Roma",86,["RW"]],["Alejandro Gómez","LW","Sevilla",84,["CM"]],["Lautaro Martínez","ST","Inter Milan",86],["Lionel Messi","RW","Paris Saint-Germain",91,["ST"]]
 ])}
];

const curatedIds = new Set(curatedSquads.map(squad => squad.id));
export const squads:Squad[] = [
 ...curatedSquads,
 ...(generatedSquads as Squad[]).filter(squad => !curatedIds.has(squad.id)),
].sort((a,b)=>a.year-b.year||a.country.localeCompare(b.country));
