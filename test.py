import pandas as pd
from datetime import date
import concurrent.futures as futures
import multiprocessing

# from multiprocessing import Pool

# import the data
file_names = [
    "anagraficapazientiattivi",
    "diagnosi",
    "esamilaboratorioparametri",
    "esamilaboratorioparametricalcolati",
    "esamistrumentali",
    "prescrizionidiabetefarmaci",
    "prescrizionidiabetenonfarmaci",
    "prescrizioninondiabete",
]


def read_csv(filename):
    return pd.read_csv(filename, header=0, index_col=0)


# read all the dataset concurrently and store them in a dictionary with the name of the file as key
with futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    df_list = dict()
    for name in file_names:
        df_list[str(name)] = executor.submit(read_csv, f"sample/{name}.csv")

# with Pool(processes=multiprocessing.cpu_count()) as pool:
#     df_list1 = pool.map(read_csv, paths)

######## PUNTO 1 ########

# diagnosi table
df_diagnosi = df_list["diagnosi"].result()
# pd.read_csv("sample/diagnosi.csv", header=0, index_col=False)

"""
AMD047: Myocardial infarction
AMD048: Coronary angioplasty
AMD049: Coronary bypass
AMD071: Ictus
AMD081: Lower limb angioplasty
AMD082: Peripheral By-pass Lower Limbs
AMD208: Revascularization of intracranial and neck vessels
AMD303: Ischemic stroke
"""
amd_of_cardiovascular_event = [
    "AMD047",
    "AMD048",
    "AMD049",
    "AMD071",
    "AMD081",
    "AMD082",
    "AMD208",
    "AMD303",
]

print("numero record presenti in diagnosi: ", len(df_diagnosi[["idana", "idcentro"]])) # 4427337
print(
    "numero pazienti unici presenti in diagnosi: ",
    len(df_diagnosi[["idana", "idcentro"]].drop_duplicates()),
) # 226303

# anagrafica table
df_anagrafica_attivi = df_list["anagraficapazientiattivi"].result()
# pd.read_csv("sample/anagraficapazientiattivi.csv", header=0, index_col=False)

print(
    "numero record presenti in anagrafica: ",
    len(df_anagrafica_attivi[["idana", "idcentro"]]),
)  # 250000
print(
    "numero pazienti unici in anagrafica: ",
    len(df_anagrafica_attivi[["idana", "idcentro"]].drop_duplicates()),
)  # 250000

print(
    "numero pazienti in anagrafica presenti in diagnosi:",
    len(
        pd.merge(
            df_anagrafica_attivi[["idana", "idcentro"]].drop_duplicates(),
            df_diagnosi[["idana", "idcentro"]].drop_duplicates(),
            how="inner",
            on=["idana", "idcentro"],
        )
    ),
)  # 226303

# Diagnosi relative a problemi cardiaci
df_diagnosi_problemi_cuore = df_diagnosi[
    df_diagnosi["codiceamd"].isin(amd_of_cardiovascular_event)
]

######## PUNTO 2 ########
print("############## POINT 2 START ##############")

print(
    "numero pazienti presenti in diagnosi con codice amd in lista (con problemi al cuore): ",
    len(df_diagnosi_problemi_cuore[["idana", "idcentro"]].drop_duplicates()),
)
print("Valori presenti:", df_diagnosi_problemi_cuore["valore"].unique())

print(
    "numero pazienti con anno diagnosi diabete minore dell'anno di nascita: ",
    sum(
        df_anagrafica_attivi["annodiagnosidiabete"]
        < df_anagrafica_attivi["annonascita"]
    ),
)

print(
    "numero pazienti con anno primo accesso minore dell'anno di nascita: ",
    sum(df_anagrafica_attivi["annoprimoaccesso"] < df_anagrafica_attivi["annonascita"]),
)

print(
    "numero pazienti con anno decesso minore dell'anno di nascita: ",
    sum(df_anagrafica_attivi["annodecesso"] < df_anagrafica_attivi["annonascita"]),
)

print(
    "numero pazienti con anno decesso maggiore dell'anno 2022: ",
    sum(df_anagrafica_attivi["annodecesso"] > 2022),
)

print(
    "numero pazienti con anno di nascita negativo: ",
    sum(df_anagrafica_attivi["annonascita"] < 0),
)

print(
    "numero pazienti con anno primo accesso maggiore dell'anno decesso: ",
    sum(df_anagrafica_attivi["annoprimoaccesso"] > df_anagrafica_attivi["annodecesso"]),
)

