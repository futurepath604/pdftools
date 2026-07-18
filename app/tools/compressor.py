<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compress PDF Online - Adjust Sizes & Resolution | SecurePDF</title>
    <meta name="description" content="Reduce PDF size online without losing quality. Choose from low, standard, or high-resolution categories to optimize your document sizes instantly.">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col justify-between">

    <header class="bg-white border-b border-slate-200 py-4 px-6">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-black text-indigo-600">📄 SecurePDF</a>
            <a href="/merge" class="text-sm font-bold text-slate-600 hover:text-indigo-600">Switch to Merger 🔗</a>
        </div>
    </header>

    <main class="max-w-xl w-full mx-auto p-6 flex-grow flex flex-col justify-center">
        <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 text-center">
            <h1 class="text-2xl font-bold text-slate-900 mb-1">Compress PDF Document</h1>
            <p class="text-xs text-slate-400 mb-6">In-Memory Engine (Max 15MB)</p>
            
            <input type="file" id="comp-input" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-indigo-50 file:text-indigo-700 mb-6" accept=".pdf">
            
            <div class="grid grid-cols-3 gap-2 mb-6">
                <label class="border p-2 rounded-xl cursor-pointer text-xs font-bold"><input type="radio" name="quality" value="low"> <br>Low Size</label>
                <label class="border border-indigo-500 bg-indigo-50 p-2 rounded-xl cursor-pointer text-xs font-bold"><input type="radio" name="quality" value="medium" checked> <br>Standard</label>
                <label class="border p-2 rounded-xl cursor-pointer text-xs font-bold"><input type="radio" name="quality" value="high"> <br>High Res</label>
            </div>

            <button id="comp-btn" class="w-full bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700 transition">Compress Now</button>
            <p id="status" class="mt-4 text-sm font-medium text-slate-600"></p>
        </div>
    </main>

    <script>
        document.getElementById('comp-btn').onclick = async () => {
            const file = document.getElementById('comp-input').files[0];
            if(!file) return alert("Select file");
            const status = document.getElementById('status');
            status.innerText = "⏳ Processing compression matrix...";
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('quality', document.querySelector('input[name="quality"]:checked').value);
            
            try {
                const res = await fetch('/api/compress', { method: 'POST', body: formData });
                if(res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = `optimized_${file.name}`; a.click();
                    status.innerText = "🎉 Success! Downloaded.";
                } else { status.innerText = "❌ Processing failed."; }
            } catch { status.innerText = "❌ Network error."; }
        };
    </script>
</body>
</html>
