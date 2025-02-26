import io
from werkzeug.datastructures import FileStorage
def test_supported_countries(client, mocker):
    expected_responce = [
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
    assert response.json == expected_responce


def test_visa_upload(client, mocker):
    my_file = FileStorage(
        stream=open('tests/VISA_V90 MY25_24w17 (24w15).xlsx', 'rb'),
        filename="VISA_V90 MY25_24w17 (24w15).xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    data = {}
    data['visa'] = my_file
    respponse = client.post("/api/231/ingest/visa/upload", data=data)
    assert respponse.status_code == 200
    assert respponse.json == "File uploaded successfully"


def test_visa_files(client, mocker):
    expected_responce = '[{"VisaFile":"VISA_V90 MY25_24w17 (24w15)","CarType":"235","CustomName":"V90"}]'
    response = client.get("/api/db/231/2025/visa-files")
    assert response.status_code == 200
    assert response.text == expected_responce
