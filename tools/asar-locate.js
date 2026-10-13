// Locate known strings in the asar to derive the real data-area base offset.
const fs = require('fs');
const asarPath = 'C:/Users/sf-bc04.SF/AppData/Local/Programs/DeepSeek Harness/resources/app.asar';
const needles = ['name: mcp-client', 'name: dsh-mcp-client', 'dsh-mcp-client/README.md', 'MCP client for dsh'];

const fd = fs.openSync(asarPath, 'r');
const size = fs.fstatSync(fd).size;
const bufs = needles.map((n) => Buffer.from(n, 'latin1'));
const CHUNK = 1 << 24;
let pos = 0;
let carry = Buffer.alloc(0);
const found = needles.map(() => []);
const maxLen = Math.max(...bufs.map((b) => b.length));
while (pos < size) {
  const len = Math.min(CHUNK, size - pos);
  const buf = Buffer.alloc(len);
  fs.readSync(fd, buf, 0, len, pos);
  const hay = Buffer.concat([carry, buf]);
  const base = pos - carry.length;
  bufs.forEach((n, i) => {
    let idx = hay.indexOf(n);
    while (idx !== -1 && found[i].length < 4) {
      found[i].push(base + idx);
      idx = hay.indexOf(n, idx + 1);
    }
  });
  carry = hay.subarray(Math.max(0, hay.length - maxLen));
  pos += len;
}
fs.closeSync(fd);
needles.forEach((n, i) => console.log(n, '->', found[i].join(', ') || 'none'));
