import pandas as pd
import numpy as np
import tableauserverclient as TSC


class TableauServerConnection:
    def __init__(self, server_url, token_name, token_secret, site=""):
        self.server_url = server_url
        self.token_name = token_name
        self.token_secret = token_secret
        self.site = site

    def to_string(self):
        print(
            "server_url={}\ntoken_name={}\ntoken_secret={}\nsite={}".format(
                self.server_url, self.token_name, self.token_secret, self.site
            )
        )


def getDataSourcesTableauServer(myTSConnection):
    server = TSC.Server(myTSConnection.server_url, use_server_version=True)
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=myTSConnection.token_name,
        personal_access_token=myTSConnection.token_secret,
        site_id=myTSConnection.site,
    )

    with server.auth.sign_in_with_personal_access_token(tableau_auth):
        print("[Logged in successfully to {}]".format(myTSConnection.server_url))
        print("[Loading data-sources...]")
        all_datasources, pagination_item = server.datasources.get()

        tableauDS = []
        for datasource in TSC.Pager(server.datasources.get):
            tableauDS.append(
                (
                    datasource.id,
                    datasource.name,
                    datasource.created_at,
                    datasource.certified,
                    datasource.certification_note,
                    datasource.datasource_type,
                    datasource.owner_id,
                    datasource.content_url,
                    datasource.project_id,
                    datasource.project_name,
                    datasource.tags,
                    datasource.updated_at,
                )
            )

        print("[Tableau {} data-sources loaded]".format(len(tableauDS)))
        return tableauDS


def refreshDataSourceTableauServer(myTSConnection, datasource_id):
    server = TSC.Server(myTSConnection.server_url, use_server_version=True)
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=myTSConnection.token_name,
        personal_access_token=myTSConnection.token_secret,
        site_id=myTSConnection.site,
    )
    with server.auth.sign_in_with_personal_access_token(tableau_auth):
        print("[Logged in successfully to {}]".format(myTSConnection.server_url))

        datasource = server.datasources.get_by_id(datasource_id)
        print("[Datasource previusly updated at {}]".format(datasource.updated_at))
        refreshed_datasource = server.datasources.refresh(datasource)

        print("[Datasource {} refreshed]".format(datasource.name))


def getWorkBooksTableauServer(myTSConnection):
    server = TSC.Server(myTSConnection.server_url, use_server_version=True)
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=myTSConnection.token_name,
        personal_access_token=myTSConnection.token_secret,
        site_id=myTSConnection.site,
    )

    with server.auth.sign_in_with_personal_access_token(tableau_auth):
        print("[Logged in successfully to {}]".format(myTSConnection.server_url))
        print("[Loading workbooks...]")
        all_datasources, pagination_item = server.datasources.get()

        tableauWB = []
        for workbook in TSC.Pager(server.workbooks.get):
            tableauWB.append(
                (
                    workbook.id,
                    workbook.name,
                    workbook.owner_id,
                    workbook.content_url,
                    workbook.project_id,
                    workbook.project_name,
                    workbook.size,
                    workbook.tags,
                    workbook.created_at,
                    workbook.updated_at,
                    workbook.webpage_url,
                )
            )

        print("[Tableau {} workbooks loaded]".format(len(tableauWB)))
        return tableauWB


def refreshWorkBookTableauServer(myTSConnection, workbook_id):
    server = TSC.Server(myTSConnection.server_url, use_server_version=True)
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=myTSConnection.token_name,
        personal_access_token=myTSConnection.token_secret,
        site_id=myTSConnection.site,
    )
    with server.auth.sign_in_with_personal_access_token(tableau_auth):
        print("[Logged in successfully to {}]".format(myTSConnection.server_url))
        workbook = server.workbooks.get_by_id(workbook_id)
        state = server.workbooks.refresh(workbook)
        print("[The data of workbook {0} is refreshed.".format(workbook.name))


tsconn = TableauServerConnection(
    "https://prod-apnortheast-a.online.tableau.com/",
    "google",
    "yPpTjHqKSmadrb4/D4+fwQ==:NThFOCjyrboMzhdOuhKgC0eg4t10SSND",
    "chimesai",
)


refreshDataSourceTableauServer(tsconn, "3e7870ea-c7fd-43ae-9727-c7987b7b31b5")
refreshWorkBookTableauServer(tsconn, "12479f28-81bb-4f9b-9cd5-a94c0382438a")
