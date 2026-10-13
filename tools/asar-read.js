// Minimal read-only asar inspector: list entries and extract named files.
// Usage: node asar-read.js list <asarPath> <substring>
//        node asar-read.js get  <asarPath> <archivePath> [outFile]
const fs = require('fs');

const [, , cmd, asarPath, arg3, arg4] = process.argv;

function readHeader(fd) {
  // asar layout: [0..3] uint32 = 4, [4..7] uint32 = pickle payload size,
  // then the pickle payload whose string length is a uint32 followed by the
  // JSON directory. Empirically the JSON starts at byte 16 and the file data
  // area begins at 8 + payloadSize.
  const sizeBuf = Buffer.alloc(8);
  fs.readSync(fd, sizeBuf, 0, 8, 0);
  const payloadSize = sizeBuf.readUInt32LE(4);
  const jsonBuf = Buffer.alloc(payloadSize);
  fs.readSync(fd, jsonBuf, 0, payloadSize, 16);
  const text = jsonBuf.toString('utf8');
  const end = text.lastIndexOf('}');
  const json = text.slice(0, end + 1);
  // The data area is padded so the directory length lands on a 4-byte boundary.
  const headerLength = Buffer.byteLength(json, 'utf8');
  const alignedLength = headerLength % 4 === 0 ? headerLength : headerLength + (4 - (headerLength % 4));
  return { header: JSON.parse(json), baseOffset: 16 + alignedLength };
}

const fd = fs.openSync(asarPath, 'r');
const { header, baseOffset } = readHeader(fd);

function walk(node, prefix, out) {
  for (const [name, entry] of Object.entries(node.files || {})) {
    const p = prefix + '/' + name;
    if (entry.files) walk(entry, p, out);
    else out.push({ path: p, size: entry.size || 0, offset: entry.offset, unpacked: !!entry.unpacked });
  }
  return out;
}

if (cmd === 'list') {
  const needle = (arg3 || '').toLowerCase();
  const all = walk(header, '', []);
  const hits = all.filter((e) => e.path.toLowerCase().includes(needle));
  for (const h of hits) console.log(`${String(h.size).padStart(9)}  ${h.path}${h.unpacked ? '  [unpacked]' : ''}`);
  console.log(`--- matched ${hits.length} of ${all.length} ---`);
} else if (cmd === 'get') {
  const target = arg3;
  const all = walk(header, '', []);
  const entry = all.find((e) => e.path === target || e.path === '/' + target);
  if (!entry) {
    console.error('NOT FOUND: ' + target);
    process.exit(2);
  }
  let data;
  if (entry.unpacked) {
    data = fs.readFileSync(asarPath + '.unpacked' + entry.path);
  } else {
    const buf = Buffer.alloc(entry.size);
    fs.readSync(fd, buf, 0, entry.size, baseOffset + Number(entry.offset));
    data = buf;
  }
  if (arg4) {
    fs.writeFileSync(arg4, data);
    console.log(`wrote ${data.length} bytes -> ${arg4}`);
  } else {
    process.stdout.write(data);
  }
} else {
  console.error('usage: list|get');
  process.exit(1);
}
fs.closeSync(fd);
