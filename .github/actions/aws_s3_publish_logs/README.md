# 🛠️ AWS S3 Publish Logs

Uploads logs from archive folder into AWS S3 bucket. Logs are gzipped before
upload.

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
- name: AWS S3 Publish Logs
  uses: fdio/csit/.github/actions/aws_s3_publish_logs@master
```
<!-- markdownlint-enable MD013 -->

## Inputs

<!-- markdownlint-disable MD013 -->

| Variable Name   | Description                                     |
| --------------- | ----------------------------------------------- |
| S3_BUCKET       | Name of the Amazon S3 bucket.                   |
| S3_PATH         | Path within Amazon AWS S3 bucket.               |
| ARCHIVES_PATH   | Source directory with logs artifact to archive. |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

The gzip command-line tool must be available in the environment for the action
to succeed.