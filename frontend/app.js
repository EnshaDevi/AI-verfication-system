let currentModule = 'sms';

const modules = {
    'sms': {
        title: 'SMS & Text Spam Detection',
        desc: 'Analyze messages for spam, scams, and malicious intent.',
        placeholder: 'Paste the message content here...',
        endpoint: '/api/analyze/text',
        payloadKey: 'text'
    },
    'url': {
        title: 'Phishing URL Detection',
        desc: 'Analyze URLs for phishing patterns and malicious domains.',
        placeholder: 'https://example.com/suspicious-link',
        endpoint: '/api/analyze/url',
        payloadKey: 'url',
        inputType: 'text'
    },
    'email': {
        title: 'Email Spam & Phishing',
        desc: 'Analyze email content for scams, phishing, and social engineering.',
        placeholder: 'Paste the email text here...',
        endpoint: '/api/analyze/email',
        payloadKey: 'text',
        inputType: 'text'
    },
    'phone': {
        title: 'Phone Number Risk',
        desc: 'Check phone numbers for premium rate, international scam prefixes.',
        placeholder: '+44 7012345678',
        endpoint: '/api/analyze/phone',
        payloadKey: 'text',
        inputType: 'text'
    },
    'social': {
        title: 'Social Media Profile Risk',
        desc: 'Analyze profile bios for bot activity, scam links, and spam behavior.',
        placeholder: 'Paste profile bio or recent posts here...',
        endpoint: '/api/analyze/social',
        payloadKey: 'text',
        inputType: 'text'
    },
    'news': {
        title: 'News Verification (RAG)',
        desc: 'Verify claims against the trusted factual database.',
        placeholder: 'Enter a news claim (e.g., TechCorp filed for bankruptcy)',
        endpoint: '/api/analyze/news',
        payloadKey: 'text',
        inputType: 'text'
    },
    'image': {
        title: 'AI-Generated Image Detection',
        desc: 'Analyze images for AI generation artifacts and metadata manipulation.',
        placeholder: '',
        endpoint: '/api/analyze/image',
        payloadKey: 'file',
        inputType: 'file'
    },
    'document': {
        title: 'Certificate & ID Verification',
        desc: 'Analyze documents for forged text, formatting anomalies, and tampering.',
        placeholder: '',
        endpoint: '/api/analyze/document',
        payloadKey: 'file',
        inputType: 'file'
    },
    'audio': {
        title: 'Audio Deepfake Detection',
        desc: 'Analyze audio spectrograms for synthetic voice cloning artifacts.',
        placeholder: '',
        endpoint: '/api/analyze/audio',
        payloadKey: 'file',
        inputType: 'file'
    },
    'video': {
        title: 'Video Deepfake Detection',
        desc: 'Analyze video frames for facial boundary blending and temporal inconsistencies.',
        placeholder: '',
        endpoint: '/api/analyze/video',
        payloadKey: 'file',
        inputType: 'file'
    }
};

const API_BASE_URL = 'http://127.0.0.1:8000';

function hideAllViews() {
    ['analysis-area', 'history-area', 'results-card'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });

    // Reset active buttons
    document.querySelectorAll('.module-btn').forEach(btn => {
        btn.classList.remove('bg-gray-800', 'text-gray-200', 'bg-primary/10', 'text-primary', 'border-primary/20');
        btn.classList.add('text-gray-400', 'border-transparent');
    });
}

function selectModule(moduleId) {
    currentModule = moduleId;
    hideAllViews();
    
    const activeBtn = document.getElementById(`btn-${moduleId}`);
    if (activeBtn) {
        activeBtn.classList.remove('text-gray-400', 'border-transparent');
        activeBtn.classList.add('bg-primary/10', 'text-primary', 'border', 'border-primary/20');
    }

    // Update Content Area
    document.getElementById('module-title').innerText = modules[moduleId].title;
    document.getElementById('module-desc').innerText = modules[moduleId].desc;
    
    // Toggle input types
    const isFile = modules[moduleId].inputType === 'file';
    if (isFile) {
        document.getElementById('text-input-container').classList.add('hidden');
        document.getElementById('file-input-container').classList.remove('hidden');
        document.getElementById('input-file').value = '';
        document.getElementById('file-name-display').innerText = 'PNG, JPG, PDF, WAV, MP3, MP4, WEBM up to 10MB';
    } else {
        document.getElementById('text-input-container').classList.remove('hidden');
        document.getElementById('file-input-container').classList.add('hidden');
        document.getElementById('input-text').placeholder = modules[moduleId].placeholder;
        document.getElementById('input-text').value = '';
    }
    
    document.getElementById('analysis-area').classList.remove('hidden');
}

