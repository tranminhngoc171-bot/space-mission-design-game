
const { STRINGS } = await import('file://' + process.argv[1].replace(/\\/g,'/'));
const vi = Object.keys(STRINGS.vi), en = Object.keys(STRINGS.en);
const fv = vi.filter(k=>k.startsWith('flight.')), fe = en.filter(k=>k.startsWith('flight.'));
console.log('flight vi', fv.length, 'en', fe.length);
console.log('missing in en', fv.filter(k=>!en.includes(k)));
console.log('missing in vi', fe.filter(k=>!vi.includes(k)));
const all=[...vi,...en]; const dup=[];
console.log('total keys', vi.length, en.length);
// em dash check
for (const l of ['vi','en']) for (const k of Object.keys(STRINGS[l])) {
  const s = STRINGS[l][k];
  if (typeof s === 'string' && (s.includes('\u2014') || s.includes('\u2013'))) console.log('DASH', l, k);
}
for (const k of fv) console.log(k, '|', STRINGS.vi[k]);