# print(
#     "pazienti con anno primo accesso maggiore dell'anno decesso: ",
#     df_anagrafica_attivi[
#         df_anagrafica_attivi["annoprimoaccesso"] > df_anagrafica_attivi["annodecesso"]
#     ],
# )

print(
    "numero pazienti con anno diagnosi diabete maggiore dell'anno decesso: ",
    sum(
        df_anagrafica_attivi["annodiagnosidiabete"]
        > df_anagrafica_attivi["annodecesso"]
    ),
)

# print(
#     "pazienti con anno diagnosi diabete maggiore dell'anno decesso: ",
#     df_anagrafica_attivi[
#         df_anagrafica_attivi["annodiagnosidiabete"]
#         > df_anagrafica_attivi["annodecesso"]
#     ],
# )

print(
    "numero pazienti con anno diagnosi diabete a N/A: ",
    sum(df_anagrafica_attivi["annodiagnosidiabete"].isna()),
)

# print("tipi possibili di diabete: ", df_anagrafica_attivi["tipodiabete"].unique())
# in anagrafica abbiamo solo pazienti con diagnosi di diabete di tipo 2 valore 5 in 'tipodiabete'
# quindi possiamo fillare l'annodiagnosidiabete con l'annoprimoaccesso

# visto che il tipo diabete è sempre lo stesso si può eliminare la colonna dal df per risparmiare memoria
df_anagrafica_attivi.drop(columns=["tipodiabete"], inplace=True)

print(
    "numero pazienti con anno diagnosi diabete a N/A, ma che hanno l'anno di primo accesso: ",
    len(
        df_anagrafica_attivi[
            df_anagrafica_attivi["annodiagnosidiabete"].isna()
            & df_anagrafica_attivi["annoprimoaccesso"].notnull()
        ][["idana", "idcentro"]]
    ),
)

# anagrafica pazienti con problemi al cuore, e relativa diagnosi
aa_prob_cuore = pd.merge(
    df_anagrafica_attivi, df_diagnosi_problemi_cuore, on=["idcentro", "idana"]
)

print(
    "numero pazienti con problemi al cuore: ",
    len(aa_prob_cuore[["idana", "idcentro"]].drop_duplicates()),
)


print("info dataframe pazienti con problemi al cuore: ")
print(aa_prob_cuore.info())

# questi son tutti a 0 quindi li commento
# print(sum(aa_prob_cuore["annodiagnosidiabete"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annoprimoaccesso"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annodecesso"] < aa_prob_cuore["annonascita"]))  # 0
# print(sum(aa_prob_cuore["annodecesso"] > 2022))  # 0
# print(sum(aa_prob_cuore["annonascita"] < 0))  # 0

# 7 pazienti hanno la data di primo accesso maggiore della data di decesso -> da scartare
print(
    "numero righe con data di primo accesso maggiore della data di decesso: ",
    sum(aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]),
)  # 14 righe di cui 7 unici

print(
    "numero pazienti unici con data di primo accesso maggiore della data di decesso: ",
    len(
        aa_prob_cuore[aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]][
            ["idana", "idcentro"]
        ].drop_duplicates()
    ),
)

# 5 pazienti hanno la data di diagnosi di diabete maggiore della data di decesso -> da scartare
print(
    "numero righe con data di diagnosi di diabete maggiore della data di decesso: ",
    sum(aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]),
)  # 9 righe di cui 5 unici

print(
    "numero pazienti unici con data di diagnosi di diabete maggiore della data di decesso: ",
    len(
        aa_prob_cuore[
            aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]
        ][["idana", "idcentro"]].drop_duplicates()
    ),
)

print(
    "numero righe con anno diagnosi diabete a N/A: ",
    sum(aa_prob_cuore["annodiagnosidiabete"].isna()),
)  # 2234

print(
    "numero pazienti unici con anno diagnosi diabete a N/A: ",
    len(
        aa_prob_cuore[aa_prob_cuore["annodiagnosidiabete"].isna()][
            ["idana", "idcentro"]
        ].drop_duplicates()
    ),
)  # 526

# in anagrafica abbiamo solo pazienti con diagnosi di diabete di tipo 2 valore 5 in 'tipodiabete'
# quindi possiamo fillare l'annodiagnosidiabete con l'annoprimoaccesso
print(
    "numero righe con anno diagnosi diabete a N/A ma con anno primo accesso presente: ",
    len(
        aa_prob_cuore[
            aa_prob_cuore["annodiagnosidiabete"].isna()
            & aa_prob_cuore["annoprimoaccesso"].notnull()
        ][["idana", "idcentro"]]
    ),
)  # 1797


