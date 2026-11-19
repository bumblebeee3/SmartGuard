const analyzeButton = document.querySelector('#analyze');
const clearButton = document.querySelector('#clear');
const codeInput = document.querySelector('#code');
const fileInput = document.querySelector('#fileInput');
const results = document.querySelector('#results');
const findingsContainer = document.querySelector('#findings');
const disclaimer = document.querySelector('#disclaimer');
const lineCount = document.querySelector('#lineCount');
const rulesGrid = document.querySelector('#rulesGrid');
const ruleCount = document.querySelector('#ruleCount');
const downloadReport = document.querySelector('#downloadReport');
const reviewLevel = document.querySelector('#reviewLevel');
const totalCount = document.querySelector('#totalCount');
const highCount = document.querySelector('#highCount');
const mediumCount = document.querySelector('#mediumCount');
const lowCount = document.querySelector('#lowCount');
let lastReport = null;

const severityLabels = { HIGH: 'ALTA', MEDIUM: 'MEDIA', LOW: 'BAJA' };

function escapeHtml(value = '') {
  return value.replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
  }[char]));
}

function updateLineCount() {
  const text = codeInput.value;
  const lines = text ? text.split('\n').length : 0;
  lineCount.textContent = `${lines} línea${lines === 1 ? '' : 's'}`;
}

async function loadRules() {
  try {
    const response = await fetch('/api/rules');
    const data = await response.json();
    ruleCount.textContent = data.total;
    rulesGrid.innerHTML = data.rules.map((rule) => `
      <article class="rule-item">
        <div><span class="rule-id">${rule.rule_id}</span><strong>${rule.title}</strong></div>
        <span class="severity ${rule.severity.toLowerCase()}">${severityLabels[rule.severity]}</span>
        <small>${rule.category}</small>
      </article>
    `).join('');
  } catch (_error) {
    rulesGrid.innerHTML = '<p>No fue posible cargar el catálogo de reglas.</p>';
  }
}

async function loadSample(name) {
  const response = await fetch(`/api/sample/${name}`);
  if (!response.ok) throw new Error('No fue posible cargar el ejemplo');
  codeInput.value = await response.text();
  updateLineCount();
  codeInput.focus();
}

document.querySelectorAll('[data-sample]').forEach((button) => {
  button.addEventListener('click', async () => {
    try { await loadSample(button.dataset.sample); }
    catch (_error) { alert('No fue posible cargar el ejemplo.'); }
  });
});

fileInput.addEventListener('change', async () => {
  const file = fileInput.files?.[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.sol')) {
    alert('Selecciona un archivo con extensión .sol.');
    fileInput.value = '';
    return;
  }
  codeInput.value = await file.text();
  updateLineCount();
});

clearButton.addEventListener('click', () => {
  codeInput.value = '';
  fileInput.value = '';
  results.hidden = true;
  lastReport = null;
  downloadReport.disabled = true;
  updateLineCount();
});

codeInput.addEventListener('input', updateLineCount);

analyzeButton.addEventListener('click', async () => {
  const code = codeInput.value.trim();
  if (!code) {
    alert('Ingresa código Solidity antes de realizar el análisis.');
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.textContent = 'Analizando...';

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    if (!response.ok) throw new Error('Error en la solicitud de análisis');

    const data = await response.json();
    lastReport = { generated_at: new Date().toISOString(), source_lines: code.split('\n').length, ...data };
    downloadReport.disabled = false;
    results.hidden = false;

    totalCount.textContent = data.total_findings;
    highCount.textContent = data.severity_counts.HIGH;
    mediumCount.textContent = data.severity_counts.MEDIUM;
    lowCount.textContent = data.severity_counts.LOW;
    reviewLevel.textContent = data.review_level;
    reviewLevel.className = `review-banner ${data.severity_counts.HIGH ? 'urgent' : data.severity_counts.MEDIUM ? 'review' : 'calm'}`;
    disclaimer.textContent = data.disclaimer;

    if (data.findings.length === 0) {
      findingsContainer.innerHTML = `
        <div class="ok-card">
          <strong>No se detectaron los patrones configurados.</strong>
          <p>Esto no garantiza que el contrato sea seguro; solo indica que las reglas actuales no encontraron coincidencias.</p>
        </div>`;
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    findingsContainer.innerHTML = data.findings.map((finding) => `
      <article class="finding">
        <div class="finding-top">
          <div>
            <span class="rule-id">${finding.rule_id}</span>
            <strong>${finding.title}</strong>
          </div>
          <span class="severity ${finding.severity.toLowerCase()}">${severityLabels[finding.severity]}</span>
        </div>
        <div class="meta-row">
          <span>${finding.category}</span>
          <span>Línea ${finding.line}</span>
          ${finding.function ? `<span>Función: ${escapeHtml(finding.function)}()</span>` : ''}
        </div>
        ${finding.snippet ? `<pre><code>${escapeHtml(finding.snippet)}</code></pre>` : ''}
        <p>${finding.description}</p>
        <p class="recommendation"><b>Recomendación:</b> ${finding.recommendation}</p>
      </article>
    `).join('');

    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (_error) {
    results.hidden = false;
    findingsContainer.innerHTML = '<div class="error-card">No fue posible completar el análisis. Intenta nuevamente.</div>';
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = 'Analizar contrato';
  }
});

downloadReport.addEventListener('click', () => {
  if (!lastReport) return;
  const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `smartguard-reporte-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);
});

updateLineCount();
loadRules();
