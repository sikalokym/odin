/opt/mssql-tools18/bin/sqlcmd -U sa -P $1 -Q 'CREATE DATABASE [odin]' -C
/opt/mssql-tools18/bin/sqlcmd -U sa -P $1 -d 'odin' -i /usr/scripts/db_setup.sql -C
/opt/mssql-tools18/bin/sqlcmd -U sa -P $1 -d 'odin' -i /usr/scripts/log_triggers.sql -C