def printSexInfo(dataset):
    dataset = dataset[["idcentro", "idana", "sesso"]].drop_duplicates()
    print("numero righe del df: ", len(dataset))

    print("Sex info")
    print(dataset["sesso"].unique())
    print("sesso ad N/A", dataset["sesso"].isna().sum())
    print("Maschi: ", sum(dataset["sesso"].isin(["M"])))
    print("Femmine: ", sum(dataset["sesso"].isin(["F"])))


#    dataset['sesso'].plot(kind='kde')


def getDeaseasePercentage(dataset, deaseases):
    print("Deasease: ", deaseases)
    # print(dataset.columns)
    percent = "Percentage of deasease:\n"
    dataset = dataset[["idcentro", "idana", "codiceamd"]].drop_duplicates()
    print("numero righe del df: ", len(dataset))

    for deasease in deaseases:
        # print("Deasease: ", deasease)
        tempdataset = dataset[dataset["codiceamd"].isin([deasease])]
        tempdataset2 = tempdataset[["idana", "idcentro"]].drop_duplicates()
        total = len(dataset[["idana", "idcentro"]].drop_duplicates())
        percent += (
            deasease
            + ": "
            + str(len(tempdataset2) / total * 100)
            + "%\t"
            + str(len(tempdataset2))
            + " su "
            + str(total)
            + "\n"
        )
    print(percent)


def getInfoOnDiagnosi(df):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Info on diagnosi")
    print(
        "il dizionario stampato è formattato così: 'chiave': [minori, uguali, maggiori] rispetto a data"
    )
    dates = ["annodiagnosidiabete", "annonascita", "annoprimoaccesso", "annodecesso"]
    stampami = dict()
    df = df[
        [
            "idcentro",
            "idana",
            "annodiagnosidiabete",
            "annonascita",
            "annoprimoaccesso",
            "annodecesso",
            "data",
        ]
    ].drop_duplicates()

    print("numero righe del df: ", len(df))

    for d in dates:
        df["extra"] = df["data"].dropna().str[:4]
        df["extra"] = df["extra"].astype(float)
        minor = (df[d].astype(float) < df["extra"]).sum()
        equal = (df[d].astype(float) == df["extra"]).sum()
        more = (df[d].astype(float) > df["extra"]).sum()
        stampami[d] = [minor, equal, more]

    print(stampami)


getInfoOnDiagnosi(aa_prob_cuore)
# Sesso
print("In anagrafica attivi abbiamo:")
printSexInfo(df_anagrafica_attivi)
print("Fra i pazienti con problemi al cuore abbiamo:")
printSexInfo(aa_prob_cuore)
# Deasease Distribution
getDeaseasePercentage(aa_prob_cuore, amd_of_cardiovascular_event)
# TODO: qui i numeri non tornano quindi significa che stessi pazienti hanno avuto più codici amd diversi
# ora vai a capire in ambito medico se significa che hanno più problemi diversi o che hanno avuto diverse diagnosi,
# che la malattia progredisce e quindi cambia codice amd, bho
# provo a capire quali sono i pazienti che hanno avuto più codici amd diversi:
print(
    "numero pazienti con più codici amd diversi: ",
    len(
        aa_prob_cuore[aa_prob_cuore[["idana", "idcentro"]].duplicated(keep=False)][
            ["idana", "idcentro"]
        ].drop_duplicates()
    ),
)

# print(
#     "pazienti con più codici amd diversi: ",
#     aa_prob_cuore[aa_prob_cuore[["idana", "idcentro"]].duplicated(keep=False)][["idana", "idcentro"]].drop_duplicates(),
# )

print(
    "numero pazienti con un unico codice amd: ",
    len(
        aa_prob_cuore[~aa_prob_cuore[["idana", "idcentro"]].duplicated(keep=False)][
            ["idana", "idcentro"]
        ].drop_duplicates()
    ),
)

# TODO: qui si potrebbe calcolare anche qual'è la percentuale in base al sesso e casomai anche per età
del df_anagrafica_attivi

print(
    "righe da eliminare: ",
    aa_prob_cuore[aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]],
)
aa_prob_cuore = aa_prob_cuore.drop(
    aa_prob_cuore[
        aa_prob_cuore["annoprimoaccesso"] > aa_prob_cuore["annodecesso"]
    ].index,
)
print(len(aa_prob_cuore[["idana", "idcentro"]].drop_duplicates()))

