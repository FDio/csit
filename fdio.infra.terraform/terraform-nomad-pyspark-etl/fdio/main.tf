data "vault_generic_secret" "fdio_logs" {
  path = "kv/secret/data/etl/fdio_logs"
}

data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

module "etl-stats" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-stats"
}

module "etl-trending-hoststack" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-trending-hoststack"
}

module "etl-trending-mrr" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-trending-mrr"
  memory                    = 60000
}

module "etl-trending-ndrpdr" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-trending-ndrpdr"
  memory                    = 60000
}

module "etl-trending-soak" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-trending-soak"
  memory                    = 60000
}

module "etl-iterative-hoststack-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-iterative-hoststack-rls2406"
}

module "etl-iterative-mrr-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-iterative-mrr-rls2406"
}

module "etl-iterative-ndrpdr-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-iterative-ndrpdr-rls2406"
}

module "etl-iterative-reconf-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-iterative-reconf-rls2406"
}

module "etl-iterative-soak-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-iterative-soak-rls2406"
}

module "etl-coverage-device-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-device-rls2406"
}

module "etl-coverage-hoststack-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-hoststack-rls2406"
}

module "etl-coverage-mrr-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-mrr-rls2406"
}

module "etl-coverage-ndrpdr-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-ndrpdr-rls2406"
}

module "etl-coverage-reconf-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-reconf-rls2406"
}

module "etl-coverage-soak-rls2406" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = "etl-coverage-soak-rls2406"
}

