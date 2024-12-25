locals {
    virtual_network_name = "vnet-weu-app-6255-${var.env}-001"
    inbound_subnet_name = "snet-weu-app-6255-${var.env}-001"
    outbound_subnet_name = var.purpose != "" ? "snet-weu-app-6255-web-app-${var.purpose}" : "snet-weu-app-6255-web-app"
    network_resource_group_name = "rg-network-${var.env}-001"
}