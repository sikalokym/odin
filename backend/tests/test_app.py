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


def test_visa_files(client, mocker):
    expected_responce = '[{"VisaFile":"VISA C40 MY25_24w17 (24w05) .xlsx","CarType":"539","CustomName":"EC40"}]'
    response = client.get("/api/db/231/2025/visa-files")
    assert response.status_code == 200
    assert response.text == expected_responce
