// ══════════════════════════════════════════════════════════
// State
// ══════════════════════════════════════════════════════════
const state = {
  documents: [],
  mode: 'qa',
  loading: false,
  hasMessages: false,
};

// ══════════════════════════════════════════════════════════
// DOM refs
// ══════════════════════════════════════════════════════════
const welcome   = document.getElementById('welcome');
const chat      = document.getElementById('chat');
const queryInput = document.getElementById('query-input');
const sendBtn   = document.getElementById('send-btn');
const fileInput = document.getElementById('file-input');
const dropZone  = document.getElementById('drop-zone');
const docList   = document.getElementById('doc-list');
const clearBtn  = document.getElementById('clear-btn');

// ══════════════════════════════════════════════════════════
// Markdown (marked.js + highlight.js)
// ══════════════════════════════════════════════════════════
marked.use({ breaks: true, gfm: true });

function renderMarkdown(text) {
  const html = marked.parse(text || '');
  const wrap = document.createElement('div');
  wrap.innerHTML = html;
  wrap.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
  return wrap.innerHTML;
}

// ══════════════════════════════════════════════════════════
// Utilities
// ══════════════════════════════════════════════════════════
function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function setLoading(val) {
  state.loading = val;
  queryInput.disabled = val;
  sendBtn.disabled = val || !queryInput.value.trim();
}

function showChat() {
  if (!state.hasMessages) {
    welcome.style.display = 'none';
    chat.classList.add('visible');
    state.hasMessages = true;
  }
}

// ══════════════════════════════════════════════════════════
// Mode tabs
// ══════════════════════════════════════════════════════════
document.querySelectorAll('.mode-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.mode-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.mode = btn.dataset.mode;
  });
});

// ══════════════════════════════════════════════════════════
// Document list
// ══════════════════════════════════════════════════════════
const EXT_MAP = {
  pdf: { badge: 'PDF', cls: 'pdf' },
  png: { badge: 'IMG', cls: 'img' },
  jpg: { badge: 'IMG', cls: 'img' },
  jpeg:{ badge: 'IMG', cls: 'img' },
  webp:{ badge: 'IMG', cls: 'img' },
  gif: { badge: 'IMG', cls: 'img' },
  md:  { badge: 'MD',  cls: 'md'  },
  txt: { badge: 'TXT', cls: 'txt' },
};

function docInfo(ext) {
  return EXT_MAP[(ext || '').toLowerCase().replace('.', '')] || { badge: 'FILE', cls: 'txt' };
}

function renderDocList() {
  docList.innerHTML = '';
  state.documents.forEach(doc => {
    const { badge, cls } = docInfo(doc.type);
    const item = document.createElement('div');
    item.className = 'doc-item';
    item.innerHTML = `
      <div class="doc-badge ${cls}">${badge}</div>
      <div class="doc-info">
        <div class="doc-name" title="${doc.name}">${doc.name}</div>
        <div class="doc-meta">${doc.chunks} chunk${doc.chunks !== 1 ? 's' : ''}</div>
      </div>`;
    docList.appendChild(item);
  });
}

function addUploadPlaceholder(name) {
  const item = document.createElement('div');
  item.className = 'doc-item uploading';
  item.dataset.uploading = name;
  item.innerHTML = `
    <div class="doc-badge txt"><div class="spinner"></div></div>
    <div class="doc-info">
      <div class="doc-name" title="${name}">${name}</div>
      <div class="doc-meta">Processing…</div>
    </div>`;
  docList.appendChild(item);
  return item;
}

// ══════════════════════════════════════════════════════════
// File upload
// ══════════════════════════════════════════════════════════
async function uploadFiles(files) {
  if (!files || !files.length) return;

  const formData = new FormData();
  const placeholders = [];

  Array.from(files).forEach(f => {
    formData.append('files', f);
    placeholders.push(addUploadPlaceholder(f.name));
  });

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await res.json();

    placeholders.forEach(el => el.remove());

    data.results.forEach(r => {
      if (r.status === 'ok') {
        const ext = r.name.split('.').pop();
        state.documents.push({ name: r.name, chunks: r.chunks, type: ext });
        toast(`✓ ${r.name}`, 'success');
      } else {
        toast(`✗ ${r.name}: ${r.message}`, 'error');
      }
    });

    renderDocList();
  } catch {
    placeholders.forEach(el => el.remove());
    toast('Upload failed — is the server running?', 'error');
  }
}

// Drag-and-drop
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  uploadFiles(e.dataTransfer.files);
});
fileInput.addEventListener('change', () => { uploadFiles(fileInput.files); fileInput.value = ''; });

// Clear
clearBtn.addEventListener('click', async () => {
  if (!state.documents.length) return;
  if (!confirm('Clear the entire knowledge base? This cannot be undone.')) return;
  try {
    await fetch('/api/documents', { method: 'DELETE' });
    state.documents = [];
    renderDocList();
    toast('Knowledge base cleared');
  } catch {
    toast('Failed to clear', 'error');
  }
});

