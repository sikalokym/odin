#!/bin/bash
# export DB_CONNECTION_STRING=${DB_CONNECTION_STRING}Pwd=$(cat /run/secrets/sa_password);
pip3 install -r /app/requirements.txt -r /app/requirements_dev.txt
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.SupportedCountry.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.VisaFiles.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.Model.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNO.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOCustom.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOColor.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOColorCustom.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.Color.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOOptions.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOUpholstery.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOUpholsteryCustom.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOPackage.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.PNOPackageCustom.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.Package.Table.sql
/opt/mssql-tools18/bin/sqlcmd -S test_odin_database -U $SQL_DB_UID -P $SQL_DB_PWD -C -d odin -i /odin_database/dbo.Engine.Table.sql
cd /app
pytest -s -vv