# XML templates for API requests

model_year_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <startModelYear>{3}</startModelYear> 
</ProductDataGet>"""

model_year_resp_template = {
    "Error": ".//Moye/Error",
    "Years": {
        "path": ".//Moye/Data/Year",
        "children": {}
    }
}

car_types_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <modelYear>{3}</modelYear>	 
</ProductDataGet>"""

car_types_resp_template = {
    "Error": ".//Error",
    "DataRows": {
        "path": ".//DataRow",
        "children": {
            "Type": "Type",
            "ShortText": "ShortText",
            "MarketText": "MarketText"
        }
    }
}

dictionary_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <carType>{3}</carType>
    <modelYear>{4}</modelYear>
    <marketAuthFlag>{5}</marketAuthFlag>
    <startWeek>{6}</startWeek>
</ProductDataGet>"""

dictionary_resp_template = {
    "Error": ".//Dict/Error",
    "DataRows": {
        "path": ".//Dict/Data/DataRow",
        "children": {
            "MainDataType": "MainDataType",
            "DataType": "DataType",
            "Code": "Code",
            "Special": "Special",
            "ShortText": "ShortText",
            "MarketText": "MarketText",
            "StartDate": "Start",
            "EndDate": "End"
        }
    }
}

authorization_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <carType>{3}</carType>
    <modelYear>{4}</modelYear>
    <marketAuthFlag>{5}</marketAuthFlag>
    <startWeek>{6}</startWeek>
</ProductDataGet>"""

authorization_resp_template = {
    "Error": ".//Auth/Error",
    "DataRows": {
        "path": ".//Auth/Data/DataRow",
        "children": {
            "DataType": "DataType",
            "Code": "Code",
            "VariantRules": {
                "path": "VariantRules/VariantRule",
                "children": {
                    "Model": "Model",
                    "Engine": "Engine",
                    "SalesVersion": "SalesVersion",
                    "Steering": "Steering",
                    "Gearbox": "Gearbox",
                    "Body": "Body",
                    "MarketCode": "MarketCode",
                    "RuleName": "Rule",
                    "StartDate": "Start",
                    "EndDate": "End"
                }
            }
        }
    }
}

packages_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <carType>{3}</carType>
    <modelYear>{4}</modelYear>
    <marketAuthFlag>{5}</marketAuthFlag>
    <startWeek>{6}</startWeek>
</ProductDataGet>"""

packages_resp_template = {
    "Error": ".//Pack/Error",
    "PackageDataRows": {
        "path": ".//Pack/Data/DataRow",
        "children": {
            "Code": "Code",
            "Title": "Text",
            "VariantRules": {
                "path": "VariantRule",
                "children": {
                    "Model": "Model",
                    "Engine": "Engine",
                    "SalesVersion": "SalesVersion",
                    "Body": "Body",
                    "Gearbox": "Gearbox",
                    "Steering": "Steering",
                    "MarketCode": "MarketCode",
                    "StartDate": "Start",
                    "EndDate": "End"
                }
            },
            "Content": {
                "path": "Item",
                "children": {
                    "RuleCode": "code",
                    "RuleType": "type",
                    "RuleName": "Rule",
                    "RuleBase": "base"
                }
            }
        }
    }
}

dependency_rules_req_xml = """<ProductDataGet> 
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <carType>{3}</carType>
    <modelYear>{4}</modelYear>
    <marketAuthFlag>{5}</marketAuthFlag>
    <startWeek>{6}</startWeek>
</ProductDataGet>"""

dependency_rules_resp_template = {
    "Error": ".//Rules/Error",
    "DataRows": {
        "path": ".//Rules/Data/DataRow",
        "children": {
            "RuleCode": "Rule",
            "ItemCode": "Item",
            "FeatureCode": {
                "path": "mflist/mf",
                "children": {}
            },
            "VariantRules": {
                "path": "VariantRules/VariantRule",
                "children": {
                    "Model": "Model",
                    "Engine": "Engine",
                    "SalesVersion": "SalesVersion",
                    "Body": "Body",
                    "Gearbox": "Gearbox",
                    "Steering": "Steering",
                    "MarketCode": "MarketCode",
                    "StartDate": "Start",
                    "EndDate": "End"
                }
            }
        }
    }
}

features_req_xml = """<ProductDataGet>
    <consumer>{0}</consumer>
    <dataType>{1}</dataType>
    <specMarket>{2}</specMarket>
    <carType>{3}</carType>
    <modelYear>{4}</modelYear>
    <marketAuthFlag>{5}</marketAuthFlag>
    <startWeek>{6}</startWeek>
</ProductDataGet>"""

features_resp_template = {
    "Error": ".//Feat/Error",
    "DataRows": {
        "path": ".//Feat/Data/DataRow",
        "children": {
            "Code": "Code",
            "Special": "Special",
            "Reference": "Ref",
            "VariantRules": {
                "path": "VariantRules/VariantRule",
                "children": {
                    "Model": "Model",
                    "Engine": "Engine",
                    "SalesVersion": "SalesVersion",
                    "Body": "Body",
                    "Gearbox": "Gearbox",
                    "Steering": "Steering",
                    "MarketCode": "MarketCode",
                    "Options": "Option",
                    "RuleName": "Rule",
                    "StartDate": "Start",
                    "EndDate": "End"
                }
            }
        }
    }
}
