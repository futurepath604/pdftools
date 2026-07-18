<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merge PDF Online - Custom Sequence Priority | SecurePDF</title>
    <meta name="description" content="Combine and merge multiple PDF files online into one document. Interactive drag-and-drop sequencing control allows you to manage priority ordering seamlessly.">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col justify-between">

    <header class="bg-white border-b border-slate-200 py-4 px-6">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-black text-emerald-600">📄 SecurePDF</a>
            <a href="/compress" class="text-sm font-bold text-slate-600 hover:text-emerald-600">Switch to Compressor 🗜️</a>
        </div>
    </header>

    <main class="max-w-xl w-full mx-auto p-6 flex-grow flex flex-col justify-center">
        <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
            <h1 class="text-2xl font-bold text-slate-900 text-center mb-1">Priority Sequence PDF Merger</h1>
            <p class="text-xs text-slate-400 text-center mb-6">Select files multiple times to append. Adjust sequences via controls.</p>
            
            <!-- 📂 Append Multi-file Selection Input -->
            <input type="file" id="merge-input" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-emerald-50 file:text-emerald-700 mb-4" accept=".pdf" multiple>
            
            <!-- Dynamic Priority Matrix Container -->
            <div id="list-container" class="border border-slate-200 rounded-xl p-3 bg-slate-50 hidden space-y-2 mb-4">
                <p class="text-xxs font-bold text-slate-400 uppercase tracking-wider">Processing Priority Sequence:</p>
                <div id="dynamic-list" class="space-y-1"></div>
            </div>

            <button id="merge-btn" class="w-full bg-emerald-600 text-white py-3 rounded-xl font-bold hover:bg-emerald-700 transition">Merge Documents</button>
            <p id="status" class="mt-4 text-sm font-medium text-center text-slate-600"></p>
        </div>
    </main>

    <script>
        let filesStorage = []; // 🔒 চিরস্থায়ী মেমরি বাফার (নতুন ফাইল যোগ করলেও পুরনো ফাইল মুছবে না)

        document.getElementById('merge-input').onchange = function(e) {
            const selectedFiles = Array.from(e.target.files);
            
            // একই ফাইল ডুপ্লিকেট হওয়া রোধ করতে ফিল্টার এবং মেমরিতে আপেন্ড (Append) করা
            selectedFiles.forEach(file => {
                if(!filesStorage.some(f => f.name === file.name && f.size === file.size)) {
                    filesStorage.push(file);
                }
            });

            this.value = ""; // রিসেট ইনপুট যেন একই ফাইল বারবার যোগ করা যায়
            renderList();
        };

        function renderList() {
            const container = document.getElementById('list-container');
            const listDiv = document.getElementById('dynamic-list');
            listDiv.innerHTML = "";

            if(filesStorage.length > 0) {
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
                return;
            }

            filesStorage.forEach((file, index) => {
                const item = document.createElement('div');
                item.className = "flex justify-between items-center bg-white p-2.5 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700";
                item.innerHTML = `
                    <div class="flex items-center space-x-1.5 truncate max-w-[70%]">
                        <span class="bg-slate-100 px-1.5 py-0.5 rounded text-slate-400 text-xxs">${index + 1}</span>
                        <span class="truncate">${file.name}</span>
                    </div>
                    <div class="flex space-x-1 flex-shrink-0">
                        <button onclick="move(${index}, -1)" class="p-1 bg-slate-50 border rounded text-xxs hover:bg-slate-100">🔼</button>
                        <button onclick="move(${index}, 1)" class="p-1 bg-slate-50 border rounded text-xxs hover:bg-slate-100">🔽</button>
                        <button onclick="removeFile(${index})" class="p-1 bg-rose-50 border border-rose-200 rounded text-xxs text-rose-600 hover:bg-rose-100">❌</button>
                    </div>
                `;
                listDiv.appendChild(item);
            });
        }

        window.move = function(index, direction) {
            const target = index + direction;
            if(target < 0 || target >= filesStorage.length) return;
            const temp = filesStorage[index];
            filesStorage[index] = filesStorage[target];
            filesStorage[target] = temp;
            renderList();
        };

        window.removeFile = function(index) {
            filesStorage.splice(index, 1);
            renderList();
        };

        document.getElementById('merge-btn').onclick = async () => {
            if(filesStorage.length < 2) return alert("Select at least 2 files");
            const status = document.getElementById('status');
            status.innerText = "⏳ Compiling secure sequenced stream...";
            
            const formData = new FormData();
            filesStorage.forEach(file => formData.append('files', file));
            formData.append('file_order', JSON.stringify(filesStorage.map(f => f.name)));
            
            try {
                const res = await fetch('/api/merge', { method: 'POST', body: formData });
                if(res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = "merged_sequence_doc.pdf"; a.click();
                    status.innerText = "🎉 Merged Successfully!";
                } else { status.innerText = "❌ Merging pipeline failed."; }
            } catch { status.innerText = "❌ Network error."; }
        };
    </script>
</body>
</html>
