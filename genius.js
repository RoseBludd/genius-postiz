(function () {
  var ICON = '/favicon.png';
  var WORDMARK = '/genius-wordmark.png';

  function replaceLogos(root) {
    (root || document).querySelectorAll('svg[viewBox="0 0 60 60"]').forEach(function (svg) {
      if (svg.dataset.geniusReplaced) return;
      var img = document.createElement('img');
      img.src = ICON;
      img.alt = 'Genius';
      img.width = 60;
      img.height = 60;
      img.dataset.geniusReplaced = '1';
      img.className = svg.getAttribute('class') || 'mt-[8px] min-w-[60px] min-h-[60px] w-[60px] h-[60px] rounded-[12px] object-contain';
      img.style.borderRadius = '12px';
      svg.replaceWith(img);
    });

    (root || document).querySelectorAll('svg[viewBox="0 0 101 33"], svg[width="101"][height="33"]').forEach(function (svg) {
      if (svg.dataset.geniusReplaced) return;
      var img = document.createElement('img');
      img.src = WORDMARK;
      img.alt = 'Genius';
      img.width = 180;
      img.height = 40;
      img.dataset.geniusReplaced = '1';
      img.style.display = 'block';
      img.style.margin = '0 auto 20px auto';
      img.style.objectFit = 'contain';
      svg.replaceWith(img);
    });

    (root || document).querySelectorAll('svg path[fill="#612BD3"], svg path[fill="#612bd3"]').forEach(function (path) {
      var svg = path.closest('svg');
      if (!svg || svg.dataset.geniusReplaced) return;
      if (svg.getAttribute('viewBox') === '0 0 60 60' || svg.getAttribute('width') === '60') {
        return;
      }
    });
  }

  function run() {
    replaceLogos(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  new MutationObserver(function () {
    run();
  }).observe(document.documentElement, { childList: true, subtree: true });

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) run();
  });
})();
