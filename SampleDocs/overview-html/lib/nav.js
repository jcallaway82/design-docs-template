/* ═══════════════════════════════════════════════════════════════════
   Design Docs Template — Shared Navigation Bar
   One nav definition for the whole document suite, maintained here
   in a single place. Every page includes:

     <div id="page-nav"></div>
     <script src="lib/nav.js"></script>      (../lib/nav.js from subfolders)

   The script auto-detects the suite root from its own src attribute,
   so the same file works from any folder depth.

   ── EDIT THE `links` ARRAY BELOW FOR YOUR DOCUMENT SUITE ──
   Each entry: { label, href (relative to suite root), match: [substrings
   of the page path used to highlight the active link] }.
   Use the `sep` sentinel to draw a divider between link groups.
   ═══════════════════════════════════════════════════════════════════ */
(function () {
  // ── Compute base path (suite root) from this script's src ──
  var scriptEl = document.currentScript;
  var src = scriptEl.getAttribute('src');        // e.g. "../lib/nav.js"
  var base = src.replace(/lib\/nav\.js$/, '');   // e.g. "../"

  var sep = '│';

  // ═══ EDIT ME — suite navigation ═══
  var links = [
    { label: 'Home', href: 'index.html', match: ['index.html'] },
    sep,
    { label: 'Example Page A', href: 'Section A/Page_A.html', match: ['Page_A'] },
    { label: 'Example Page B', href: 'Section B/Page_B.html', match: ['Page_B'] },
  ];
  // ═══ END EDIT ME ═══

  var path = decodeURIComponent(window.location.pathname);
  var container = document.getElementById('page-nav');
  if (!container) return;

  var nav = document.createElement('nav');
  nav.className = 'page-nav';

  links.forEach(function (item) {
    if (item === sep) {
      var span = document.createElement('span');
      span.className = 'sep';
      span.textContent = sep;
      nav.appendChild(span);
      return;
    }
    var a = document.createElement('a');
    a.href = base + item.href;
    a.textContent = item.label;
    var isActive = item.match.some(function (m) {
      return path.indexOf(m) !== -1 || path.indexOf(m.replace(/\//g, '\\')) !== -1;
    });
    if (isActive) a.classList.add('active');
    nav.appendChild(a);
  });

  container.appendChild(nav);

  // ── Inject nav styles once ──
  if (!document.getElementById('nav-styles')) {
    var style = document.createElement('style');
    style.id = 'nav-styles';
    style.textContent = [
      '.page-nav {',
      '  position: sticky; top: 0; z-index: 100;',
      '  display: flex; align-items: center; gap: 0;',
      '  background: #161b22;',
      '  border-bottom: 1px solid #30363d;',
      '  margin: 0 -2rem 2rem;',
      '  padding: 0 2rem;',
      '  flex-wrap: wrap;',
      '}',
      '.page-nav a {',
      '  display: block; padding: 0.7rem 1.2rem;',
      '  font-size: 0.84rem; font-weight: 500;',
      '  color: #7d8590; text-decoration: none;',
      '  border-bottom: 2px solid transparent;',
      '  transition: color 0.15s, border-color 0.15s;',
      '  white-space: nowrap;',
      '}',
      '.page-nav a:hover { color: #c9d1d9; }',
      '.page-nav a.active { color: #58a6ff; border-bottom-color: #58a6ff; }',
      '.page-nav .sep {',
      '  color: #30363d; margin: 0 0.25rem; font-size: 0.75rem;',
      '  align-self: center; user-select: none;',
      '}',
    ].join('\n');
    document.head.appendChild(style);
  }
})();
