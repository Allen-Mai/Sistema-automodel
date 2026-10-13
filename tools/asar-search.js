// Search the asar for DSH's own conventions: skill discovery paths and the
// MCP client config field names.
const fs = require('fs');
const asarPath = 'C:/Users/sf-bc04.SF/AppData/Local/Programs/DeepSeek Harness/resources/app.asar';
const needles = [
  'SKILL.md',
  'skills',
  'mcpServers',
  'streamableHttp',
  'streamable-http',
  'mcp.cloudflare.com',
  'serverUrl',
];

const fd = fs.openSync(asarPath, 'r');
const size = fs.fstatSync(fd).size;
const start = 3392064; // data area
const bufs = needles.map((n) => Buffer.from(n, 'latin1'));
const CHUNK = 1 << 24;
let pos = start;
let carry = Buffer.alloc(0);
const counts = needles.map(() => 0);
const samples = needles.map(() => []);
const maxLen = Math.max(...bufs.map((b) => b.length));
while (pos < size) {
  const len = Math.min(CHUNK, size - pos);
  const buf = Buffer.alloc(len);
  fs.readSync(fd, buf, 0, len, pos);
  const hay = Buffer.concat([carry, buf]);
  const base = pos - carry.length;
  bufs.forEach((n, i) => {
    let idx = hay.indexOf(n);
    while (idx !== -1) {
      counts[i]++;
      if (samples[i].length < 3) {
        samples[i].push({ abs: base + idx, ctx: hay.subarray(Math.max(0, idx - 70), idx + 90).toString('latin1').replace(/\s+/g, ' ') });
      }
      idx = hay.indexOf(n, idx + 1);
    }
  });
  carry = hay.subarray(Math.max(0, hay.length - maxLen));
  pos += len;
}
fs.closeSync(fd);
needles.forEach((n, i) => {
  console.log(`\n== ${n} : ${counts[i]} hits`);
  samples[i].forEach((s) => console.log(`   @${s.abs} ...${s.ctx}...`));
});
