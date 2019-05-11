New-Item -ItemType Directory -Force -Path palettes | Out-Null

$formats = @("ccxml", "gpl", "ase", "json", "csv")
foreach ($format in $formats) {
    python generate.py --format $format palettes/githublangs.$format
}