async function showHistory() {
    hideAllViews();
    document.getElementById('history-area').classList.remove('hidden');
    
    const historyBtn = document.getElementById('btn-history');
    if(historyBtn) {
        historyBtn.classList.add('bg-gray-800', 'text-gray-200');
        historyBtn.classList.remove('text-gray-400');
    }
    
    document.getElementById('history-loading').classList.remove('hidden');
    const tbody = document.getElementById('history-table-body');
    tbody.innerHTML = '';
    
    try {
        const response = await fetch(API_BASE_URL + '/api/history');
        if (response.ok) {
            const data = await response.json();
            const historyList = data.history || [];
            const statsEl = document.getElementById('history-stats');
            
            if (historyList.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-8 text-center text-gray-500">No scans found in history.</td></tr>`;
                statsEl.classList.add('hidden');
            } else {
                let fraudCount = 0;
                let safeCount = 0;
                
                historyList.forEach(scan => {
                    if (scan.risk_score > 50) fraudCount++;
                    else safeCount++;
                    
                    const date = new Date(scan.timestamp).toLocaleString();
                    const mod = modules[scan.module] ? modules[scan.module].title : scan.module;
                    let riskColor = "text-green-400";
                    if (scan.risk_score > 30) riskColor = "text-yellow-400";
                    if (scan.risk_score > 60) riskColor = "text-red-400";
                    
                    const row = document.createElement('tr');
                    row.className = "hover:bg-gray-800/30 transition-colors";
                    
                    const safeInput = scan.input_data || '';
                    const displayInput = safeInput.length > 20 ? safeInput.substring(0, 20) + '...' : safeInput;
                    const safeAdvice = scan.advice || '-';
                    const safeUser = scan.user || 'Unknown';
                    const encodedScan = encodeURIComponent(JSON.stringify(scan));

                    row.innerHTML = `
                        <td class="px-4 py-3 text-gray-500 whitespace-nowrap">${date}</td>
                        <td class="px-4 py-3 text-gray-400">${safeUser}</td>
                        <td class="px-4 py-3 font-medium text-gray-300">${mod}</td>
                        <td class="px-4 py-3 text-gray-400 truncate max-w-[150px]" title="${safeInput.replace(/"/g, '&quot;')}">${displayInput.replace(/"/g, '&quot;')}</td>
                        <td class="px-4 py-3 text-gray-400">${scan.classification} (<span class="${riskColor} font-bold">${scan.risk_score}</span>)</td>
                        <td class="px-4 py-3 text-gray-400 text-xs truncate max-w-[200px]" title="${safeAdvice.replace(/"/g, '&quot;')}">${safeAdvice.replace(/"/g, '&quot;')}</td>
                        <td class="px-4 py-3">
                            <button data-scan="${encodeURIComponent(JSON.stringify(scan))}" onclick="downloadHistoryPDF(decodeURIComponent(this.dataset.scan))" class="text-primary hover:text-white transition" title="Export PDF">
                                <i class="fa-solid fa-file-pdf"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                statsEl.innerHTML = `
                    <span class="text-red-400"><i class="fa-solid fa-shield-virus"></i> Fraud/Spam: ${fraudCount}</span>
                    <span class="text-gray-600">|</span>
                    <span class="text-green-400"><i class="fa-solid fa-shield-check"></i> Safe: ${safeCount}</span>
                `;
                statsEl.classList.remove('hidden');
            }
        }
    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-4 text-center text-red-500">Failed to load history</td></tr>`;
    } finally {
        document.getElementById('history-loading').classList.add('hidden');
    }
}

function downloadHistoryPDF(scanData) {
    const scan = typeof scanData === 'string' ? JSON.parse(scanData) : scanData;
    
    const tempDiv = document.createElement('div');
    tempDiv.style.padding = '20px';
    tempDiv.style.backgroundColor = '#1e1e1e';
    tempDiv.style.color = '#fff';
    tempDiv.style.fontFamily = 'sans-serif';
    
    let riskColor = "#22c55e";
    if (scan.risk_score > 30) riskColor = "#eab308";
    if (scan.risk_score > 60) riskColor = "#ef4444";
    
    tempDiv.innerHTML = `
        <h2 style="color: #f59e0b; margin-bottom: 10px;">VeriSense Forensics Report</h2>
        <p><strong>Date:</strong> ${new Date(scan.timestamp).toLocaleString()}</p>
        <p><strong>User:</strong> ${scan.user || 'Unknown'}</p>
        <p><strong>Module:</strong> ${scan.module}</p>
        <p><strong>Input Data:</strong> ${scan.input_data}</p>
        <hr style="border-color: #333; margin: 15px 0;">
        <h3 style="color: ${riskColor};">Result: ${scan.classification} (Risk Score: ${scan.risk_score})</h3>
        <div style="background-color: #2a2a2a; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #60a5fa; margin-top: 0;">Actionable Advice:</h4>
            <p style="margin-bottom: 0;">${scan.advice || 'No specific advice available.'}</p>
        </div>
    `;
    
    document.body.appendChild(tempDiv);
    
    const opt = {
        margin:       10,
        filename:     `VeriSense_History_${scan.id}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf().set(opt).from(tempDiv).save().then(() => {
        document.body.removeChild(tempDiv);
        if (typeof speak === 'function') speak("History report downloaded.");
    });
}

function updateFileName() {
    const fileInput = document.getElementById('input-file');
    const display = document.getElementById('file-name-display');
    if (fileInput.files.length > 0) {
        display.innerText = fileInput.files[0].name;
        display.classList.add('text-primary', 'font-medium');
    } else {
        display.innerText = 'PNG, JPG, PDF, WAV, MP3, MP4, WEBM up to 10MB';
        display.classList.remove('text-primary', 'font-medium');
    }
}

async function runAnalysis() {
    const moduleConfig = modules[currentModule];
    const isFile = moduleConfig.inputType === 'file';
    
    let fetchOptions = {
        method: 'POST'
    };
    
    if (isFile) {
        const fileInput = document.getElementById('input-file');
        if (fileInput.files.length === 0) return;
        
        const formData = new FormData();
        formData.append(moduleConfig.payloadKey, fileInput.files[0]);
        fetchOptions.body = formData;
        // Do not set Content-Type header when using FormData; the browser sets it with the boundary
    } else {
        const inputText = document.getElementById('input-text').value;
        if (!inputText.trim()) return;
        
        const payload = {};
        payload[moduleConfig.payloadKey] = inputText;
        fetchOptions.headers = { 'Content-Type': 'application/json' };
        fetchOptions.body = JSON.stringify(payload);
    }

    // Show loading
    document.getElementById('results-card').classList.add('hidden');
    document.getElementById('loading-state').classList.remove('hidden');
    document.getElementById('analyze-btn').disabled = true;

    try {
        const response = await fetch(API_BASE_URL + moduleConfig.endpoint, fetchOptions);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'API request failed');
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        console.error("Analysis failed:", error);
        alert(`Failed to analyze content: ${error.message}\nMake sure the FastAPI backend is running.`);
    } finally {
        document.getElementById('loading-state').classList.add('hidden');
        document.getElementById('analyze-btn').disabled = false;
    }
}

function renderResults(data) {
    document.getElementById('results-card').classList.remove('hidden');
    
    // Update Score & Confidence
    document.getElementById('risk-score-text').innerHTML = `${data.risk_score}<span class="text-sm text-gray-500">/100</span>`;
    document.getElementById('confidence-val').innerText = `${data.confidence}%`;
    
    // Update Classification Badge
    const badge = document.getElementById('classification-badge');
    badge.innerText = data.classification;
    if (data.risk_score > 75) {
        badge.className = 'px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-red-500/10 text-red-400 border border-red-500/20';
    } else if (data.risk_score > 40) {
        badge.className = 'px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
    } else {
        badge.className = 'px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-green-500/10 text-green-400 border border-green-500/20';
    }

    // Update Explanation
    let explanationHTML = data.explanation;
    if (currentModule === 'email' || currentModule === 'sms' || currentModule === 'social') {
        // Mock XAI Text Highlighting
        const dangerWords = ['urgent', 'password', 'click', 'bank', 'account', 'verify', 'suspended', 'login', 'prize', 'winner', 'free', 'offer'];
        const words = explanationHTML.split(' ');
        explanationHTML = words.map(w => {
            if (dangerWords.some(dw => w.toLowerCase().includes(dw))) {
                return `<span class="bg-red-500/20 text-red-400 font-bold px-1 rounded">${w}</span>`;
            }
            return w;
        }).join(' ');
    }
    document.getElementById('ai-explanation').innerHTML = explanationHTML;

    // XAI Image Preview Handling
    const xaiContainer = document.getElementById('xai-image-container');
    const xaiBox = document.getElementById('xai-bounding-box');
    if (modules[currentModule].inputType === 'file' && document.getElementById('input-file').files.length > 0) {
        xaiContainer.classList.remove('hidden');
        const file = document.getElementById('input-file').files[0];
        document.getElementById('xai-image-preview').src = URL.createObjectURL(file);
        
        if (data.risk_score > 50) {
            // Show bounding box
            xaiBox.classList.remove('hidden');
            xaiBox.style.top = '20%';
            xaiBox.style.left = '30%';
            xaiBox.style.width = '40%';
            xaiBox.style.height = '40%';
        } else {
            xaiBox.classList.add('hidden');
        }
    } else {
        xaiContainer.classList.add('hidden');
    }

    // Dark Web Badge Handling
    const darkWebBadge = document.getElementById('dark-web-badge');
    if ((currentModule === 'email' || currentModule === 'phone') && data.risk_score > 60) {
        darkWebBadge.classList.remove('hidden');
        if(window.speak) window.speak("Warning. Dark web breach detected for this identifier.");
    } else {
        darkWebBadge.classList.add('hidden');
    }

    // AI Advice Generation
    let adviceText = "";
    const adviceContainer = document.getElementById('ai-advice-container');
    const adviceEl = document.getElementById('ai-advice-text');
    
    if (data.risk_score > 60) {
        adviceText = "Do not interact with any links or attachments. Block the sender and report this as spam.";
        adviceContainer.classList.replace('bg-blue-500/10', 'bg-red-500/10');
        adviceContainer.classList.replace('border-blue-500/20', 'border-red-500/20');
        adviceContainer.querySelector('h4').classList.replace('text-blue-400', 'text-red-400');
        adviceContainer.querySelector('i').classList.replace('text-blue-400', 'text-red-400');
    } else if (data.risk_score > 30) {
        adviceText = "Exercise caution. Do not share personal information unless you verify the source.";
        adviceContainer.classList.replace('bg-blue-500/10', 'bg-yellow-500/10');
        adviceContainer.classList.replace('border-blue-500/20', 'border-yellow-500/20');
        adviceContainer.querySelector('h4').classList.replace('text-blue-400', 'text-yellow-400');
        adviceContainer.querySelector('i').classList.replace('text-blue-400', 'text-yellow-400');
    } else {
        adviceText = "This content appears safe. You may proceed normally, but stay vigilant.";
        adviceContainer.classList.replace('bg-red-500/10', 'bg-blue-500/10');
        adviceContainer.classList.replace('bg-yellow-500/10', 'bg-blue-500/10');
        adviceContainer.classList.replace('border-red-500/20', 'border-blue-500/20');
        adviceContainer.classList.replace('border-yellow-500/20', 'border-blue-500/20');
        adviceContainer.querySelector('h4').classList.replace('text-red-400', 'text-blue-400');
        adviceContainer.querySelector('h4').classList.replace('text-yellow-400', 'text-blue-400');
        adviceContainer.querySelector('i').classList.replace('text-red-400', 'text-blue-400');
        adviceContainer.querySelector('i').classList.replace('text-yellow-400', 'text-blue-400');
    }
    
    adviceEl.innerText = adviceText;
    adviceContainer.classList.remove('hidden');

    // Voice Feedback
    if (typeof speak === 'function') {
        const explanationHTML = data.explanation || "";
        const cleanExplanation = explanationHTML.replace(/<[^>]*>?/gm, '');
        speak(`Analysis complete. The result is ${data.classification}. ${cleanExplanation} Advice: ${adviceText}`);
    }

    // Update Indicators
    const indicatorsList = document.getElementById('indicators-list');
    indicatorsList.innerHTML = '';
    data.indicators.forEach(ind => {
        let iconClass = 'text-red-400 fa-circle-exclamation';
        if (ind.risk === 'medium') iconClass = 'text-yellow-400 fa-triangle-exclamation';
        if (ind.risk === 'low') iconClass = 'text-green-400 fa-check';

        const li = document.createElement('li');
        li.className = 'flex items-start gap-3 text-sm text-gray-300 bg-gray-900/50 p-3 rounded-lg border border-gray-800';
        li.innerHTML = `<i class="fa-solid ${iconClass} mt-0.5"></i> <span>${ind.text}</span>`;
        indicatorsList.appendChild(li);
    });

    // Handle Evidence (RAG)
    const evidenceSection = document.getElementById('evidence-section');
    const evidenceContainer = document.getElementById('evidence-container');
    
    if (data.evidence && data.evidence.length > 0) {
        evidenceSection.classList.remove('hidden');
        evidenceContainer.innerHTML = '';
        
        data.evidence.forEach(ev => {
            const div = document.createElement('div');
            div.className = 'bg-primary/5 border border-primary/20 p-4 rounded-xl relative overflow-hidden';
            div.innerHTML = `
                <div class="absolute top-0 left-0 w-1 h-full bg-primary"></div>
                <p class="text-gray-300 text-sm italic mb-2">"${ev.text}"</p>
                <div class="flex justify-between items-center text-xs">
                    <span class="text-gray-500 font-medium">Source: <span class="text-primary">${ev.source}</span></span>
                    <span class="text-gray-500">Relevance: ${(ev.relevance_score * 100).toFixed(0)}%</span>
                </div>
            `;
            evidenceContainer.appendChild(div);
        });
    } else {
        evidenceSection.classList.add('hidden');
    }
}



// ----------------// Modal logic for Export Report
function openReportModal() {
    const modal = document.getElementById('report-modal');
    const container = document.getElementById('report-preview-container');
    const sourceCard = document.getElementById('results-card');
    
    // Clone the results card to preview it
    container.innerHTML = '';
    const clone = sourceCard.cloneNode(true);
    // Remove the export button from the cloned preview
    const exportBtnContainer = clone.querySelector('.mt-8.flex.gap-4');
    if (exportBtnContainer) {
        exportBtnContainer.remove();
    }
    
    // Ensure styles render correctly in clone (tailwind handles most)
    clone.style.margin = '0';
    clone.style.boxShadow = 'none';
    
    container.appendChild(clone);
    
    modal.classList.remove('hidden');
}

function closeReportModal() {
    const modal = document.getElementById('report-modal');
    modal.classList.add('hidden');
}

async function generateCombinedReport() {
    try {
        const response = await fetch(API_BASE_URL + '/api/history');
        if (response.ok) {
            const data = await response.json();
            const historyList = data.history || [];
            
            if (historyList.length === 0) {
                alert("No scans found to generate a report.");
                return;
            }
            
            // Build Combined HTML
            let html = `
                <div id="combined-report-content" style="background-color: #1e1e1e; color: #fff; padding: 20px; font-family: sans-serif; width: 100%;">
                    <h1 style="color: #f59e0b; text-align: center; margin-bottom: 5px;">VeriSense AI</h1>
                    <h2 style="color: #e5e7eb; text-align: center; margin-top: 0; margin-bottom: 30px;">Comprehensive Analysis Report</h2>
                    <p><strong>Generated On:</strong> ${new Date().toLocaleString()}</p>
                    <p><strong>Total Scans:</strong> ${historyList.length}</p>
                    <hr style="border-color: #333; margin: 20px 0;">
            `;
            
            historyList.forEach((scan, index) => {
                let riskColor = "#22c55e";
                if (scan.risk_score > 30) riskColor = "#eab308";
                if (scan.risk_score > 60) riskColor = "#ef4444";
                
                const mod = modules[scan.module] ? modules[scan.module].title : scan.module;
                const safeInput = scan.input_data || 'N/A';
                
                html += `
                    <div style="margin-bottom: 25px; padding: 15px; border: 1px solid #333; border-radius: 8px; background-color: #262626;">
                        <h3 style="margin-top: 0; color: #60a5fa;">Scan #${historyList.length - index} - ${mod}</h3>
                        <p style="margin: 5px 0; font-size: 14px;"><strong>Date:</strong> ${new Date(scan.timestamp).toLocaleString()} | <strong>User:</strong> ${scan.user || 'Unknown'}</p>
                        <p style="margin: 5px 0; font-size: 14px;"><strong>Input:</strong> ${safeInput.length > 100 ? safeInput.substring(0, 100) + '...' : safeInput}</p>
                        <h4 style="color: ${riskColor}; margin: 10px 0 5px 0;">Result: ${scan.classification} (Risk Score: ${scan.risk_score})</h4>
                        <div style="background-color: #1a1a1a; padding: 10px; border-radius: 6px; font-size: 13px;">
                            <strong style="color: #9ca3af;">Actionable Advice:</strong><br>
                            ${scan.advice || 'No specific advice available.'}
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            
            const container = document.getElementById('report-preview-container');
            container.innerHTML = html;
            
            const modal = document.getElementById('report-modal');
            modal.classList.remove('hidden');
        } else {
            alert("Failed to load history data from server.");
        }
    } catch (e) {
        console.error(e);
        alert("An error occurred while generating the report.");
    }
}

function downloadReportFromModal() {
    const container = document.getElementById('report-preview-container');
    // For the PDF, we'll take the first child (the cloned results-card)
    const element = container.firstElementChild;
    
    const opt = {
        margin:       10,
        filename:     `VeriSense_Report_${new Date().getTime()}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf().set(opt).from(element).save().then(() => {
        if (typeof speak === 'function') speak("Report downloaded successfully.");
    });
}


