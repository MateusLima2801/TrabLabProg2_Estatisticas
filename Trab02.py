import numpy as np
import mysql.connector
import math
import matplotlib.pyplot as plt

db_connection = mysql.connector.connect( host='localhost', user='root',
                        password='Dona2801#', database='Enade')

cursor = db_connection.cursor()


def retorna_estatisticas(_list):
    _media = media(_list)
    _variancia = variancia(_list, _media)
    dict = {"Media": _media, 
            "Variancia": _variancia,
            "Desvio Padrao": desvio_padrao(_variancia),
            "Moda": moda(_list),
            "Mediana": mediana(_list)}
    # for x in dict.keys():
    #     print(f"{x}: {dict[x]}")
    return dict


def media(_list):
    sum = 0.
    for x in _list:
        sum = sum + x
    return sum / len(_list)

def variancia(_list, media):
    square_sum = 0.
    for x in _list:
        square_sum += math.pow(x-media,2)
    return square_sum / len(_list)

def desvio_padrao(variancia):
    return math.sqrt(variancia)

def moda(_list):
    dict = {0.0: 0.0} 
    for x in _list:
        if(x in dict.keys()):
            dict[x] += 1
        else:
            dict[x] = 1
    sorted_dict = sorted(dict, key=dict.get, reverse= True)
    return sorted_dict[0]

def mediana(_list):
    sorted_list = sorted(_list)
    if(len(_list)%2 == 1):
        return sorted_list[int((len(_list)-1)/2)]
    else:
        return (sorted_list[int((len(_list))/2.0-1)] + sorted_list[int((len(_list))/2.0)])/2.0
        
#gerando estatisticas

cursor.execute("SELECT  e.Área_de_Avaliação, e.Conceito_Enade_Contínuo FROM enade.enade2019 as e" +
               " where e.Sigla_da_IES=\'IME\'" +
               " GROUP BY e.Área_de_Avaliação")


tabela_ime = cursor.fetchall()
linhas_ime = {}
for x in tabela_ime:
    linhas_ime[x[0]] = float(x[1])

print("Conceitos IME:")
print()
print(linhas_ime)
print()

estatisticas = {}


for x in linhas_ime:
    uni_cursor = db_connection.cursor()
    uni_cursor.execute("SELECT e.Área_de_Avaliação, e.Nome_da_IES, e.Conceito_Enade_Contínuo FROM enade.enade2019 as e"+
                   f" where e.Área_de_Avaliação LIKE \'{x}\'"+
                       "and e.Sigla_da_IES != \'IME\' and e.Conceito_Enade_Contínuo!=\'None\'")
    tabela_uni = uni_cursor.fetchall()
    linhas_uni = {}
    for x in tabela_uni:
        linhas_uni[x[1]] = float(x[2])

    estatisticas[x[0]] = retorna_estatisticas(linhas_uni.values())

print("Estatísticas Outras Universidades\n")
print(estatisticas)

engenharias = []
for x in estatisticas.keys():
    engenharias.append(x)

unis = []
concs = []
#valores totais
for x in linhas_ime:
    tot_cursor = db_connection.cursor()
    tot_cursor.execute("SELECT e.Área_de_Avaliação, e.Nome_da_IES, e.Conceito_Enade_Contínuo FROM enade.enade2019 as e" +
                   f" where e.Área_de_Avaliação LIKE \'{x}\'" +
                   " and e.Conceito_Enade_Contínuo!=\'None\'")
    tabela_tot = tot_cursor.fetchall()
    uni = []
    conc = []
    for y in tabela_tot:
        uni.append(y[1])
        conc.append(y[2])
    unis.append(uni)
    concs.append(conc)

#HISTOGRAMA
# plt.hist(unis, density=True, label = engenharias)
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)

#STAR PLOT
medias = []
media_ime = []
for x in engenharias:
    medias.append(estatisticas[x]['Media'])
    media_ime.append(linhas_ime[x])

label_loc = np.linspace(start=0, stop=((len(medias)-1)/len(medias))
                        * 2 * np.pi, num=len(medias))

plt.figure(figsize=(8, 8))
plt.subplot(polar=True)
plt.plot(label_loc, medias, label='Outras universidades')
plt.plot(label_loc, media_ime, label='IME')
plt.title('Comparação entre valores médios de conceito contínuo no Enade 2019', size=20)
lines, labels = plt.thetagrids(np.degrees(label_loc), labels=engenharias)
plt.legend()
plt.show()
plt.legend()
plt.show()


cursor.close()
db_connection.close()
