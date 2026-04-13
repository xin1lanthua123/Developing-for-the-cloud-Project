# Lấy danh sách tất cả bucket trong account
$buckets = aws s3 ls | ForEach-Object { ($_ -split "\s+")[-1] }

foreach ($bucket in $buckets) {
    Write-Host "`n==== Xử lý bucket: $bucket ===="

    do {
        # 1. Lấy ALL versions + delete markers
        $data = aws s3api list-object-versions `
            --bucket $bucket `
            --output json | ConvertFrom-Json

        # 2. Build payload đúng format AWS
        $objects = @()

        if ($data.Versions) {
            foreach ($v in $data.Versions) {
                $objects += @{
                    Key = $v.Key
                    VersionId = $v.VersionId
                }
            }
        }

        if ($data.DeleteMarkers) {
            foreach ($m in $data.DeleteMarkers) {
                $objects += @{
                    Key = $m.Key
                    VersionId = $m.VersionId
                }
            }
        }

        # 3. Nếu không còn gì thì skip
        if ($objects.Count -eq 0) {
            Write-Host "Bucket $bucket đã rỗng (không còn versions hoặc delete markers)."
            break
        } else {
            $payload = @{ Objects = $objects }

            # 4. Ghi file JSON KHÔNG BOM (ascii)
            $payload | ConvertTo-Json -Depth 5 | Set-Content delete-all.json -Encoding ascii

            # 5. Xóa tất cả versions và delete markers
            aws s3api delete-objects `
                --bucket $bucket `
                --delete file://delete-all.json
        }

    } while ($true)

    # 6. Xóa bucket
    aws s3 rb s3://$bucket
    Write-Host "Bucket $bucket đã được xóa hoàn toàn."
}

# 7. Tự động xóa file delete-all.json sau khi xong
if (Test-Path delete-all.json) {
    Remove-Item delete-all.json
    Write-Host "File delete-all.json đã được xóa tự động."
}
