import io
import urllib.parse
from werkzeug.datastructures import FileStorage
import json
import uuid

def test_supported_countries(client, mocker):
    expected_response = [
        {
            "Code": '231',
            "CountryName": "Germany"
        },
        {
            "Code": '232',
            "CountryName": "Switzerland"
        }
    ]
    
    response = client.get("/api/setup/supported_countries")
    assert response.status_code == 200
    assert response.json == expected_response


def test_available_model_years(client, mocker):
    expected_response = [2024, 2025, 2026]
    response = client.get("/api/setup/231/available_model_years")
    assert response.status_code == 200
    assert response.json == expected_response


def test_pnos(client, mocker):
    expected_response = '[{"ID":"F295F3B7-DA49-4A95-8CB3-10EC21CB5B89","Model":"539","Engine":"EH","SalesVersion":"CB","Gearbox":"L","StartDate":202417,"EndDate":202516,"CustomName":"EC40"}]'
    response = client.get("/api/db/231/2025/pnos")
    assert response.status_code == 200
    assert response.text == expected_response


def test_models(client, mocker):
    data = {"Code": '539', "CustomName": "test name"}
    response = client.post("/api/db/231/2025/write/models", json=data)
    assert response.status_code == 200
    assert response.text == 'Models written successfully'

    expected_response = '[{"Code":"539","CustomName":"test name","MarketText":"EC40"}]'
    response = client.get("/api/db/231/2025/models")
    assert response.status_code == 200
    assert response.text == expected_response


def test_packages(client, mocker):
    data = {
        "Code": "P0030",
        "CustomName": "test name",
        "Model": "539"
    }

    response = client.post("/api/db/231/2025/write/packages", json=data)
    assert response.status_code == 200
    assert response.text == 'Packages written successfully'

    expected_response = '[{"Code":"P0030","MarketText":"Edition Pack","CustomName":"test name"}]'
    response = client.get("/api/db/231/2025/packages")
    assert response.status_code == 200
    assert response.text == expected_response

    response = client.get("/api/db/231/2025/packages?model=539")
    assert response.status_code == 200
    assert response.text == expected_response


def test_colors(client, mocker):
    data = {"Code": 717, "CustomName": "test name", "Model": 539}
    response = client.post("/api/db/231/2025/write/colors", json=data)
    assert response.status_code == 200
    assert response.text == 'Colors written successfully'

    expected_response = '[{"Code":"717","MarketText":"Space","CustomName":"test name"}]'
    response = client.get("/api/db/231/2025/colors")
    assert response.status_code == 200
    assert response.text == expected_response

    response = client.get("/api/db/231/2025/colors?model=539")
    assert response.status_code == 200
    assert response.text == expected_response


def test_engines(client, mocker):
    data = {
        "Code": "EH",
        "CustomName": "test name",
        "EngineCategory": "Vollelektrisch",
        "EngineType": "Vollelektrisch",
        "Performance": "185 (252)"
    }
    response = client.post("/api/db/231/2025/write/engines", json=data)
    assert response.status_code == 200
    assert response.text == 'Engines written successfully'

    expected_response = '[{"Code":"EH","MarketText":"EL-ENGINE         252","CustomName":"test name","Performance":"185 (252)","EngineCategory":"Vollelektrisch","EngineType":"Vollelektrisch"}]'
    response = client.get("/api/db/231/2025/engines")
    assert response.status_code == 200
    assert response.text == expected_response


def test_engine_cats(client, mocker):
    expected_response = ['Vollelektrisch']
    response = client.get("/api/db/231/2025/engine_cats?model=539")
    assert response.status_code == 200
    assert response.json == expected_response


def test_sales_versions(client, mocker):
    data = {"Code": 'CB', "CustomName": "test name"}
    response = client.post("/api/db/231/2025/write/sales_versions", json=data)
    assert response.status_code == 200
    assert response.text == 'Sales Versions written successfully'

    expected_response = {"Code":"CB","CustomName":"test name","MarketText":"BLACK EDITION PURE EL 2"}
    response = client.get("/api/db/231/2025/sales_versions")
    assert response.status_code == 200
    assert json.loads(response.text).index(expected_response) >=0


def test_gearboxes(client, mocker):
    data = {"Code": 'L', "CustomName": "test name"}
    response = client.post("/api/db/231/2025/write/gearboxes", json=data)
    assert response.status_code == 200
    assert response.text == 'Gearboxes written successfully'

    expected_response = {"Code":"L","CustomName":"test name","MarketText":"1-SPEED GEARBOX"}
    response = client.get("/api/db/231/2025/gearboxes")
    assert response.status_code == 200
    assert json.loads(response.text).index(expected_response) >=0


def test_upholstery(client, mocker):
    data = {
        "Code": "R780",
        "CustomName": "test name",
        "CustomCategory": "test category",
        "Model": "539"
    }

    response = client.post("/api/db/231/2025/write/upholstery", json=data)
    assert response.status_code == 200
    assert response.text == 'Upholstery written successfully'

    expected_response = {'Code': 'R780', 'MarketText': None, 'CustomName': 'test name', 'CustomCategory': 'test category'}
    response = client.get("/api/db/231/2025/upholstery")
    assert response.status_code == 200
    assert json.loads(response.text).index(expected_response) >=0

    response = client.get("/api/db/231/2025/upholstery?model=539")
    assert response.status_code == 200
    assert json.loads(response.text).index(expected_response) >=0


