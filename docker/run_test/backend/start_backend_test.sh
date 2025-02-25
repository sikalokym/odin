#!/bin/bash
# export DB_CONNECTION_STRING=${DB_CONNECTION_STRING}Pwd=$(cat /run/secrets/sa_password);
pip3 install -r /app/requirements.txt -r /app/requirements_dev.txt
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.SupportedCountry.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.VisaFiles.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.Model.Table.sql
cd /app
pytest -s -vv