# =====================================
# EXPORT AI-TRO-GIANG SOURCE CODE (FINAL)
# =====================================

$Root = Get-Location
$OutputFile = Join-Path $Root "project_export.txt"

Remove-Item $OutputFile -ErrorAction SilentlyContinue

# Thư mục cần loại trừ
$ExcludeDirs = @(
    "node_modules",
    "venv",
    "__pycache__",
    ".git",
    "data"
)

Write-Host "Exporting source code to project_export.txt ..."

Get-ChildItem -Path $Root -Recurse -File | Where-Object {

    # 1. Loại thư mục không cần
    foreach ($dir in $ExcludeDirs) {
        if ($_.FullName -like "*\$dir\*") {
            return $false
        }
    }

    # 2. Điều kiện lấy file CẦN THIẾT
    return (
        $_.FullName -like "*\backend\*.py" -or
        $_.FullName -like "*\frontend\src\*.js" -or
        $_.FullName -like "*\frontend\src\*.jsx" -or
        $_.FullName -like "*\frontend\src\*\*.js" -or
        $_.FullName -like "*\frontend\src\*\*.jsx" -or
        $_.Name -in @(
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "README.md"
        )
    )

} | Sort-Object FullName | ForEach-Object {

    Add-Content $OutputFile "`n=============================="
    Add-Content $OutputFile "FILE: $($_.FullName)"
    Add-Content $OutputFile "==============================`n"

    Get-Content $_.FullName -Encoding UTF8 |
        Add-Content $OutputFile
}

Write-Host "DONE. File created: project_export.txt"