print(
    "righe da eliminare: ",
    aa_prob_cuore[aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]],
)
aa_prob_cuore = aa_prob_cuore.drop(
    aa_prob_cuore[
        aa_prob_cuore["annodiagnosidiabete"] > aa_prob_cuore["annodecesso"]
    ].index,
)

print("dopo scarto :")
print(len(aa_prob_cuore[["idana", "idcentro"]].drop_duplicates()))

# siccome più della metà dei pazienti che hanno problemi al cuore
# hanno l'anno di diagnosi di diabete minore dell'anno di primo accesso
# noi abbiamo deciso di fillare l'annodiagnosidiabete con l'anno primo accesso
print(
    "numero pazienti unici con anno diagnosi diabete minore dell'anno primo accesso: ",
    len(
        aa_prob_cuore[
            aa_prob_cuore["annodiagnosidiabete"] < aa_prob_cuore["annoprimoaccesso"]
        ][["idana", "idcentro"]].drop_duplicates()
    ),
)  # 27592

aa_prob_cuore.loc[
    aa_prob_cuore["annodiagnosidiabete"].isna()
    & aa_prob_cuore["annoprimoaccesso"].notnull(),
    "annodiagnosidiabete",
] = aa_prob_cuore["annoprimoaccesso"]

print("All filtered :")
aa_prob_cuore = aa_prob_cuore.dropna(subset="annodiagnosidiabete")
print(len(aa_prob_cuore[["idana", "idcentro"]].drop_duplicates()))  # 49829


### TODO Punto 2 per dataset diversi da anagrafica attivi e diagnosi (?)
## Carica i dataset
print("############## LOADING DATASETS ##############")

df_esami_par = df_list["esamilaboratorioparametri"].result()
# pd.read_csv("sample/esamilaboratorioparametri.csv", header=0, index_col=False)
print("loaded esami parametri")

df_esami_par_cal = df_list["esamilaboratorioparametricalcolati"].result()
# pd.read_csv("sample/esamilaboratorioparametricalcolati.csv", header=0, index_col=False)
print("loaded esami parametri calcolati")

df_esami_stru = df_list["esamistrumentali"].result()
# pd.read_csv("sample/esamistrumentali.csv", header=0, index_col=False)
print("loaded esami strumentali")

df_diagnosi = df_list["diagnosi"].result()
# pd.read_csv("sample/diagnosi.csv", header=0, index_col=False)
print("loaded diagnosi")

df_prescrizioni_diabete_farmaci = df_list["prescrizionidiabetefarmaci"].result()
# pd.read_csv("sample/prescrizionidiabetefarmaci.csv", header=0, index_col=False)
print("loaded prescrizioni diabete farmaci")

df_prescrizioni_diabete_non_farmiaci = df_list["prescrizionidiabetenonfarmaci"].result()
# pd.read_csv("sample/prescrizionidiabetenonfarmaci.csv", header=0, index_col=False)
print("loaded prescrizioni diabete non farmaci")

df_prescirizioni_non_diabete = df_list["prescrizioninondiabete"].result()
# pd.read_csv("sample/prescrizioninondiabete.csv", header=0, index_col=False)
print("loaded prescrizioni non diabete")
del df_list

## Calcola le chiavi dei pazienti di interesse
aa_cuore_key = aa_prob_cuore[
    [
        "idana",
        "idcentro",
        "annonascita",
        "annoprimoaccesso",
        "annodecesso",
    ]  # TODO: why here we need those dates?
]
aa_cuore_key = aa_cuore_key.drop_duplicates()
print(len(aa_cuore_key))

## Cast string to datatime
# all this lines can be done in 1 line like:
# aa_cuore_key["annonascita"] = pd.to_datetime(aa_cuore_key["annonascita"], format="%Y")
# whitout the need of the appo column and it is also faster ... (Antonio said)
aa_cuore_key.rename(columns={"annonascita": "appo"}, inplace=True)
aa_cuore_key["annonascita"] = pd.to_datetime(aa_cuore_key["appo"], format="%Y")
aa_cuore_key.drop(columns=["appo"], inplace=True)
aa_cuore_key.rename(columns={"annoprimoaccesso": "appo"}, inplace=True)
aa_cuore_key["annoprimoaccesso"] = pd.to_datetime(aa_cuore_key["appo"], format="%Y")
aa_cuore_key.drop(columns=["appo"], inplace=True)
aa_cuore_key.rename(columns={"annodecesso": "appo"}, inplace=True)
aa_cuore_key["annodecesso"] = pd.to_datetime(aa_cuore_key["appo"], format="%Y")

