FROM python:3.11

RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
RUN curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN . ~/.bashrc
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev

RUN echo "[MSSQLServerDatabase]\n\
Driver                 = ODBC Driver 18 for SQL Server\n\
Description            = Connect to my SQL Server instance\n\
Trace                  = No\n\
TrustServerCertificate = Yes\n\
Server                 = odin_database" >> ~/sql_conn_setup

RUN odbcinst -i -s -f ~/sql_conn_setup -l

# WORKDIR /code
# COPY ./backend/requirements.txt .
# COPY ./backend/requirements_dev.txt .
# RUN pip3 install -r requirements.txt
# RUN pip3 install -r requirements_dev.txt
COPY run_test/backend/backend_start.sh /usr
RUN chmod +x /usr/backend_start.sh
EXPOSE 50505
# CMD ["/usr/backend_start.sh"]
# ENTRYPOINT [ "/usr/backend_start.sh" ]: 