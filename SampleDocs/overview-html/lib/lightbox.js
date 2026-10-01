/* ═══════════════════════════════════════════════════════════════════
   Design Docs Template — Diagram Lightbox (click-to-enlarge)
   Include AFTER mermaid-init.js. No HTML markup required — this
   script creates the overlay itself and binds every rendered SVG
   inside a .diagram-container (or legacy .arch-container).

     <script src="lib/mermaid.min.js"></script>
     <script src="lib/mermaid-init.js"></script>
     <script src="lib/lightbox.js"></script>

   Click a diagram → full-screen zoom.  Esc / click outside / × closes.
   ═══════════════════════════════════════════════════════════════════ */
(function () {
  // ── Inject overlay markup once ──
  var overlay = document.createElement('div');
  overlay.className = 'lightbox-overlay';
  overlay.innerHTML = '<div class="lightbox-content"></div>';
  var closeBtn = document.createElement('button');
  closeBtn.className = 'lightbox-close';
  closeBtn.title = 'Close';
  closeBtn.innerHTML = '&times;';

  function mount() {
    document.body.appendChild(overlay);
    document.body.appendChild(closeBtn);
  }
  if (document.body) { mount(); }
  else { document.addEventListener('DOMContentLoaded', mount); }

  var content = overlay.querySelector('.lightbox-content');

  // ── Inject styles once (kept here so the lightbox is drop-in) ──
  if (!document.getElementById('lightbox-styles')) {
    var style = document.createElement('style');
    style.id = 'lightbox-styles';
    style.textContent = [
      '.lightbox-overlay {',
      '  position: fixed; inset: 0; z-index: 9999;',
      '  background: rgba(0,0,0,0.88);',
      '  display: flex; align-items: center; justify-content: center;',
      '  cursor: zoom-out; opacity: 0; visibility: hidden;',
      '  transition: opacity 0.2s, visibility 0.2s;',
      '}',
      '.lightbox-overlay.active { opacity: 1; visibility: visible; }',
      '.lightbox-content {',
      '  background: #161b22; border: 1px solid #30363d; border-radius: 10px;',
      '  padding: 2.5rem 2rem; width: 92vw; max-height: 90vh;',
      '  overflow: auto; cursor: default;',
      '  transform: scale(0.95); transition: transform 0.2s;',
      '}',
      '.lightbox-overlay.active .lightbox-content { transform: scale(1); }',
      '.lightbox-close {',
      '  position: fixed; top: 1.2rem; right: 1.5rem; z-index: 10000;',
      '  background: #161b22; border: 1px solid #30363d;',
      '  color: #e6edf3; font-size: 1.4rem; line-height: 1;',
      '  width: 2.4rem; height: 2.4rem; border-radius: 6px; cursor: pointer;',
      '  display: flex; align-items: center; justify-content: center;',
      '  opacity: 0; visibility: hidden;',
      '  transition: opacity 0.2s, visibility 0.2s, background 0.15s;',
      '}',
      '.lightbox-close:hover { background: #f47067; }',
      '.lightbox-close.active { opacity: 1; visibility: visible; }',
    ].join('\n');
    document.head.appendChild(style);
  }

  // ── Bind every rendered diagram ──
  function bindLightboxes() {
    var containers = document.querySelectorAll('.diagram-container, .arch-container');
    containers.forEach(function (container) {
      if (container._lightboxBound) return;
      var svgEl = container.querySelector('svg');
      if (!svgEl) return;                       // not rendered (yet, or at all)
      container._lightboxBound = true;
      container.classList.add('zoomable');
      container.addEventListener('click', function () {
        var svg = container.querySelector('svg');
        if (!svg) return;
        var clone = svg.cloneNode(true);
        clone.removeAttribute('width');
        clone.removeAttribute('height');
        clone.style.cssText = 'width:100%; height:auto; max-width:none;';
        if (!clone.getAttribute('viewBox')) {
          var w = (svg.width && svg.width.baseVal.value) || svg.getBoundingClientRect().width;
          var h = (svg.height && svg.height.baseVal.value) || svg.getBoundingClientRect().height;
          if (w && h) clone.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
        }
        content.innerHTML = '';
        content.appendChild(clone);
        overlay.classList.add('active');
        closeBtn.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    });
  }

  // Preferred: bind when mermaid-init.js signals completion.
  document.addEventListener('mermaid:rendered', bindLightboxes);
  // Fallbacks: pages without mermaid (static SVG), or slow renders.
  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(bindLightboxes, 600);
    setTimeout(bindLightboxes, 2000);
  });

  // ── Close interactions ──
  function closeLightbox() {
    overlay.classList.remove('active');
    closeBtn.classList.remove('active');
    document.body.style.overflow = '';
  }
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeLightbox();
  });
  closeBtn.addEventListener('click', closeLightbox);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
  });
})();
