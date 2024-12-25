resource "azurerm_private_endpoint" "odin_pe" {
    name = "${var.private_service_connection_name}-pe"
    location = var.location
    resource_group_name = var.resource_group_name
    subnet_id = var.subnet_id
    private_service_connection {
      is_manual_connection = false
      name = "${var.private_service_connection_name}-psc"
      private_connection_resource_id = var.private_service_connection_resource_id
      subresource_names = [ var.subresource_name ]
    }

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"],
        private_dns_zone_group
       ]
    }
}