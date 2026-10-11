import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='C:/AnalogueGames/aphelion-deep';
const matrix=JSON.parse(await fs.readFile(root+'/provenance/card-table.json','utf8'));
const wb=Workbook.create();
const col=n=>{let x='';for(n++;n;n=Math.floor((n-1)/26))x=String.fromCharCode(65+(n-1)%26)+x;return x};
function add(name,rows){const s=wb.worksheets.add(name);const end=col(rows[0].length-1);s.getRange(`A1:${end}${rows.length}`).values=rows;s.showGridLines=false;
s.getRange(`A1:${end}${rows.length}`).format={font:{name:'Calibri',size:11,color:'#142D39'},columnWidth:26,rowHeight:32,wrapText:true,verticalAlignment:"top"};
s.getRange(`A1:${end}1`).format={fill:'#163E4A',font:{bold:true,color:'#FFFFFF'},rowHeight:44};s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(2);
return s;}
const s=add('Cards',matrix);s.getRange('B:B').format.columnWidth=34;s.getRange('K:L').format.columnWidth=85;s.getRange('R:R').format.columnWidth=65;
for(let i=1;i<matrix.length;i++){const length=Math.max(...matrix[i].map(x=>String(x).length));s.getRange(`A${i+1}:${col(matrix[0].length-1)}${i+1}`).format.rowHeight=Math.min(400,Math.max(110,Math.ceil(length/75)*17+90));}
const pacing=await fs.readFile(root+'/design/legacy-pacing.md','utf8');
const p=add('Pacing',[['ID','Name','Status','Text'],...pacing.split(/\r?\n(?:\r?\n)+/).map((v,i)=>['ad-pacing-'+(i+1),'Original pacing '+(i+1),'working',v])]);p.getRange('D:D').format.columnWidth=110;p.getRange('A2:D60').format.rowHeight=140;
const maps=JSON.parse(await fs.readFile(root+'/provenance/map-reconciliation.json','utf8'));
add('Map Names',[['ID','Name','Status','Source','Decision'],...maps.prose_locations.map((n,i)=>['ad-prose-location-'+(i+1),n,'working','Outline','Unresolved artwork correspondence']),...maps.artwork_labels.map((n,i)=>['ad-map-label-'+(i+1),n,'working','AD_Mat.png','Unresolved prose correspondence'])]);
wb.recalculate();console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(root+'/.staging/card-catalogue.xlsx');
const img=await wb.render({sheetName:'Cards',range:'A1:D4',scale:1,format:'png'});await fs.writeFile(root+'/.staging/cards-preview.png',new Uint8Array(await img.arrayBuffer()));