aa_cuore_key.drop(columns=["appo"], inplace=True)
print(aa_cuore_key.head())


df_esami_par.rename(columns={"data": "appo"}, inplace=True)
df_esami_par["data"] = pd.to_datetime(df_esami_par["appo"], format="%Y-%m-%d")
df_esami_par.drop(columns=["appo"], inplace=True)
df_esami_par_cal.rename(columns={"data": "appo"}, inplace=True)
df_esami_par_cal["data"] = pd.to_datetime(df_esami_par_cal["appo"], format="%Y-%m-%d")
df_esami_par_cal.drop(columns=["appo"], inplace=True)
df_esami_stru.rename(columns={"data": "appo"}, inplace=True)
df_esami_stru["data"] = pd.to_datetime(df_esami_stru["appo"], format="%Y-%m-%d")
df_esami_stru.drop(columns=["appo"], inplace=True)
df_diagnosi.rename(columns={"data": "appo"}, inplace=True)
df_diagnosi["data"] = pd.to_datetime(df_diagnosi["appo"], format="%Y-%m-%d")
df_diagnosi.drop(columns=["appo"], inplace=True)
df_prescrizioni_diabete_farmaci.rename(columns={"data": "appo"}, inplace=True)
df_prescrizioni_diabete_farmaci["data"] = pd.to_datetime(
    df_prescrizioni_diabete_farmaci["appo"], format="%Y-%m-%d"
)
df_prescrizioni_diabete_farmaci.drop(columns=["appo"], inplace=True)
df_prescrizioni_diabete_non_farmiaci.rename(columns={"data": "appo"}, inplace=True)
df_prescrizioni_diabete_non_farmiaci["data"] = pd.to_datetime(
    df_prescrizioni_diabete_non_farmiaci["appo"], format="%Y-%m-%d"
)
df_prescrizioni_diabete_non_farmiaci.drop(columns=["appo"], inplace=True)
df_prescirizioni_non_diabete.rename(columns={"data": "appo"}, inplace=True)
df_prescirizioni_non_diabete["data"] = pd.to_datetime(
    df_prescirizioni_non_diabete["appo"], format="%Y-%m-%d"
)
df_prescirizioni_non_diabete.drop(columns=["appo"], inplace=True)


## Rimuovi pazienti non di interesse
df_esami_par = df_esami_par.merge(aa_cuore_key, on=["idana", "idcentro"], how="inner")
df_esami_par_cal = df_esami_par_cal.merge(
    aa_cuore_key, on=["idana", "idcentro"], how="inner"
)
df_esami_stru = df_esami_stru.merge(aa_cuore_key, on=["idana", "idcentro"], how="inner")
df_diagnosi = df_diagnosi.merge(aa_cuore_key, on=["idana", "idcentro"], how="inner")
df_prescrizioni_diabete_farmaci = df_prescrizioni_diabete_farmaci.merge(
    aa_cuore_key, on=["idana", "idcentro"], how="inner"
)
df_prescrizioni_diabete_non_farmiaci = df_prescrizioni_diabete_non_farmiaci.merge(
    aa_cuore_key, on=["idana", "idcentro"], how="inner"
)
df_prescirizioni_non_diabete = df_prescirizioni_non_diabete.merge(
    aa_cuore_key, on=["idana", "idcentro"], how="inner"
)

del aa_cuore_key

dfs_esami_diagnosi_and_prescrizioni = [
    df_esami_par,
    df_esami_par_cal,
    df_esami_stru,
    df_diagnosi,
    df_prescrizioni_diabete_farmaci,
    df_prescrizioni_diabete_non_farmiaci,
    df_prescirizioni_non_diabete,
]

df_esami_par = df_esami_par[df_esami_par["data"] >= df_esami_par["annonascita"]]
appo_1 = df_esami_par[df_esami_par["data"] <= df_esami_par["annodecesso"]]
appo_2 = df_esami_par[pd.isnull(df_esami_par["annodecesso"])]
df_esami_par = pd.concat([appo_1, appo_2])

# df_esami_par = pd.concat(df_esami_par[df_esami_par["data"] <= df_esami_par["annodecesso"]], df_esami_par[df_esami_par["annodecesso"] == pd.NaT])

