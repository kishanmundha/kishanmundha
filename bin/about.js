#!/usr/bin/env node

/**
 * The profile, as a terminal session. Zero dependencies.
 *
 *   node bin/about.js              wide layout  (~76 cols)
 *   node bin/about.js --narrow     phone layout (~36 cols, restructured)
 *
 * Narrow is a different layout, not a smaller one: columns collapse into
 * stacked rows and copy shortens. Edit once here, run ./build.sh, both ship.
 */

const NARROW = process.argv.includes('--narrow');
const WIDTH = NARROW ? 36 : 76;

// ── ansi ────────────────────────────────────────────────────────────────────
const color = process.env.NO_COLOR
  ? false
  : process.stdout.isTTY || process.env.FORCE_COLOR;

const p = (code) => (s) => (color ? `\x1b[${code}m${s}\x1b[0m` : String(s));
const ink = p('97');
const grey = p('38;5;245');
const dim = p('38;5;240');
const amber = p('38;5;179');
const teal = p('38;5;79');
const bold = p('1');

const vis = (s) => s.replace(/\x1b\[[0-9;]*m/g, '');
const len = (s) => [...vis(s)].length;
const pad = (s, n) => s + ' '.repeat(Math.max(0, n - len(s)));

const out = [];
const line = (s = '') => out.push(s);

/** Wrap prose to the column budget so it's authored once, not twice. */
const wrap = (text, width) => {
  const lines = [];
  let cur = '';
  for (const w of text.split(' ')) {
    if (cur && [...cur, ' ', ...w].length > width) {
      lines.push(cur);
      cur = w;
    } else cur = cur ? `${cur} ${w}` : w;
  }
  if (cur) lines.push(cur);
  return lines;
};
const para = (text, tone) =>
  wrap(text, WIDTH - 4).forEach((l) => line(`    ${tone(l)}`));

// ── blocks ──────────────────────────────────────────────────────────────────
const ask = (wide, narrow) => {
  line();
  line(`${teal(bold('\u276f'))} ${ink(NARROW ? narrow : wide)}`);
  line();
};

/**
 * A carriage return is how a terminal overwrites in place. Printed live you
 * see "thinking" replaced by the elapsed time; the SVG renderer cross-fades
 * the two at the same line.
 */
const think = (took) => {
  line(
    `  ${amber('\u25c7')} ${grey('thinking')}\r  ${amber('\u25c7')} ${dim(`thought for ${took}`)}`,
  );
  line();
};

const call = (fn, args, ms) => {
  const left = NARROW
    ? `  ${dim('\u22c5')} ${grey(fn)}`
    : `  ${dim('\u22c5')} ${grey(fn)} ${dim(args)}`;
  line(`${pad(left, WIDTH - 9)}${teal('\u2713')} ${dim(ms)}`);
  line();
};

// ── 1. who ──────────────────────────────────────────────────────────────────
ask('who is kishan mundha?', 'who is kishan?');
think('1.2s');
call('get_profile', '{}', '40ms');
line(`    ${bold(ink('Kishan Mundha'))}`);
line();
para('Building apps since 2013 to make things a little better.', teal);
line();
para(
  'Full-stack engineer and consultant. I turn messy business problems into ' +
    'software that holds up \u2014 lately, admin platforms that render themselves ' +
    'from a schema, and the agents that operate them.',
  grey,
);

// ── 2. stack ────────────────────────────────────────────────────────────────
ask('what does he work with?', 'what does he use?');
call('get_stack', '{}', '65ms');

const STACK = [
  ['languages', ['typescript', 'javascript', 'python', 'c#']],
  ['frontend', ['react', 'next.js', 'expo']],
  ['backend', ['node', 'postgres', 'docker']],
  ['ai', ['vercel ai sdk', 'mcp', 'ollama']],
];

STACK.forEach(([label, items]) => {
  if (NARROW) {
    line(`    ${dim(label)}`);
    // wrap to the column budget instead of overflowing the panel
    let row = [];
    const flush = () => {
      if (row.length) line(`      ${row.map(teal).join(dim(' \u00b7 '))}`);
      row = [];
    };
    items.forEach((it) => {
      const next = [...row, it].join(' \u00b7 ');
      if (next.length > WIDTH - 6) flush();
      row.push(it);
    });
    flush();
  } else {
    line(`    ${dim(pad(label, 12))}${items.map(teal).join(dim(' \u00b7 '))}`);
  }
});

// ── 3. built ────────────────────────────────────────────────────────────────
ask('what has he built?', 'what has he built?');
think('0.8s');
call('list_projects', '{ sort: "notable" }', '180ms');

line(
  `    ${ink(NARROW ? '50+ projects since 2013.' : '50+ projects shipped since 2013.')}`,
);
line(`    ${dim('Two worth opening:')}`);
line();

const PROJECTS = [
  [
    'headless-adminapp',
    'Admin panels rendered from a schema',
    'Admin panels from a schema',
    '9 pkgs',
  ],
  [
    'd365-troubleshooter-mcp',
    'MCP server for Dataverse triage',
    'MCP server for Dataverse',
    'public',
  ],
];

PROJECTS.forEach(([name, wide, narrow, tag], i) => {
  if (NARROW) {
    line(`    ${amber(pad(name, WIDTH - 4 - tag.length))}${dim(tag)}`);
    line(`      ${grey(narrow)}`);
    if (i < PROJECTS.length - 1) line();
  } else {
    line(`    ${amber(pad(name, 25))}${grey(pad(wide, 39))}${dim(tag)}`);
  }
});

// ── 4. contact ────────────────────────────────────────────────────────────
ask('how do I contact him?', 'how to contact?');
call('get_contact', '{}', '12ms');

const CONTACT = [
  ['email', 'kishan.mundha@gmail.com', 'kishan.mundha@gmail.com'],
  ['github', 'github.com/kishanmundha', '/kishanmundha'],
  ['linkedin', 'linkedin.com/in/kishan-mundha', '/in/kishan-mundha'],
  ['based in', 'Tokyo, Japan', 'Tokyo, Japan'],
];

CONTACT.forEach(([label, wide, narrow]) => {
  const value = NARROW ? narrow : wide;
  const tone = label === 'based in' ? grey : teal;
  line(`    ${dim(pad(label, NARROW ? 9 : 12))}${tone(value)}`);
});

// ── footer ──────────────────────────────────────────────────────────────────
line();
line(`  ${dim('\u2500'.repeat(WIDTH - 4))}`);
line(`  ${teal('npx kishanmundha')}`);

console.log(out.join('\n'));
