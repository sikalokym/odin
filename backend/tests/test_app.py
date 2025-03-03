import io
import urllib.parse
from werkzeug.datastructures import FileStorage
import json


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
    expected_response = '[{"Code":"539","CustomName":"EC40","MarketText":"EC40"}]'
    response = client.get("/api/db/231/2025/models")
    assert response.status_code == 200
    assert response.text == expected_response


def test_packages(client, mocker):
    expected_response = '[{"Code":"P0030","MarketText":"Edition Pack","CustomName":""}]'
    response = client.get("/api/db/231/2025/packages")
    assert response.status_code == 200
    assert response.text == expected_response

    response = client.get("/api/db/231/2025/packages?model=539")
    assert response.status_code == 200
    assert response.text == expected_response


def test_colors(client, mocker):
    expected_response = '[{"Code":"717","MarketText":"Space","CustomName":""}]'
    response = client.get("/api/db/231/2025/colors")
    assert response.status_code == 200
    assert response.text == expected_response

    response = client.get("/api/db/231/2025/colors?model=539")
    assert response.status_code == 200
    assert response.text == expected_response


def test_engines(client, mocker):
    expected_response = '[{"Code":"EH","MarketText":"EL-ENGINE         252","CustomName":"Single Motor Extended Range RWD","Performance":"185 (252)","EngineCategory":"Vollelektrisch","EngineType":"Vollelektrisch"}]'
    response = client.get("/api/db/231/2025/engines")
    assert response.status_code == 200
    assert response.text == expected_response


def test_engine_cats(client, mocker):
    expected_response = ['Vollelektrisch']
    response = client.get("/api/db/231/2025/engine_cats?model=539")
    assert response.status_code == 200
    assert response.json == expected_response


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
    expected_responce = '[{"VisaFile":"VISA C40 MY25_24w17 (24w05)","CarType":"539","CustomName":"EC40"}]'
    response = client.get("/api/db/231/2025/visa-files")
    assert response.status_code == 200
    assert response.text == expected_responce


def test_visa_file(client, mocker):
    expected_responce = '[{"ID":"C3082836-FBF7-4C9A-96BB-3A7727989C2D","Active":"X","SalesOrg":"1585","DistrCh":"10","PriceList":"01","DealerGroup":"DE","Country":"DE","CarType":"539","Engine":"--","SalesVersion":"CB","Body":"-","Gearbox":"-","Steering":"-","MarketCode":"19","ModelYear":"2025","StructureWeek":"-","DateFrom":"2024-02-01","DateTo":"2025-04-20","Currency":"EUR","Color":"","Options":"","Upholstery":"","Package":"P0030","SNote":"","MSRP":"1810","TAX2":"0","VAT":"288.99","TAX1":"0","PriceBeforeTax":"1521.01","WholesalePrice":"1399.33","TransferPrice":"1034.29","VisaFile":"VISA C40 MY25_24w17 (24w05)"},{"ID":"4EDA9FC6-F7A5-4AA2-8E36-67DC0E55D618","Active":"X","SalesOrg":"1585","DistrCh":"10","PriceList":"01","DealerGroup":"DE","Country":"DE","CarType":"539","Engine":"EB","SalesVersion":"C8","Body":"0","Gearbox":"L","Steering":"1","MarketCode":"19","ModelYear":"2025","StructureWeek":"-","DateFrom":"2024-02-01","DateTo":"2025-04-20","Currency":"EUR","Color":"","Options":"","Upholstery":"","Package":"","SNote":"","MSRP":"58090","TAX2":"0","VAT":"9274.87","TAX1":"0","PriceBeforeTax":"48815.13","WholesalePrice":"44909.92","TransferPrice":"33194.29","VisaFile":"VISA C40 MY25_24w17 (24w05)"}]'
    params = urllib.parse.urlencode({"VisaFile": "VISA C40 MY25_24w17 (24w05)"})
    response = client.get(f"/api/db/231/2025/visa-file?{params}")
    assert response.status_code == 200
    assert response.text == expected_responce


def test_visa_rename(client, mocker):
    data = {"OldName": "VISA C40 MY25_24w17 (24w05)",
            "NewName": "VISA C40 MY25_24w17 (24w05) test"}
    response = client.post("/api/db/231/2025/write/visa/rename", json=data)
    assert response.status_code == 200
    assert response.text == "Visa file renamed successfully"

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


def test_visa_delete(client, mocker):
    params = urllib.parse.urlencode({"VisaFile": "VISA C40 MY25_24w17 (24w05)"})
    response = client.delete(f"/api/db/231/2025/write/visa?{params}")
    assert response.status_code == 200
    assert response.text == "Record deleted successfully"


def test_visa_data(client, mocker):
    params = urllib.parse.urlencode({"ID": "4EDA9FC6-F7A5-4AA2-8E36-67DC0E55D618"})
    response = client.delete(f"/api/db/231/2025/write/visa/data?{params}")
    assert response.status_code == 200
    assert response.text == "Record deleted successfully"
