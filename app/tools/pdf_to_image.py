<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF to Image - Secure PDF Tools</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        }
        @media print {
            body * { visibility: hidden; }
            #preview-container, #preview-container * { visibility: visible; }
            #preview-container { position: absolute; left: 0; top: 0; width: 100%; }
            .no-print { display: none !important; }
        }
    </style>
</head>
<body class="bg-gray-50 font-sans min-h-screen flex flex-col justify-between">

    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200 no-print">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="flex items-center space-x-2 text-indigo-600 font-bold text-xl">
                        <span>🛠️ Secure PDF Tools</span>
                    </a>
                </div>
                <div class="flex items-center">
                    <a href="/" class="text-gray-600 hover:text-indigo-600 text-sm font-medium">Dashboard</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main class="flex-grow max-w-5xl w-full mx-auto px-4 py-12">
        <div class="text-center mb-8 no-print">
            <h1 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">Convert PDF to Images</h1>
            <p class="mt-3 max-w-2xl mx-auto text-xl text-gray-500">
                Extract pages into high-quality JPG, PNG, or WebP with Instant Print & Save features.
            </p>
        </div>

        <!-- Tool Container -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 no-print">
            <!-- Upload Box -->
            <div id="drop-zone" class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-indigo-500 transition-colors bg-gray-50">
                <input type="file" id="file-input" class="hidden" accept=".pdf">
                <div class="space-y-4">
                    <div class="text-indigo-500 text-5xl flex justify-center">📄</div>
                    <div class="text-gray-600">
                        <span class="font-medium text-indigo-600">Click to upload</span> or drag and drop PDF here
                    </div>
                </div>
            </div>

            <!-- Options Panel -->
            <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Select Output Format:</label>
                    <select id="image-format" class="w-full bg-white border border-gray-300 rounded-xl px-4 py-2.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="image/jpeg">JPG (Standard)</option>
                        <option value="image/png">PNG (Lossless/Transparent)</option>
                        <option value="image/webp">WebP (Next-Gen/Optimized)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Image Quality (DPI):</label>
                    <select id="image-dpi" class="w-full bg-white border border-gray-300 rounded-xl px-4 py-2.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="150">150 DPI (Fast / Screen)</option>
                        <option value="300">300 DPI (High Quality / Print)</option>
                    </select>
                </div>
            </div>

            <!-- Submit Button -->
            <button id="convert-btn" class="mt-6 w-full gradient-bg text-white py-3 px-6 rounded-xl font-medium shadow-md hover:opacity-90 transition-opacity flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                <span>Convert PDF Pages</span>
            </button>

            <!-- Status Alerts -->
            <div id="status-container" class="mt-4 hidden">
                <div id="status-message" class="p-4 rounded-xl text-sm font-medium"></div>
            </div>
        </div>

        <!-- Result Control & Preview Section (Hidden Initially) -->
        <div id="result-section" class="mt-8 hidden bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <div class="flex flex-col sm:flex-row items-center justify-between border-b border-gray-200 pb-4 mb-6 gap-4 no-print">
                <h2 class="text-xl font-bold text-gray-800">Generated Images Container</h2>
                <div class="flex space-x-3 w-full sm:w-auto">
                    <button id="save-all-btn" class="flex-1 sm:flex-none bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-xl font-medium transition-colors flex items-center justify-center space-x-2">
                        <span>💾 Save All (ZIP)</span>
                    </button>
                    <button id="print-btn" class="flex-1 sm:flex-none bg-gray-800 hover:bg-gray-900 text-white px-5 py-2.5 rounded-xl font-medium transition-colors flex items-center justify-center space-x-2">
                        <span>🖨️ Print Pages</span>
                    </button>
                </div>
            </div>

            <!-- Gallery/Preview Area -->
            <div id="preview-container" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Javascript will dynamically add images here -->
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 py-6 text-center text-sm text-gray-500 no-print">
        &copy; 2026 FFuture's Workspace. All rights reserved.
    </footer>

    <!-- PDF.js library for client-side multi-extension rendering & print support -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const convertBtn = document.getElementById('convert-btn');
        const statusContainer = document.getElementById('status-container');
        const statusMessage = document.getElementById('status-message');
        const resultSection = document.getElementById('result-section');
        const previewContainer = document.getElementById('preview-container');
        const saveAllBtn = document.getElementById('save-all-btn');
        const printBtn = document.getElementById('print-btn');

        let pdfDataArrayBuffer = null;
        let generatedImages = []; 

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-indigo-500'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-indigo-500'));
        dropZone.addEventListener('drop', (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); });

        function handleFile(file) {
            if (file && file.type === 'application/pdf') {
                const reader = new FileReader();
                reader.onload = function(e) {
                    pdfDataArrayBuffer = e.target.result;
                    convertBtn.disabled = false;
                    showStatus(`Successfully loaded: ${file.name}`, 'success');
                };
                reader.readAsArrayBuffer(file);
            } else {
                showStatus('Please drop or select a valid PDF file.', 'error');
            }
        }

        convertBtn.addEventListener('click', async () => {
            if (!pdfDataArrayBuffer) return;
            
            convertBtn.disabled = true;
            convertBtn.textContent = 'Processing...';
            previewContainer.innerHTML = '';
            generatedImages = [];
            
            const format = document.getElementById('image-format').value;
            const dpiScale = parseFloat(document.getElementById('image-dpi').value) / 72; 
            const ext = format.split('/')[1];

            try {
                const pdf = await pdfjsLib.getDocument({ data: pdfDataArrayBuffer }).promise;
                
                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    const page = await pdf.getPage(pageNum);
                    const viewport = page.getViewport({ scale: dpiScale });
                    
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    await page.render({ canvasContext: context, viewport: viewport }).promise;
                    
                    const imgDataUrl = canvas.toDataURL(format, 0.95);
                    generatedImages.push({ name: `page_${pageNum}.${ext}`, data: imgDataUrl });

                    // UI Card creation with individual save button
                    const card = document.createElement('div');
                    card.className = "bg-gray-100 p-4 rounded-xl border border-gray-200 flex flex-col items-center shadow-inner";
                    card.innerHTML = `
                        <img src="${imgDataUrl}" class="max-w-full h-auto rounded shadow-md border border-gray-300 mb-3" alt="Page ${pageNum}">
                        <div class="flex justify-between w-full items-center no-print">
                            <span class="text-xs font-semibold text-gray-500">Page ${pageNum} (${ext.toUpperCase()})</span>
                            <a href="${imgDataUrl}" download="page_${pageNum}.${ext}" class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">💾 Save Page</a>
                        </div>
                    `;
                    previewContainer.appendChild(card);
                }

                resultSection.classList.remove('hidden');
                showStatus('All pages parsed successfully below!', 'success');
            } catch (err) {
                showStatus(`Render error: ${err.message}`, 'error');
            } finally {
                convertBtn.disabled = false;
                convertBtn.textContent = 'Convert PDF Pages';
            }
        });

        // Save All Images as ZIP Container
        saveAllBtn.addEventListener('click', () => {
            if (generatedImages.length === 0) return;
            const zip = new JSZip();
            
            generatedImages.forEach(img => {
                const base64Data = img.data.split(',')[1];
                zip.file(img.name, base64Data, { base64: true });
            });

            zip.generateAsync({ type: 'blob' }).then(content => {
                const url = window.URL.createObjectURL(content);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'pdf_extracted_images.zip';
                a.click();
            });
        });

        // Custom Layout Printing Trigger
        printBtn.addEventListener('click', () => {
            window.print();
        });

        function showStatus(msg, type) {
            statusContainer.classList.remove('hidden');
            statusMessage.textContent = msg;
            statusMessage.className = `p-4 rounded-xl text-sm font-medium ${
                type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`;
        }
    </script>
</body>
</html>