def test_sales_channels(client, mocker):
    data = {
        "Code": "01",
        "ChannelName": "HDL",
        "Comment": "90% WS ALL",
        "DateFrom": "2023-01-02",
        "DateTo": "2099-12-30"
    }
    response = client.post("/api/db/231/2025/write/sales-channels", json=data)
    assert response.status_code == 200
    assert response.text == "Sales channel created successfully"

    response = client.get("/api/db/231/2025/sales-channels")
    assert response.status_code == 200
    resp_dict = []
    sales_channels_id = None
    for row in json.loads(response.text):
        if not sales_channels_id:
            id = row.pop("ID")
            if row == data:
                sales_channels_id = id
        resp_dict.append(row)
    assert resp_dict.index(data) >= 0

    response = client.post(f"/api/db/231/2025/write/sales-channels/copy?ids={sales_channels_id}")
    assert response.status_code == 200
    assert response.text == "Sales channel copied successfully"


    response = client.delete(f"/api/db/231/2025/write/sales-channels?ID={sales_channels_id}")
    assert response.status_code == 200
    assert response.json == {"message":"Record deleted successfully"}


def test_custom_local_options(client, mocker):
    data = {
        "ChannelID": "17597AA7-57D1-4C3C-BC7E-05956CD40FCF",
        "FeatureCode": "X03015",
        "FeatureRetailPrice": 3000,
        "FeatureWholesalePrice": 0,
        "AffectedVisaFile": None,
        "DateFrom": "2022-01-03",
        "DateTo": "2099-12-31"
    }
    response = client.post("/api/db/231/2025/write/custom-local-options", json=data)
    assert response.status_code == 200
    assert response.text == "Custom local option created successfully"

    expected_response = {'FeatureCode': 'X03015', 'FeatureRetailPrice': 3000.0, 'FeatureWholesalePrice': 0.0, 'AffectedVisaFile': [], 'DateFrom': '2022-01-03', 'DateTo': '2099-12-31'}
    response = client.get("/api/db/231/2025/custom-local-options?id=17597AA7-57D1-4C3C-BC7E-05956CD40FCF")
    assert response.status_code == 200
    resp_dict = []
    for row in json.loads(response.text):
        custom_local_options_id = row.pop("ID")
        resp_dict.append(row)
    assert resp_dict.index(expected_response) >= 0

    response = client.delete(f"/api/db/231/2025/write/custom-local-options?ID={custom_local_options_id}")
    assert response.status_code == 200
    assert response.json == {"message": "Record deleted successfully"}
    

def test_discount(client, mocker):
    data = {"ChannelID": "17597AA7-57D1-4C3C-BC7E-05956CD40FCF",
            "DiscountPercentage": 0.0,
            "RetailPrice": None,
            "WholesalePrice": None,
            "PNOSpecific": False,
            "AffectedVisaFile": []}
    response = client.post("/api/db/231/2025/write/discounts", json=data)
    assert response.status_code == 200
    assert response.text == "Discount created successfully"

    response = client.get("/api/db/231/2025/discounts?id=17597AA7-57D1-4C3C-BC7E-05956CD40FCF")
    resp_data = json.loads(response.data)[0]
    discount_id = resp_data.pop("ID")
    assert response.status_code == 200
    assert resp_data == data

    response = client.delete(f"/api/db/231/2025/write/discounts?ID={discount_id}")
    assert response.status_code == 200
    assert response.json == {'message': 'Record deleted successfully'}
    

def test_customfeatures(client, mocker):
    data_insert = {
        "CustomName": "test name",
        "CustomCategory": "test category",
        "StartDate": "202001",
        "EndDate": "202901",
        "Model": "539"
    }
    response = client.post("/api/db/231/2025/write/insert/customfeatures", json=data_insert)
    assert response.status_code == 200
    assert response.text == "Features written successfully"

    data_update = {
        "Code": "XY0001",
        "CustomName": "test name 2",
        "CustomCategory": "test category 2",
        "Model": "539",
        "ID": "2D9B2F73-3736-41D1-811C-01FD94C371F6"
    }
    response = client.post("/api/db/231/2025/write/update/customfeatures", json=data_update)
    assert response.status_code == 200
    assert response.text == "Features written successfully"

    data_delete = {
        "ID": "2D9B2F73-3736-41D1-811C-01FD94C371F6"
    }
    response = client.post("/api/db/231/2025/write/delete/customfeatures", json=data_delete)
    assert response.status_code == 200
    assert response.json == {"message": "Records deleted successfully"}



