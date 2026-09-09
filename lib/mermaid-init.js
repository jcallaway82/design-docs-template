/* ═══════════════════════════════════════════════════════════════════
   Design Docs Template — Shared Mermaid Initialization
   Include AFTER mermaid.min.js on every page that has diagrams:

     <script src="lib/mermaid.min.js"></script>
     <script src="lib/mermaid-init.js"></script>
     <script src="lib/lightbox.js"></script>   <!-- optional zoom -->

   Diagrams are authored as:  <div class="diagram-container">
                                <pre class="mermaid"> ...source... </pre>
                              </div>

   Fully offline — mermaid.min.js is a local file, never a CDN.
   Dispatches 'mermaid:rendered' on document when all SVGs are done
   (lightbox.js listens for this).
   ═══════════════════════════════════════════════════════════════════ */
(function () {
  if (typeof mermaid === 'undefined') {
    console.error('mermaid-init.js: mermaid.min.js is missing or failed to load. ' +
      'Copy lib/mermaid.min.js next to this file — diagrams will show as raw source.');
    return;
  }

  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {
      /* Matches doc.css tokens */
      primaryColor:       '#1a3a5c',
      primaryTextColor:   '#c9d1d9',
      primaryBorderColor: '#30363d',
      lineColor:          '#58a6ff',
      secondaryColor:     '#161b22',
      tertiaryColor:      '#0d1117',
      noteBkgColor:       '#1c2129',
      noteTextColor:      '#c9d1d9',
      noteBorderColor:    '#30363d',
      actorBkg:           '#161b22',
      actorTextColor:     '#e6edf3',
      actorBorder:        '#58a6ff',
      signalColor:        '#c9d1d9',
      signalTextColor:    '#c9d1d9',
    },
    sequence: {
      mirrorActors:  false,
      wrap:          true,
      width:         180,
      noteMargin:    12,
      messageMargin: 40,
      actorMargin:   60,
      boxMargin:     8,
      boxTextMargin: 4,
      useMaxWidth:   true,
    },
    flowchart: { useMaxWidth: true },
  });

  function renderAll() {
    var done = function () {
      document.dispatchEvent(new CustomEvent('mermaid:rendered'));
    };
    try {
      var result = mermaid.run();
      if (result && typeof result.then === 'function') {
        result.then(done).catch(function (err) {
          console.error('Mermaid render error:', err);
          done(); // still fire so lightbox binds whatever rendered
        });
      } else {
        setTimeout(done, 400);
      }
    } catch (err) {
      console.error('Mermaid render error:', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAll);
  } else {
    renderAll();
  }
})();
