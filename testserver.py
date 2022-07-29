import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth(
    "google",
    "yPpTjHqKSmadrb4/D4+fwQ==:NThFOCjyrboMzhdOuhKgC0eg4t10SSND",
    site_id="chimesai",
)
server = TSC.Server(
    "https://prod-apnortheast-a.online.tableau.com/", use_server_version=True
)
server.auth.sign_in(tableau_auth)

# Get a list of data sources
all_datasources, pagination_item = server.datasources.get()
print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
print([datasource.name for datasource in all_datasources])
print([datasource.id for datasource in all_datasources])


all_workbook, pagination_item = server.workbooks.get()
print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
print([datasource.name for datasource in all_workbook])
print([datasource.id for datasource in all_workbook])
