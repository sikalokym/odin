data "azurerm_subnet" "odin_subnet_inbound" {
    name = local.inbound_subnet_name
    resource_group_name = local.network_resource_group_name
    virtual_network_name = local.virtual_network_name
}

data "azurerm_subnet" "odin_subnet_outbound" {
    name = local.outbound_subnet_name
    resource_group_name = local.network_resource_group_name
    virtual_network_name = local.virtual_network_name
}

data "azuread_application" "spn_app_6255" {
  display_name = "spn-app-6255-corp-${var.env}-001"
}