provider "aws" {
  alias  = "deploy"
  region = "us-east-1"
  profile = "csit-pmikus"
}

provider "vault" {
}
