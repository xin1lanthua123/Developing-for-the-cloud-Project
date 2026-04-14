$projectPrefixes = @(
  "cloud-incident-frontend-",
  "cloud-incident-upload-"
)

# tfstate bucket name bạn truyền từ pipeline hoặc set tay
$tfstateBucket = $env:TFSTATE_BUCKET_NAME

$buckets = aws s3 ls | ForEach-Object { ($_ -split "\s+")[-1] }

foreach ($bucket in $buckets) {

    # Exclude tfstate bucket
    if ($tfstateBucket -and $bucket -eq $tfstateBucket) {
        Write-Host "SKIP TFSTATE bucket: $bucket"
        continue
    }

    # chỉ xử lý bucket có prefix đúng
    $matched = $false
    foreach ($prefix in $projectPrefixes) {
        if ($bucket.StartsWith($prefix)) {
            $matched = $true
            break
        }
    }

    if (-not $matched) {
        Write-Host "SKIP bucket not in project: $bucket"
        continue
    }

    Write-Host "`n==== Xử lý bucket: $bucket ===="

    do {
        $data = aws s3api list-object-versions --bucket $bucket --output json | ConvertFrom-Json

        $objects = @()

        if ($data.Versions) {
            foreach ($v in $data.Versions) {
                $objects += @{ Key = $v.Key; VersionId = $v.VersionId }
            }
        }

        if ($data.DeleteMarkers) {
            foreach ($m in $data.DeleteMarkers) {
                $objects += @{ Key = $m.Key; VersionId = $m.VersionId }
            }
        }

        if ($objects.Count -eq 0) {
            Write-Host "Bucket $bucket đã rỗng."
            break
        }

        $payload = @{ Objects = $objects }
        $payload | ConvertTo-Json -Depth 5 | Set-Content delete-all.json -Encoding ascii

        aws s3api delete-objects --bucket $bucket --delete file://delete-all.json

    } while ($true)

    aws s3 rb s3://$bucket --force  
    Write-Host "Bucket $bucket đã được xóa hoàn toàn."
}

if (Test-Path delete-all.json) {
    Remove-Item delete-all.json
    Write-Host "File delete-all.json đã được xóa tự động."
}
