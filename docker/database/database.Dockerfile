FROM mcr.microsoft.com/mssql/server:2022-latest
WORKDIR /usr
COPY docker/database/setup.sh ./scripts/setup.sh
# COPY backend/src/database/sql_templates/db_setup.sql ./scripts/db_setup.sql
# COPY backend/src/database/sql_templates/log_triggers.sql ./scripts/log_triggers.sql
RUN --mount=type=secret,id=sa_password,env=MSSQL_SA_PASSWORD ( /opt/mssql/bin/sqlservr --accept-eula & ) | grep -q "Service Broker manager has started" \
    && /usr/scripts/setup.sh $MSSQL_SA_PASSWORD  \
    && pkill sqlservr