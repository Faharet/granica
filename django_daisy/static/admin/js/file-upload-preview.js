(function () {
  // Helpers
  const isImageType = (nameOrType) => {
    if (!nameOrType) return false;
    const s = String(nameOrType).toLowerCase();
    if (s.startsWith('image/')) return true;
    return /\.(png|jpe?g|gif|webp|avif|svg)$/i.test(s);
  };
  const bytesToSize = (bytes) => {
    if (bytes === undefined || bytes === null || bytes === '') return '';
    const sizes = ['B','KB','MB','GB','TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Init all widgets
  document.querySelectorAll('[data-clearable-file-widget]').forEach(initWidget);

  function initWidget(container) {
    let fileInput = container.querySelector('input[type="file"]');
    const previewArea = container.querySelector('[data-preview-area]');
    const previewContent = container.querySelector('[data-preview-content]');
    const previewEmpty = container.querySelector('[data-preview-empty]');
    const rotationInput = container.querySelector('[data-rotation-input]');
    const initialDataEl = container.querySelector('[data-initial-file]');

    if (!fileInput || !previewArea || !previewContent) return;

    let currentObjectUrl = null;
    let currentRotation = 0; // 0 | 90 | 180 | 270
    let currentImgElement = null;
    let resizeObserver = null;

    // revoke objectURL helper
    function revokeObjectUrl() {
      if (currentObjectUrl) {
        try { URL.revokeObjectURL(currentObjectUrl); } catch (e) {}
        currentObjectUrl = null;
      }
    }
    window.addEventListener('beforeunload', revokeObjectUrl);

    // Render preview (image or file card)
    function renderPreview(info) {
      // info: {url, isImage, name, size, type, source}
      previewContent.innerHTML = '';
      previewContent.classList.remove('hidden');
      if (previewEmpty) previewEmpty.style.display = 'none';
      currentImgElement = null;

      const wrapper = document.createElement('div');
      wrapper.className = 'relative w-full h-full flex items-center justify-center';

      // controls top-right with visible background (helps on dark images)
      const controls = document.createElement('div');
      controls.className = 'absolute right-3 top-3 z-20 flex items-center gap-2';
      controls.innerHTML = `
        <button type="button" aria-label="Открыть" title="Открыть" class="flex items-center justify-center h-9 w-9 rounded-full bg-white/90 backdrop-blur-sm shadow border border-gray-200 hover:scale-105 transition-transform" data-action-open>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.543 7-1.275 4.057-5.065 7-9.543 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
        </button>
        <button type="button" aria-label="Повернуть" title="Повернуть" class="flex items-center justify-center h-9 w-9 rounded-full bg-white/90 backdrop-blur-sm shadow border border-gray-200 hover:scale-105 transition-transform" data-action-rotate>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 10-3.22 6.6"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 3v5h-5"/>
          </svg>
        </button>
      `;
      wrapper.appendChild(controls);

      if (info.isImage) {
        // image container that constrains area; we compute scale to avoid cropping on rotation
        const imgWrap = document.createElement('div');
        imgWrap.className = 'w-full h-full flex items-center justify-center overflow-hidden rounded-md';
        imgWrap.style.position = 'relative';
        imgWrap.style.minHeight = '100px';
        imgWrap.style.maxHeight = '288px'; // keeps widget reasonable height

        const img = document.createElement('img');
        img.alt = info.name || 'preview';
        img.decoding = 'async';
        img.loading = 'lazy';
        img.className = 'will-change-transform transition-transform duration-150';
        img.style.transformOrigin = 'center center';
        img.style.maxWidth = 'none';
        img.style.maxHeight = 'none';
        img.src = info.url;

        img.addEventListener('load', () => {
          currentImgElement = img;
          applyScaleAndRotation();
          if (resizeObserver) resizeObserver.disconnect();
          resizeObserver = new ResizeObserver(() => applyScaleAndRotation());
          resizeObserver.observe(imgWrap);
          window.addEventListener('resize', applyScaleAndRotation);
        });

        imgWrap.appendChild(img);
        wrapper.appendChild(imgWrap);

        controls.querySelector('[data-action-open]').addEventListener('click', () => {
          window.open(info.url, '_blank', 'noopener');
        });
        controls.querySelector('[data-action-rotate]').addEventListener('click', () => {
          currentRotation = (currentRotation + 90) % 360;
          if (rotationInput) rotationInput.value = String(currentRotation);
          applyScaleAndRotation();
        });

      } else {
        // non-image: file card
        const card = document.createElement('div');
        card.className = 'w-full flex items-center gap-3 p-3 bg-white rounded-md border border-gray-100 shadow-sm';

        const icon = document.createElement('div');
        icon.className = 'flex-none';
        icon.innerHTML = `
          <div class="h-10 w-10 flex items-center justify-center rounded-md bg-gray-100 text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 7v10a3 3 0 003 3h4a3 3 0 003-3V9l-5-5H7z"/>
            </svg>
          </div>
        `;

        const meta = document.createElement('div');
        meta.className = 'min-w-0 flex-1 text-left';
        const name = document.createElement('div');
        name.className = 'text-sm font-medium text-gray-800 truncate';
        name.textContent = info.name || 'file';

        const sub = document.createElement('div');
        sub.className = 'text-xs text-gray-500';
        sub.textContent = (info.size ? bytesToSize(Number(info.size)) + (info.type ? ' · ' + info.type : '') : (info.type || ''));

        meta.appendChild(name);
        meta.appendChild(sub);

        controls.querySelector('[data-action-open]').addEventListener('click', () => {
          if (info.url) window.open(info.url, '_blank', 'noopener');
        });
        controls.querySelector('[data-action-rotate]').addEventListener('click', () => {
          const btn = controls.querySelector('[data-action-rotate]');
          btn.classList.add('animate-pulse');
          setTimeout(() => btn.classList.remove('animate-pulse'), 300);
        });

        card.appendChild(icon);
        card.appendChild(meta);
        wrapper.appendChild(card);
      }

      previewContent.appendChild(wrapper);
    }

    // Clear preview UI
    function clearPreviewUI() {
      previewContent.innerHTML = '';
      previewContent.classList.add('hidden');
      if (previewEmpty) previewEmpty.style.display = 'block';
      currentRotation = 0;
      if (rotationInput) rotationInput.value = '0';
      if (resizeObserver) { try { resizeObserver.disconnect(); } catch (e) {} }
      currentImgElement = null;
    }

    // Compute and apply scale + rotation so image never crops in container
    function applyScaleAndRotation() {
      if (!currentImgElement) return;
      const img = currentImgElement;
      const area = previewArea;
      if (!area) return;

      // available inner size (account for a small inset)
      const pad = 12;
      const cw = Math.max(20, area.clientWidth - pad);
      const ch = Math.max(20, area.clientHeight - pad);

      const nw = img.naturalWidth || img.width || 100;
      const nh = img.naturalHeight || img.height || 100;

      const rot = currentRotation % 360;
      let scale;
      if (rot === 90 || rot === 270) {
        // when rotated, width/height swap; ensure scaled dimensions fit
        scale = Math.min(cw / nh, ch / nw);
      } else {
        scale = Math.min(cw / nw, ch / nh);
      }
      if (!isFinite(scale) || scale > 1) scale = 1;

      img.style.transition = 'transform 180ms ease';
      img.style.transform = `rotate(${rot}deg) scale(${scale})`;
      // set explicit max sizes to allow natural dimensions but not overflow
      img.style.maxWidth = nw + 'px';
      img.style.maxHeight = nh + 'px';
      // center by ensuring display block and auto margins (image inside a flex-centered container)
      img.style.display = 'block';
    }

    // Load initial server file if present
    if (initialDataEl) {
      const url = initialDataEl.dataset.initialUrl || '';
      const name = initialDataEl.dataset.initialName || '';
      const size = initialDataEl.dataset.initialSize || '';
      const contentType = initialDataEl.dataset.initialContenttype || '';
      const isImg = isImageType(contentType) || isImageType(name);
      renderPreview({ url: url, isImage: isImg, name: name, size: size, type: contentType, source: 'initial' });
    }

    // Handle native file selection
    fileInput.addEventListener('change', (ev) => {
      const file = fileInput.files && fileInput.files[0];
      handleNewFile(file, 'local');
    });

    // Drag & drop handling (on the previewArea)
    previewArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      previewArea.classList.add('ring-2', 'ring-offset-2', 'ring-indigo-300', 'bg-indigo-50/10');
    });
    previewArea.addEventListener('dragleave', (e) => {
      e.preventDefault();
      previewArea.classList.remove('ring-2', 'ring-offset-2', 'ring-indigo-300', 'bg-indigo-50/10');
    });
    previewArea.addEventListener('drop', (e) => {
      e.preventDefault();
      previewArea.classList.remove('ring-2', 'ring-offset-2', 'ring-indigo-300', 'bg-indigo-50/10');

      const dt = e.dataTransfer;
      if (!dt || !dt.files || dt.files.length === 0) return;
      const file = dt.files[0];

      // Try to assign to input.files via DataTransfer
      let assigned = false;
      try {
        const dt2 = new DataTransfer();
        dt2.items.add(file);
        fileInput.files = dt2.files;
        assigned = true;
      } catch (err) {
        // fallback: clone input and replace
        try {
          const newInput = fileInput.cloneNode();
          const dt3 = new DataTransfer();
          dt3.items.add(file);
          newInput.files = dt3.files;
          fileInput.parentNode.replaceChild(newInput, fileInput);
          newInput.addEventListener('change', (ev) => {
            const f = newInput.files && newInput.files[0];
            handleNewFile(f, 'local');
          });
          fileInput = newInput;
          assigned = true;
        } catch (err2) {
          assigned = false;
        }
      }

      if (!assigned) {
        // show preview but inform user to select same file via native input to upload
        handleNewFile(file, 'local-fallback');
        showFallbackNotice(container, 'Браузер не позволил привязать файл к полю. После перетаскивания — выберите тот же файл через кнопку, чтобы он отправился на сервер.');
      } else {
        handleNewFile(file, 'local');
      }
    });

    function showFallbackNotice(containerEl, message) {
      let notice = containerEl.querySelector('[data-fallback-notice]');
      if (!notice) {
        notice = document.createElement('div');
        notice.dataset.fallbackNotice = '1';
        notice.className = 'mt-2 rounded-md bg-yellow-50 border border-yellow-100 text-sm text-yellow-800 p-2';
        containerEl.appendChild(notice);
      }
      notice.textContent = message;
      setTimeout(() => {
        if (notice && notice.parentNode) { try { notice.remove(); } catch (e) {} }
      }, 8000);
    }

    // Handle a newly chosen/dropped file
    function handleNewFile(file, source) {
      revokeObjectUrl();
      if (!file) {
        clearPreviewUI();
        return;
      }

      const isImg = file.type ? file.type.startsWith('image/') : isImageType(file.name);
      let url = '';

      if (isImg) {
        try {
          url = URL.createObjectURL(file);
          currentObjectUrl = url;
        } catch (e) {
          // fallback to dataURL
          const reader = new FileReader();
          reader.onload = function (ev) {
            url = ev.target.result;
            currentObjectUrl = null;
            currentRotation = 0;
            if (rotationInput) rotationInput.value = '0';
            renderPreview({ url, isImage: true, name: file.name, size: file.size, type: file.type, source });
          };
          reader.readAsDataURL(file);
          return;
        }
      }

      currentRotation = 0;
      if (rotationInput) rotationInput.value = '0';
      renderPreview({ url: url || '', isImage: isImg, name: file.name, size: file.size, type: file.type, source });
    }

    // Reflect clearing/reset to UI
    container.addEventListener('change', (e) => {
      if (e.target === fileInput && (!fileInput.files || fileInput.files.length === 0)) {
        revokeObjectUrl();
        clearPreviewUI();
      }
    });

    const formEl = container.closest('form');
    if (formEl) {
      formEl.addEventListener('reset', () => {
        setTimeout(() => {
          revokeObjectUrl();
          clearPreviewUI();
        }, 20);
      });
    }
  }
})();