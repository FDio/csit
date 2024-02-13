variable "flavour_name" {
  description = "(Optional; Required if flavor_id is empty) The name of the desired flavor for the server. Changing this resizes the existing server."
  type        = string
}

variable "network_id_data" {
  description = "(Required) The ID of the network to attach the port to. Changing this creates a new port."
  type        = string
}

variable "network_id_mgmt" {
  description = "(Required) The ID of the network to attach the port to. Changing this creates a new port."
  type        = string
}
