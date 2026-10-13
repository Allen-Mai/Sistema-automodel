// Extract the MCP template bundle files and the plugin-development skill by
// locating them through the asar directory and reading at base + offset.
const fs = require('fs');
const asarPath = 'C:/Users/sf-bc04.SF/AppData/Local/Programs/DeepSeek Harness/resources/app.asar';
const targets = [
  'node_modules/@deepseek-ai/dsh-agent-preset/skills/cordis-plugin-development/templates/mcp/cordis.patch.yml',
  'node_modules/@deepseek-ai/dsh-agent-preset/skills/cordis-plugin-development/templates/mcp/package.json',
  'node_modules/@deepseek-ai/dsh-agent-preset/skills/cordis-plugin-development/SKILL.md',
];

const fd = fs.openSync(asarPath, 'r');
const sizeBuf = Buffer.alloc(8);
fs.readSync(fd, sizeBuf, 0, 8, 0);
const payloadSize = sizeBuf.readUInt32LE(4);
const jsonBuf = Buffer.alloc(payloadSize);
fs.readSync(fd, jsonBuf, 0, payloadSize, 16);
const text = jsonBuf.toString('utf8');
const json = text.slice(0, text.lastIndexOf('}') + 1);
const header = JSON.parse(json);
const headerLen = Buffer.byteLength(json, 'utf8');
const base = 16 + headerLen;

function walk(node, prefix, out) {
  for (const [name, entry] of Object.entries(node.files || {})) {
    const p = prefix + '/' + name;
    if (entry.files) walk(entry, p, out);
    else out.push({ path: p.replace(/^\//, ''), size: entry.size, offset: Number(entry.offset) });
  }
  return out;
}
const all = walk(header, '', []);
console.log('base =', base, ' total entries =', all.length);

for (const t of targets) {
  const e = all.find((x) => x.path === t);
  if (!e) {
    console.log('\n### MISSING', t);
    continue;
  }
  const b = Buffer.alloc(e.size);
  fs.readSync(fd, b, 0, e.size, base + e.offset);
  console.log('\n' + '='.repeat(70));
  console.log('### ' + t + '  (size ' + e.size + ', offset ' + e.offset + ')');
  console.log('='.repeat(70));
  console.log(b.toString('utf8'));
}
fs.closeSync(fd);
