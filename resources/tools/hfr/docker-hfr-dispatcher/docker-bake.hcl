group "default" {
    targets = [
      "prod"
    ]
}

target "docker-metadata-action" {}

target "prod" {
    inherits = ["docker-metadata-action"]
    dockerfile = "Dockerfile"
    platforms = [
      "linux/amd64",
      "linux/aarch64"
    ]
    args = {
        BASE_IMAGE = "ghcr.io/astral-sh/uv:python3.13-trixie-slim"
    }
}