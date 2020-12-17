provider "null" {}

variable "sut1_mgmt_ip" {
  type    = string
  default = "10.32.8.23"
}

resource "null_resource" "deploy_sut1" {
  connection {
    type = "ssh"
    user = "testuser"
    host = var.sut1_mgmt_ip
  }
  provisioner "ansible" {
    plays {
      playbook {
        file_path      = "../../resources/tools/testbed-setup/ansible/site_awsx.yaml"
        roles_path     = [
          "../../resources/tools/testbed-setup/ansible/roles"
        ]
        force_handlers = true
        tags           = [
          "calibration"
        ]
      }
      limit               = var.sut1_mgmt_ip
      vault_password_file = "../../resources/tools/testbed-setup/ansible/vault_pass"
      inventory_file      = "../../resources/tools/testbed-setup/ansible/inventories/lf_inventory/hosts"
    }
  }
}

resource "null_resource" "deploy_topology" {
  depends_on = [ null_resource.deploy_sut1 ]
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/cloud_topology.yaml"
      }
      hosts            = ["local"]
      extra_vars       = {
        ansible_python_interpreter = "/usr/bin/python3"
        cloud_topology = "2n_clx_metal"
      }
    }
  }
}