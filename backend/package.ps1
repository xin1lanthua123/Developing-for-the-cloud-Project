# # Remove old dist
# if (Test-Path dist) { Remove-Item -Recurse -Force dist }

# # Install dependencies to dist
# pip install -r requirements.txt -t dist

# # Copy source code
# Copy-Item src\* dist\ -Recurse -Exclude *.pyc,__pycache__,test/

# # Zip
# cd dist
# Compress-Archive -Path * -DestinationPath ../lambda.zip
# cd ..
# Write-Host "Lambda package created: lambda.zip"

# Remove old dist
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Create dist
New-Item -ItemType Directory -Path "dist" | Out-Null

# Install dependencies to dist
pip install --no-user -r requirements.txt -t dist

# Copy source code, loại file *.pyc, __pycache__, và thư mục test
Get-ChildItem -Path "src" -Recurse |
    Where-Object { 
        $_.Name -notmatch "(__pycache__|test)" -and $_.Extension -ne ".pyc"
    } |
    ForEach-Object {
        $dest = $_.FullName.Replace((Resolve-Path "src").Path, (Resolve-Path "dist").Path)
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        } else {
            Copy-Item $_.FullName -Destination $dest -Force
        }
    }

# Zip
cd dist
Compress-Archive -Path (Get-ChildItem -Path .) -DestinationPath (Join-Path .. "lambda.zip")
cd ..

Write-Host "Lambda package created: lambda.zip"