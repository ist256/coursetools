history = lambda: [
    {"ver" : "1.0.3-20221111", "text": "Added display_dataframes() function." },
    {"ver" : "1.0.2-20221111", "text": "Added versioning support." },
    {"ver" : "1.0.1-20221107", "text": "Fixed error in exceptions; problem when netid is an email." },
    {"ver" : "1.0.0-20200101", "text": "Initial release" }
]

current= lambda: history()[0]['ver']
