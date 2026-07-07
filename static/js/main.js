
// CSRF TOKEN 
function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

//  AVATAR DROPDOWN 
document.addEventListener('DOMContentLoaded', () => {
  const avatarMenu = document.querySelector('.avatar-menu');
  if (avatarMenu) {
    const btn = avatarMenu.querySelector('.avatar-btn');
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      avatarMenu.classList.toggle('open');
    });
    document.addEventListener('click', () => avatarMenu.classList.remove('open'));
  }

  initVoting();
  initSharing();
  initBookmark();
  initComments();
  initEditor();
  initMarkdownPreview();
  initTagInput();
  initMessages();
  initMobileSearch();
  initConfirmations();
  initCharacterCounters();
});

//  Voting
function initVoting() {
  document.querySelectorAll('.vote-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      if (this.dataset.loading) return;
      const contentType = this.dataset.type;
      const objectId = this.dataset.id;
      const value = parseInt(this.dataset.value);
      this.dataset.loading = '1';
      const voteCell = this.closest('.vote-cell');
      voteCell.classList.add('loading');

      try {
        const res = await fetch(`/votes/${contentType}/${objectId}/${value}/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (!res.ok || data.error) { showToast(data.error || 'Could not vote.', 'error'); return; }

        const countEl = voteCell.querySelector('.vote-count-display');
        if (countEl) countEl.textContent = data.vote_count;

        const upBtn = voteCell.querySelector('.vote-btn[data-value="1"]');
        const downBtn = voteCell.querySelector('.vote-btn[data-value="-1"]');
        if (upBtn) upBtn.classList.remove('voted-up');
        if (downBtn) downBtn.classList.remove('voted-down');

        if (data.user_vote === 1 && upBtn) upBtn.classList.add('voted-up');
        if (data.user_vote === -1 && downBtn) downBtn.classList.add('voted-down');
      } catch (e) {
        showToast('Failed to vote. Please try again.', 'error');
      } finally {
        delete this.dataset.loading;
        voteCell.classList.remove('loading');
      }
    });
  });
}

//SHARE LINKS
function initSharing() {
  document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const url = new URL(this.dataset.sharePath || window.location.pathname, window.location.origin).href;
      const title = this.dataset.shareTitle || document.title;

      if (navigator.share) {
        try {
          await navigator.share({ title, url });
          return;
        } catch (error) {
          if (error.name === 'AbortError') return;
        }
      }

      try {
        await navigator.clipboard.writeText(url);
        showToast('Link copied to clipboard.', 'success');
      } catch (error) {
        const temporaryInput = document.createElement('input');
        temporaryInput.value = url;
        temporaryInput.setAttribute('readonly', '');
        temporaryInput.style.position = 'fixed';
        temporaryInput.style.opacity = '0';
        document.body.appendChild(temporaryInput);
        temporaryInput.select();
        const copied = document.execCommand('copy');
        temporaryInput.remove();
        showToast(copied ? 'Link copied to clipboard.' : url, copied ? 'success' : 'info');
      }
    });
  });
}

// BOOKMARK 
function initBookmark() {
  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const qId = this.dataset.id;
      try {
        const res = await fetch(`/questions/${qId}/bookmark/`, {
          method: 'GET',
          headers: { 'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        const label = this.querySelector('.bookmark-label');
        if (data.bookmarked) {
          this.classList.add('active');
          this.title = 'Remove from saved questions';
          if (label) label.textContent = 'Saved';
          showToast('Question saved!', 'success');
        } else {
          this.classList.remove('active');
          this.title = 'Save this question';
          if (label) label.textContent = 'Save';
          showToast('Question removed from saved items.', 'info');
        }
      } catch (e) {
        showToast('Could not update saved question.', 'error');
      }
    });
  });
}

// COMMENTS
function initComments() {
  initCommentFormToggles();
  initCommentSubmissions();
  initCommentEditing();
  initCommentVoting();
}

function initCommentFormToggles() {
  document.querySelectorAll('.comment-form-toggle').forEach(btn => {
    btn.addEventListener('click', function () {
      const formId = this.dataset.target;
      const form = document.getElementById(formId);
      if (form) {
        form.classList.toggle('visible');
        if (form.classList.contains('visible')) {
          form.querySelector('textarea').focus();
        }
      }
    });
  });
}

function initCommentSubmissions() {
  document.querySelectorAll('.comment-form form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const url = this.action;
      const textarea = this.querySelector('textarea');
      const content = textarea.value.trim();
      if (!content) return;

      const submitBtn = this.querySelector('button[type=submit]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="loading-spinner"></span>';

      try {
        const fd = new FormData(this);
        const res = await fetch(url, {
          method: 'POST',
          body: fd,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const responseType = res.headers.get('content-type') || '';
        const data = responseType.includes('application/json')
          ? await res.json()
          : {};
        if (res.ok && data.success) {
          showToast('Comment added!', 'success');
          window.location.reload();
        } else {
          const fieldErrors = data.errors
            ? Object.values(data.errors).flat()
            : [];
          const errorMessage = data.error
            || fieldErrors[0]
            || `Could not post comment (server error ${res.status}).`;
          showToast(errorMessage, 'error');
        }
      } catch (err) {
        showToast('Could not reach the server. Please try again.', 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Add Comment';
      }
    });
  });
}

function initCommentEditing() {
  document.querySelectorAll('.comment-edit-toggle').forEach(btn => {
    btn.addEventListener('click', function () {
      const item = this.closest('.comment-item');
      item.classList.add('editing');
      const textarea = item.querySelector('.comment-edit-form textarea');
      if (textarea) textarea.focus();
    });
  });

  document.querySelectorAll('.comment-cancel-edit').forEach(btn => {
    btn.addEventListener('click', function () {
      this.closest('.comment-item').classList.remove('editing');
    });
  });

  document.querySelectorAll('.comment-edit-form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const item = this.closest('.comment-item');
      const textarea = this.querySelector('textarea');
      const content = textarea.value.trim();
      if (!content) return;

      try {
        const fd = new FormData(this);
        const res = await fetch(this.action, {
          method: 'POST',
          body: fd,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data.success) {
          item.querySelector('.comment-text').textContent = data.content;
          item.classList.remove('editing');
          showToast('Comment updated.', 'success');
        } else {
          showToast(data.error || 'Could not update comment.', 'error');
        }
      } catch (e) {
        showToast('Could not update comment.', 'error');
      }
    });
  });
}

function initCommentVoting() {
  document.querySelectorAll('.comment-vote-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const item = this.closest('.comment-item');
      try {
        const res = await fetch(this.dataset.url, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (!data.success) {
          showToast(data.error || 'Could not vote on comment.', 'error');
          return;
        }
        item.querySelector('.comment-vote-count').textContent = data.vote_count;
        item.querySelectorAll('.comment-vote-btn').forEach(b => b.classList.remove('active'));
        if (data.user_vote) this.classList.add('active');
      } catch (e) {
        showToast('Could not vote on comment.', 'error');
      }
    });
  });
}

// MARKDOWN EDITOR 
function initEditor() {
  document.querySelectorAll('.editor-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.dataset.target;
      const textarea = document.getElementById(targetId);
      if (!textarea) return;
      const action = this.dataset.action;
      applyEditorAction(textarea, action);
    });
  });
}

function applyEditorAction(textarea, action) {
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selected = textarea.value.substring(start, end);
  const before = textarea.value.substring(0, start);
  const after = textarea.value.substring(end);

  let replacement = '';

  const map = {
    bold: { wrap: '**', default: 'bold text' },
    italic: { wrap: '_', default: 'italic text' },
    strikethrough: { wrap: '~~', default: 'strikethrough' },
    code: { wrap: '`', default: 'code' },
  };

  if (map[action]) {
    const { wrap, default: def } = map[action];
    const text = selected || def;
    replacement = `${wrap}${text}${wrap}`;
  } else if (action === 'heading') {
    replacement = `\n## ${selected || 'Heading'}\n`;
  } else if (action === 'link') {
    const text = selected || 'link text';
    replacement = `[${text}](url)`;
  } else if (action === 'blockquote') {
    replacement = `\n> ${selected || 'quote'}\n`;
  } else if (action === 'code-block') {
    replacement = `\n\`\`\`\n${selected || 'code here'}\n\`\`\`\n`;
  } else if (action === 'ul') {
    replacement = formatList(selected, false);
  } else if (action === 'ol') {
    replacement = formatList(selected, true);
  } else if (action === 'hr') {
    replacement = `\n---\n`;
  }

  textarea.value = before + replacement + after;
  textarea.selectionStart = textarea.selectionEnd = start + replacement.length;
  textarea.dispatchEvent(new Event('input', { bubbles: true }));
  textarea.focus();
}

function formatList(selected, ordered) {
  const lines = (selected || 'list item')
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean);
  const list = lines.map((line, index) => {
    const cleanLine = line.replace(/^(?:[-*+]|\d+\.)\s+/, '');
    return `${ordered ? `${index + 1}.` : '-'} ${cleanLine}`;
  }).join('\n');
  return `\n${list}\n`;
}

// MARKDOWN PREVIEW 
function initMarkdownPreview() {
  document.querySelectorAll('.preview-tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const editorWrap = this.closest('.editor-wrap');
      const targetId = this.dataset.target;
      const previewId = this.dataset.preview;
      const textarea = document.getElementById(targetId);
      const preview = document.getElementById(previewId);

      editorWrap.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      if (this.dataset.mode === 'preview') {
        textarea.style.display = 'none';
        preview.classList.add('visible');
        preview.innerHTML = simpleMarkdown(textarea.value) || '<p class="text-muted">Nothing to preview.</p>';
      } else {
        textarea.style.display = '';
        preview.classList.remove('visible');
        textarea.focus();
      }
    });
  });
}

