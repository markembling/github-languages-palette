New-Item -ItemType Directory -Force -Path palettes | Out-Null

$formats = @("ccxml", "gpl", "json")
foreach ($format in $formats) {
    python generate.py --format $format palettes/githublangs.$format
}