df_esami_par_cal = df_esami_par_cal[
    df_esami_par_cal["data"] >= df_esami_par_cal["annonascita"]
]
appo_1 = df_esami_par_cal[df_esami_par_cal["data"] <= df_esami_par_cal["annodecesso"]]
appo_2 = df_esami_par_cal[pd.isnull(df_esami_par_cal["annodecesso"])]
df_esami_par_cal = pd.concat([appo_1, appo_2])
# df_esami_par_cal = pd.concat(df_esami_par_cal[df_esami_par_cal["data"] <= df_esami_par_cal["annodecesso"]], df_esami_par_cal[df_esami_par_cal["annodecesso"] == pd.NaT])

df_esami_stru = df_esami_stru[df_esami_stru["data"] >= df_esami_stru["annonascita"]]
appo_1 = df_esami_stru[df_esami_stru["data"] <= df_esami_stru["annodecesso"]]
appo_2 = df_esami_stru[pd.isnull(df_esami_stru["annodecesso"])]
df_esami_stru = pd.concat([appo_1, appo_2])
# df_esami_stru = pd.concat([df_esami_stru[df_esami_stru["data"] <= df_esami_stru["annodecesso"]], df_esami_stru[df_esami_stru["annodecesso"] == pd.NaT]])

df_diagnosi = df_diagnosi[df_diagnosi["data"] >= df_diagnosi["annonascita"]]
appo_1 = df_diagnosi[df_diagnosi["data"] <= df_diagnosi["annodecesso"]]
appo_2 = df_diagnosi[pd.isnull(df_diagnosi["annodecesso"])]
df_diagnosi = pd.concat([appo_1, appo_2])
# df_diagnosi = pd.concat([df_diagnosi[df_diagnosi["data"] <= df_diagnosi["annodecesso"]], df_diagnosi[df_diagnosi["annodecesso"] == pd.NaT]])

df_prescrizioni_diabete_farmaci = df_prescrizioni_diabete_farmaci[
    df_prescrizioni_diabete_farmaci["data"]
    >= df_prescrizioni_diabete_farmaci["annonascita"]
]
appo_1 = df_prescrizioni_diabete_farmaci[
    df_prescrizioni_diabete_farmaci["data"]
    <= df_prescrizioni_diabete_farmaci["annodecesso"]
]
appo_2 = df_prescrizioni_diabete_farmaci[
    pd.isnull(df_prescrizioni_diabete_farmaci["annodecesso"])
]
df_prescrizioni_diabete_farmaci = pd.concat([appo_1, appo_2])
# df_prescrizioni_diabete_farmaci = pd.concat([df_prescrizioni_diabete_farmaci[df_prescrizioni_diabete_farmaci["data"] <= df_prescrizioni_diabete_farmaci["annodecesso"]], df_prescrizioni_diabete_farmaci[df_prescrizioni_diabete_farmaci["annodecesso"] == pd.NaT]])

df_prescrizioni_diabete_non_farmiaci = df_prescrizioni_diabete_non_farmiaci[
    df_prescrizioni_diabete_non_farmiaci["data"]
    >= df_prescrizioni_diabete_non_farmiaci["annonascita"]
]
appo_1 = df_prescrizioni_diabete_non_farmiaci[
    df_prescrizioni_diabete_non_farmiaci["data"]
    <= df_prescrizioni_diabete_non_farmiaci["annodecesso"]
]
appo_2 = df_prescrizioni_diabete_non_farmiaci[
    pd.isnull(df_prescrizioni_diabete_non_farmiaci["annodecesso"])
]
df_prescrizioni_diabete_non_farmiaci = pd.concat([appo_1, appo_2])
# df_prescrizioni_diabete_non_farmiaci = pd.concat([df_prescrizioni_diabete_non_farmiaci[df_prescrizioni_diabete_non_farmiaci["data"] <= df_prescrizioni_diabete_non_farmiaci["annodecesso"]], df_prescrizioni_diabete_non_farmiaci[df_prescrizioni_diabete_non_farmiaci["annodecesso"] == pd.NaT]])

df_prescirizioni_non_diabete = df_prescirizioni_non_diabete[
    df_prescirizioni_non_diabete["data"] >= df_prescirizioni_non_diabete["annonascita"]
]
appo_1 = df_prescirizioni_non_diabete[
    df_prescirizioni_non_diabete["data"] <= df_prescirizioni_non_diabete["annodecesso"]
]
appo_2 = df_prescirizioni_non_diabete[
    pd.isnull(df_prescirizioni_non_diabete["annodecesso"])
]
df_prescirizioni_non_diabete = pd.concat([appo_1, appo_2])

