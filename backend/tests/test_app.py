import io
from werkzeug.datastructures import FileStorage
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