// ══════════════════════════════════════════════════════════
// Chat messages
// ══════════════════════════════════════════════════════════
function addUserMessage(text) {
  const el = document.createElement('div');
  el.className = 'message user';
  el.innerHTML = `
    <div class="msg-avatar">P</div>
    <div class="msg-body">
      <div class="msg-text">${escapeHtml(text).replace(/\n/g, '<br>')}</div>
    </div>`;
  chat.appendChild(el);
  scrollToBottom();
}

function addAssistantMessage() {
  const el = document.createElement('div');
  el.className = 'message assistant';
  el.innerHTML = `
    <div class="msg-avatar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
        <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
        <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
      </svg>
    </div>
    <div class="msg-body">
      <div class="msg-text streaming"></div>
    </div>`;
  chat.appendChild(el);
  scrollToBottom();
  return el;
}

function finalizeMessage(el, fullText, sources) {
  const textEl = el.querySelector('.msg-text');
  textEl.classList.remove('streaming');
  textEl.innerHTML = renderMarkdown(fullText);

  if (sources && sources.length) {
    const section = document.createElement('div');
    section.className = 'sources-section';

    const cardsHtml = sources.map((s, i) => {
      const file = (s.metadata?.source || 'Unknown').split('/').pop().split('\\').pop();
      const page = s.metadata?.page ? ` · p.${s.metadata.page}` : '';
      const preview = (s.text || '').slice(0, 300) + (s.text?.length > 300 ? '…' : '');
      return `
        <div class="source-card">
          <div class="source-header">
            <span class="source-num">Source ${i + 1}</span>
            <span class="source-file" title="${file}${page}">${file}${page}</span>
          </div>
          <p class="source-text">${escapeHtml(preview)}</p>
        </div>`;
    }).join('');

    section.innerHTML = `
      <button class="sources-toggle">
        <span>${sources.length} source${sources.length > 1 ? 's' : ''} used</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      <div class="sources-list">${cardsHtml}</div>`;

    const toggle = section.querySelector('.sources-toggle');
    const list   = section.querySelector('.sources-list');
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('open');
      list.classList.toggle('visible');
    });

    el.querySelector('.msg-body').appendChild(section);
  }

  scrollToBottom();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ══════════════════════════════════════════════════════════
// Query / streaming
// ══════════════════════════════════════════════════════════
async function sendQuery(question) {
  if (!question.trim() || state.loading) return;

  setLoading(true);
  showChat();
  addUserMessage(question);
  const assistantEl = addAssistantMessage();
  const textEl = assistantEl.querySelector('.msg-text');

  let fullText = '';
  let sources  = null;

  try {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, mode: state.mode }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop(); // keep incomplete tail

      for (const part of parts) {
        if (!part.startsWith('data: ')) continue;
        let data;
        try { data = JSON.parse(part.slice(6)); } catch { continue; }

        if (data.type === 'sources') {
          sources = data.sources;
        } else if (data.type === 'text') {
          fullText += data.content;
          // Live-render markdown as tokens arrive
          textEl.innerHTML = renderMarkdown(fullText);
          scrollToBottom();
        } else if (data.type === 'done') {
          finalizeMessage(assistantEl, fullText, sources);
        } else if (data.type === 'error') {
          textEl.classList.remove('streaming');
          textEl.innerHTML = `<span style="color:var(--red)">Error: ${escapeHtml(data.message)}</span>`;
        }
      }
    }

    // Finalize if 'done' event didn't arrive (edge case)
    if (fullText && textEl.classList.contains('streaming')) {
      finalizeMessage(assistantEl, fullText, sources);
    }
  } catch (err) {
    textEl.classList.remove('streaming');
    textEl.innerHTML = `<span style="color:var(--red)">Connection error — is the server running?</span>`;
  }

  setLoading(false);
}

// ══════════════════════════════════════════════════════════
// Input controls
// ══════════════════════════════════════════════════════════
queryInput.addEventListener('input', () => {
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 200) + 'px';
  sendBtn.disabled = !queryInput.value.trim() || state.loading;
});

queryInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const text = queryInput.value.trim();
    if (text && !state.loading) {
      queryInput.value = '';
      queryInput.style.height = 'auto';
      sendBtn.disabled = true;
      sendQuery(text);
    }
  }
});

sendBtn.addEventListener('click', () => {
  const text = queryInput.value.trim();
  if (text && !state.loading) {
    queryInput.value = '';
    queryInput.style.height = 'auto';
    sendBtn.disabled = true;
    sendQuery(text);
  }
});

// Suggestion chips
document.querySelectorAll('.suggestion').forEach(btn => {
  btn.addEventListener('click', () => {
    queryInput.value = btn.dataset.text;
    queryInput.dispatchEvent(new Event('input'));
    queryInput.focus();
  });
});

// ══════════════════════════════════════════════════════════
// Init — load existing documents from server
// ══════════════════════════════════════════════════════════
(async () => {
  try {
    const res  = await fetch('/api/documents');
    const data = await res.json();
    state.documents = data.documents || [];
    renderDocList();
  } catch { /* server not yet ready */ }
})();