// Simple client-side markdown (basic)
function simpleMarkdown(text) {
  if (!text) return '';
  let html = escHtml(text);
  // code blocks
  html = html.replace(/```([^`]*?)```/gs, '<pre><code>$1</code></pre>');
  // inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // bold/italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/_(.+?)_/g, '<em>$1</em>');
  html = html.replace(/~~(.+?)~~/g, '<del>$1</del>');
  // links
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');
  // blockquote
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  // hr
  html = html.replace(/^---$/gm, '<hr>');
  // ordered and unordered list blocks
  html = html.replace(/(?:^|\n)((?:\d+\. [^\n]+(?:\n|$))+)/g, (match, block) => {
    const items = block.trim().split('\n')
      .map(line => `<li>${line.replace(/^\d+\.\s+/, '')}</li>`)
      .join('');
    return `\n<ol>${items}</ol>\n`;
  });
  html = html.replace(/(?:^|\n)((?:- [^\n]+(?:\n|$))+)/g, (match, block) => {
    const items = block.trim().split('\n')
      .map(line => `<li>${line.replace(/^-\s+/, '')}</li>`)
      .join('');
    return `\n<ul>${items}</ul>\n`;
  });
  // paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = '<p>' + html + '</p>';
  html = html.replace(/<p><\/p>/g, '');
  return html;
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// TAG INPUT AUTOCOMPLE
function initTagInput() {
  const input = document.getElementById('id_tags_input');
  if (!input) return;

  const container = input.closest('.tag-input-container');
  if (!container) return;

  let suggestions = document.createElement('div');
  suggestions.className = 'tag-suggestions';
  container.appendChild(suggestions);

  let debounceTimer;
  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const words = this.value.split(' ');
    const lastWord = words[words.length - 1].trim();
    if (lastWord.length < 2) { suggestions.style.display = 'none'; return; }
    debounceTimer = setTimeout(() => fetchTagSuggestions(lastWord, suggestions, input, words), 200);
  });

  document.addEventListener('click', e => {
    if (!container.contains(e.target)) suggestions.style.display = 'none';
  });
}

async function fetchTagSuggestions(query, suggestionsEl, input, words) {
  try {
    const res = await fetch(`/tags/?q=${encodeURIComponent(query)}&format=json`);
    if (!res.ok) throw new Error('Tag lookup failed');
    const data = await res.json();
    const tags = data.tags || [];
    if (!tags.length) {
      suggestionsEl.style.display = 'none';
      return;
    }
    suggestionsEl.innerHTML = tags.map(tag => (
      `<button type="button" class="tag-suggestion" data-tag="${escHtml(tag.name)}">
        <span>${escHtml(tag.name)}</span>
        <small>${tag.usage} question${tag.usage === 1 ? '' : 's'}</small>
      </button>`
    )).join('');
    suggestionsEl.style.display = 'block';
    suggestionsEl.querySelectorAll('.tag-suggestion').forEach(btn => {
      btn.addEventListener('click', () => {
        words[words.length - 1] = btn.dataset.tag;
        input.value = words.join(' ').trim() + ' ';
        suggestionsEl.style.display = 'none';
        input.focus();
      });
    });
  } catch (e) {
    suggestionsEl.style.display = 'none';
  }
}

// TOAST MESSAGES
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
  toast.className = `message ${type}`;
  toast.style.cssText = 'min-width:240px;max-width:340px;animation:slideIn 0.2s ease;box-shadow:0 4px 12px rgba(0,0,0,0.15);';
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span>${escHtml(message)}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// AUTO-DISMISS MESSAGES
function initMessages() {
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.4s';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });
}

// MOBILE SEARCH TOGGLE 
function initMobileSearch() {
  const searchToggle = document.getElementById('mobile-search-toggle');
  if (!searchToggle) return;

  searchToggle.addEventListener('click', () => {
    const navSearch = document.querySelector('.navbar-search');
    if (!navSearch) return;

    const isOpen = navSearch.classList.toggle('mobile-open');
    searchToggle.setAttribute('aria-expanded', String(isOpen));
    searchToggle.setAttribute('aria-label', isOpen ? 'Close search' : 'Open search');

    if (isOpen) {
      const searchInput = navSearch.querySelector('input');
      if (searchInput) searchInput.focus();
    }
  });
}

// CONFIRMATIONs
function initConfirmations() {
  document.querySelectorAll('[data-confirm]').forEach(element => {
    const eventName = element.tagName === 'FORM' ? 'submit' : 'click';
    element.addEventListener(eventName, function (event) {
      const message = this.dataset.confirm || 'Are you sure?';
      if (!confirm(message)) {
        event.preventDefault();
      }
    });
  });
}

// CHARACTER COUNTERS
function initCharacterCounters() {
  document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
    const maximum = parseInt(textarea.getAttribute('maxlength'));
    const counter = document.createElement('div');
    counter.style.cssText = 'text-align:right;font-size:11px;color:var(--text-muted);margin-top:2px;';
    counter.textContent = `0 / ${maximum}`;
    textarea.parentNode.insertBefore(counter, textarea.nextSibling);

    textarea.addEventListener('input', function () {
      const currentLength = this.value.length;
      counter.textContent = `${currentLength} / ${maximum}`;
      counter.style.color = currentLength > maximum * 0.9
        ? 'var(--red)'
        : 'var(--text-muted)';
    });
  });
}

// SLIDE IN ANIMATION 
const styleEl = document.createElement('style');
styleEl.textContent = `@keyframes slideIn { from { transform: translateX(40px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
document.head.appendChild(styleEl);
