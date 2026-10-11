import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='C:/AnalogueGames/aphelion-deep';
const tables=JSON.parse(await fs.readFile(root+'/provenance/project-tables.json','utf8'));
const wb=Workbook.create();const col=n=>String.fromCharCode(64+n);
for(const [name,rows] of Object.entries(tables)){
 const s=wb.worksheets.add(name),end=col(rows[0].length);s.getRange(`A1:${end}${rows.length}`).values=rows;s.showGridLines=false;
 s.getRange(`A1:${end}${rows.length}`).format={font:{name:'Calibri',size:11,color:'#14303C'},columnWidth:40,rowHeight:100,wrapText:true,verticalAlignment:'top'};
 s.getRange(`A1:${end}1`).format={fill:'#163E4A',font:{bold:true,color:'#FFFFFF'},rowHeight:32};s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(1);
 if(name==='Sources'){s.getRange('B:B').format.columnWidth=75;s.getRange('G:G').format.columnWidth=65;}
 if(name==='Gaps'){s.getRange('E:E').format.columnWidth=100;s.getRange('B:B').format.columnWidth=10;}
}
wb.recalculate();console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:1000})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(root+'/.staging/project-manifest.xlsx');
const img=await wb.render({sheetName:'Manifest',range:'A1:D4',scale:1,format:'png'});await fs.writeFile(root+'/.staging/manifest-preview.png',new Uint8Array(await img.arrayBuffer()));