# df_prescirizioni_non_diabete = pd.concat([df_prescirizioni_non_diabete[df_prescirizioni_non_diabete["data"] <= df_prescirizioni_non_diabete["annodecesso"]], df_prescirizioni_non_diabete[df_prescirizioni_non_diabete["annodecesso"] == pd.NaT]])
print("Pulite le date")
### TODO Punto 3
## Append datasets
print("############## POINT 3 START ##############")
df_diagnosi_and_esami = pd.concat(
    [df_diagnosi, df_esami_par, df_esami_par_cal, df_esami_stru], ignore_index=True
)
print("lunghezza df_diagnosi_and_esami: ")
df_diagnosi_and_esami_keys = df_diagnosi_and_esami[["idana", "idcentro"]]
df_diagnosi_and_esami_keys = df_diagnosi_and_esami_keys.drop_duplicates()

groups_diagnosi_and_esami = df_diagnosi_and_esami.groupby(["idana", "idcentro"]).agg(
    {"data": ["min", "max"]}
)
"""
groups_diagnosi_and_esami["data_min"] = pd.to_datetime(
    groups_diagnosi_and_esami["data"]["min"], format="%Y-%m-%d"
)
groups_diagnosi_and_esami["data_max"] = pd.to_datetime(
    groups_diagnosi_and_esami["data"]["max"], format="%Y-%m-%d"
)
"""
groups_diagnosi_and_esami["data_min"] = groups_diagnosi_and_esami["data"]["min"]
groups_diagnosi_and_esami["data_max"] = groups_diagnosi_and_esami["data"]["max"]
print(groups_diagnosi_and_esami.head(30))
print("trovato")

"""
groups_diagnosi_and_esami["data_min"] = pd.to_datetime(
    groups_diagnosi_and_esami["data"]["min"], format="%Y-%m-%d"
)
groups_diagnosi_and_esami["data_max"] = pd.to_datetime(
    groups_diagnosi_and_esami["data"]["max"], format="%Y-%m-%d"
)
"""
groups_diagnosi_and_esami["diff"] = (
    groups_diagnosi_and_esami["data_max"] - groups_diagnosi_and_esami["data_min"]
)
print(groups_diagnosi_and_esami.head(30))
print(
    len(
        groups_diagnosi_and_esami[
            groups_diagnosi_and_esami["diff"] == pd.Timedelta("0 days")
        ]
    )
)
print(
    len(
        groups_diagnosi_and_esami[
            groups_diagnosi_and_esami["diff"] < pd.Timedelta("30 days")
        ]
    )
)

groups_diagnosi_and_esami = groups_diagnosi_and_esami[
    groups_diagnosi_and_esami["diff"] > pd.Timedelta("30 days")
]
groups_diagnosi_and_esami = groups_diagnosi_and_esami.sort_values(by=["diff"])
print(groups_diagnosi_and_esami.head())
print(groups_diagnosi_and_esami.tail())
print(len(groups_diagnosi_and_esami))

wanted_amd_par = ["AMD004", "AMD005", "AMD006", "AMD007", "AMD008", "AMD009", "AMD111"]
wanted_stitch_par = ["STITCH001", "STITCH002", "STITCH003", "STITCH004", "STITCH005"]

### TODO: Punto 4
# df esami par
print("############## POINT 4 START ##############")

print("prima update: ")
amd004 = df_esami_par[df_esami_par["codiceamd"] == "AMD004"]["valore"]
print("numero AMD004 minori di 40: ", len(amd004[amd004.astype(float) < 40]))
print("numero AMD004 maggiori di 200: ", len(amd004[amd004.astype(float) > 200]))


df_esami_par["valore"].update(
    df_esami_par[df_esami_par["codiceamd"] == "AMD004"]["valore"].clip(40, 200)
)
df_esami_par["valore"].update(
    df_esami_par[df_esami_par["codiceamd"] == "AMD005"]["valore"].clip(40, 130)
)
df_esami_par["valore"].update(
    df_esami_par[df_esami_par["codiceamd"] == "AMD007"]["valore"].clip(50, 500)
)
df_esami_par["valore"].update(
    df_esami_par[df_esami_par["codiceamd"] == "AMD008"]["valore"].clip(5, 15)
)

print("dopo update: ")
amd004_dopo = df_esami_par[df_esami_par["codiceamd"] == "AMD004"]["valore"]

