# resource "random_uuid" "example_administrator" {}

# resource "azuread_application_app_role" "germany_reader" { 
#   application_id = data.azuread_application.spn_app_6255.id
#   role_id = random_uuid.example_administrator.id

#   allowed_member_types = ["User"]
#   display_name = "Germany.Reader"
#   value = "231.reader"
#   description = "Germany Reader has the ability to export different artefacts."
# }

# resource "azuread_application_app_role" "germany_modifier" {
#   application_id = data.azuread_application.spn_app_6255.id
#   role_id = random_uuid.example_administrator.id

#   allowed_member_types = ["User"]
#   display_name = "Germany.Modifier"
#   value = "231.modifier"
#   description = "Germany Modifier has the ability to manage the translations in the database and resolve issues."
# }

# resource "azuread_application_app_role" "germany_sappricelist" {
#   application_id = data.azuread_application.spn_app_6255.id
#   role_id = random_uuid.example_administrator.id

#   allowed_member_types = ["User"]
#   display_name = "Germany.SAPpriceList"
#   value = "231.sappricelist"
#   description = "SAP Pricelist export is enabled for Germany market."
# }

# resource "azuread_application_app_role" "switzerland_reader" {
#   application_id = data.azuread_application.spn_app_6255.id
#   role_id = random_uuid.example_administrator.id

#   allowed_member_types = ["User"]
#   display_name = "Switzerland.Reader"
#   value = "232.reader"
#   description = "Switzerland Reader has the ability to export different artefacts."
# }

# resource "azuread_application_app_role" "switzerland_modifier" {
#   application_id = data.azuread_application.spn_app_6255.id
#   role_id = random_uuid.example_administrator.id

#   allowed_member_types = ["User"]
#   display_name = "Switzerland.Modifier"
#   value = "232.modifier"
#   description = "Switzerland Modifier has the ability to manage the translations in the database and resolve issues."
# }