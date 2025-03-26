FROM mcr.microsoft.com/mssql/server:2022-latest
WORKDIR /usr
COPY --chmod=777 run_test/database/setup.sh ./scripts/setup.sh
RUN --mount=type=secret,id=sa_password ( /opt/mssql/bin/sqlservr --accept-eula & ) | grep -q "Service Broker manager has started" \
    && /usr/scripts/setup.sh $MSSQL_SA_PASSWORD  \
    && pkill sqlservr