# visa tests ---------------------------------------------------------------------------------------------------
def test_visa_upload(client, mocker):
    my_file = FileStorage(
        stream=open('tests/VISA C40 MY25_24w17 (24w05).xlsx', 'rb'),
        filename="VISA C40 MY25_24w17 (24w05).xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    data = {}
    data['visa'] = my_file
    response = client.post("/api/231/ingest/visa/upload", data=data)
    assert response.status_code == 200
    assert response.json == "File uploaded successfully"


def test_visa_files(client, mocker):
    # expected_responce = '[{"VisaFile":"VISA C40 MY25_24w17 (24w05)","CarType":"539","CustomName":"EC40"}]'
    response = client.get("/api/db/231/2025/visa-files")
    assert response.status_code == 200
    assert json.loads(response.text)[0]["VisaFile"] == "VISA C40 MY25_24w17 (24w05)"


def test_visa_file(client, mocker):
    expected_responce = {"Active":"X","SalesOrg":"1585","DistrCh":"10","PriceList":"01","DealerGroup":"DE","Country":"DE","CarType":"539","Engine":"--","SalesVersion":"CB","Body":"-","Gearbox":"-","Steering":"-","MarketCode":"19","ModelYear":"2025","StructureWeek":"-","DateFrom":"2024-02-01","DateTo":"2025-04-20","Currency":"EUR","Color":"","Options":"","Upholstery":"","Package":"P0030","SNote":"","MSRP":"1810","TAX2":"0","VAT":"288.99","TAX1":"0","PriceBeforeTax":"1521.01","WholesalePrice":"1399.33","TransferPrice":"1034.29","VisaFile":"VISA C40 MY25_24w17 (24w05)"}
    params = urllib.parse.urlencode({"VisaFile": "VISA C40 MY25_24w17 (24w05)"})
    response = client.get(f"/api/db/231/2025/visa-file?{params}")
    assert response.status_code == 200
    resp_dict = []
    for row in json.loads(response.text):
        row.pop("ID")
        resp_dict.append(row)
    assert resp_dict.index(expected_responce) >= 0


def test_visa_rename(client, mocker):
    data = {"OldName": "VISA C40 MY25_24w17 (24w05)",
            "NewName": "VISA C40 MY25_24w17 (24w05) test"}
    response = client.post("/api/db/231/2025/write/visa/rename", json=data)
    assert response.status_code == 200
    assert response.text == "Visa file renamed successfully"

    data = {"OldName": "Old name ",
            "NewName": "New name"}
    response = client.post("/api/db/231/2025/write/visa/rename", json=data)
    assert response.status_code == 203
    assert response.text == "Visa file not found"


def test_visa_post(client, mocker):
    data = {"ID":"C3082836-FBF7-4C9A-96BB-3A7727989C2D","Active":"X","SalesOrg":"1585","DistrCh":"10","PriceList":"01","DealerGroup":"DE","Country":"DE","CarType":"539","Engine":"--","SalesVersion":"CB","Body":"-","Gearbox":"-","Steering":"-","MarketCode":"19","ModelYear":"2025","StructureWeek":"-","DateFrom":"2024-02-01","DateTo":"2025-04-20","Currency":"EUR","Color":"","Options":"","Upholstery":"","Package":"P0030","SNote":"","MSRP":"1810","TAX2":"0","VAT":"288.99","TAX1":"0","PriceBeforeTax":"1521.01","WholesalePrice":"1399.33","TransferPrice":"1034.29","VisaFile":"VISA C40 MY25_24w17 (24w05)"}
    response = client.post("/api/db/231/2025/write/visa", json=data)
    assert response.status_code == 200
    assert response.text == "Visa file created successfully"

    data = {"Active":"X","SalesOrg":"1585","DistrCh":"10","PriceList":"01","DealerGroup":"DE","Country":"DE","CarType":"539","Engine":"--","SalesVersion":"CB","Body":"-","Gearbox":"-","Steering":"-","MarketCode":"19","ModelYear":"2025","StructureWeek":"-","DateFrom":"2024-02-01","DateTo":"2025-04-20","Currency":"EUR","Color":"","Options":"","Upholstery":"","Package":"P0030","SNote":"","MSRP":"1810","TAX2":"0","VAT":"288.99","TAX1":"0","PriceBeforeTax":"1521.01","WholesalePrice":"1399.33","TransferPrice":"1034.29","VisaFile":"VISA C40 MY25_24w17 (24w05)"}
    response = client.post("/api/db/231/2025/write/visa", json=data)
    assert response.status_code == 200
    assert response.text == "Visa file created successfully"


def test_visa_data(client, mocker):
    params = urllib.parse.urlencode({"ID": "C3082836-FBF7-4C9A-96BB-3A7727989C2D"})
    response = client.delete(f"/api/db/231/2025/write/visa/data?{params}")
    assert response.status_code == 200
    assert response.text == "Record deleted successfully"


def test_visa_delete(client, mocker):
    params = urllib.parse.urlencode({"VisaFile": "VISA C40 MY25_24w17 (24w05)"})
    response = client.delete(f"/api/db/231/2025/write/visa?{params}")
    assert response.status_code == 200
    assert response.text == "Record deleted successfully"
# ----------------------------------------------------------------------------------------------------------------