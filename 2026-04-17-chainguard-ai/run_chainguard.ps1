$python = "C:\Users\Rahim\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python runtime not found at $python"
    exit 1
}

& $python -m streamlit run app.py --server.headless true --server.port 8501