print("numero AMD004 minori di 40: ", len(amd004_dopo[amd004_dopo < 40]))
print(
    "numero AMD004 maggiori di 200: ", len(amd004_dopo[amd004_dopo.astype(float) > 200])
)

print("prima update: ")

stitch002 = df_esami_par_cal[df_esami_par_cal["codicestitch"] == "STITCH002"]["valore"]
print("numero STITCH001 minori di 30: ", len(stitch002[stitch002.astype(float) < 30]))
print(
    "numero STITCH001 maggiori di 300: ", len(stitch002[stitch002.astype(float) > 300])
)

df_esami_par_cal["valore"].update(
    df_esami_par_cal[df_esami_par_cal["codicestitch"] == "STITCH002"]["valore"].clip(
        30, 300
    )
)
df_esami_par_cal["valore"].update(
    df_esami_par_cal[df_esami_par_cal["codicestitch"] == "STITCH003"]["valore"].clip(
        60, 330
    )
)

stitch002_dopo = df_esami_par_cal[df_esami_par_cal["codicestitch"] == "STITCH002"][
    "valore"
]


print(
    "numero STITCH001 minori di 30: ",
    len(stitch002_dopo[stitch002_dopo < 30]),
)
print(
    "numero STITCH001 maggiori di 300: ",
    len(stitch002_dopo[stitch002_dopo.astype(float) > 300]),
)

### TODO: Punto 5
print("############## POINT 5 START ##############")

patients_keys = df_diagnosi_and_esami[["idana", "idcentro"]].drop_duplicates()
aa_prob_cuore_filtered = pd.merge(
    aa_prob_cuore,
    patients_keys,
    on=["idana", "idcentro"],
    how="inner",
)
print("aa_prob_cuore_filtered merged")
df_prescrizioni_diabete_farmaci = df_prescrizioni_diabete_farmaci.merge(
    patients_keys,
    on=["idana", "idcentro"],
    how="inner",
)
print("df_prescrizioni_diabete_farmaci merged")
df_prescirizioni_non_diabete = df_prescirizioni_non_diabete.merge(
    patients_keys,
    on=["idana", "idcentro"],
    how="inner",
)
print("df_prescirizioni_non_diabete merged")
df_prescrizioni_diabete_non_farmiaci = df_prescrizioni_diabete_non_farmiaci.merge(
    patients_keys,
    on=["idana", "idcentro"],
    how="inner",
)
print("df_prescrizioni_diabete_non_farmiaci merged")

df_diagnosi_and_esami_and_prescrioni = pd.concat(
    [
        df_diagnosi_and_esami,
        df_prescrizioni_diabete_farmaci,
        df_prescirizioni_non_diabete,
        df_prescrizioni_diabete_non_farmiaci,
    ]
)
print("df_diagnosi_and_esami_and_prescrioni concatenated")
cont = (
    df_diagnosi_and_esami_and_prescrioni[["idana", "idcentro"]]
    .groupby(["idana", "idcentro"])
    .size()
    .reset_index(name="count")
)
print("cont grouped")
cont_filtered = cont[cont["count"] >= 2]

select = df_diagnosi_and_esami_and_prescrioni.merge(
    cont_filtered, on=["idana", "idcentro"], how="inner"
)

print(select)

# select["data"] = pd.to_datetime(select["data"], format="%Y-%m-%d")

last_event = select.groupby(["idana", "idcentro"], group_keys=True)["data"].max()

print(last_event)
df_problemi_cuore = df_diagnosi_problemi_cuore.merge(
    patients_keys,
    on=["idana", "idcentro"],
    how="inner",
)
df_problemi_cuore["data"] = pd.to_datetime(df_problemi_cuore["data"], format="%Y-%m-%d")

last_problem = df_problemi_cuore.groupby(["idana", "idcentro"], group_keys=True)[
    "data"
].max()

print(last_problem)

wanted_patient = select.join(
    (
        last_problem.reset_index(drop=True).ge(
            pd.to_datetime(
                last_event.reset_index(drop=True) - pd.Timedelta("180 days"),
                format="%Y-%m-%d",
            )
        )
    ).rename("label")
)
print(wanted_patient[["idana", "idcentro", "data", "label"]])
wanted_patient = wanted_patient[wanted_patient["label"] == True]
print("RISULATI PUNTO 1.5")
print(wanted_patient)
print(len(wanted_patient))
patients_keys = wanted_patient[["idana", "idcentro"]].drop_duplicates()
print(len(patients_keys))
### TODO: Punto 6
