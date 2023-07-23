import numpy as np
import pandas as pd
import re
from datetime import datetime

def parsedatetime(x, y, z):
    datahora = x + ' ' + y + ' ' + z
    return datetime.strptime(datahora, '%m/%d/%Y %H:%M:%S %p')

def convToFloat( val):
    result = re.sub('\s+', '' , val)
    return float(result)

def calcConsumoCPU(idle):
    return float(100 - idle)

def retirarCaracterEspeciaisData(valor):
    valordata = valor
    valordata = re.sub('\[', '' , valordata)
    valordata = re.sub('\'', '' , valordata)
    valordata = re.sub('\]', '' , valordata)
    return valordata
    
class Cpusar:
    
    cpuDataFrame = pd.DataFrame()
    COLUMNS = ['Data','Hora', 'AmPm', 'CPU','User','Nice','System','Iowait','Steal','Idle']
    FILE = ''
    dataarquivo = ''
    PADRAO_DADOS_CPU = '(\d+:){2}\d+(\s+\w+){2}(\s+\d+\.\d+){6}'
    PADRAO_SAR_DATA = '(\S+\s+){5}\W\d+\s+CPU\W'
    
    def __init__(self, path):
        self.path = path
    
    def getDataframe(self):
        self.tratarDados()
        self.carregarDadosTratados()
        return self.cpuDataFrame
    
    def tratarDados(self):
        self.abrirArquivoLeituraeEscrita()
        self.processarLinhas()
        self.fechararquivos()
        
    def processarLinhas(self):
        for line in self.fileRead:
            self.capturarData(line)
            self.escreverLinhaDadosCPU(line)
    
    def escreverLinhaDadosCPU(self, linha):
        linhadados = re.findall(self.PADRAO_DADOS_CPU, linha)
        if linhadados:
            self.filewrite.write(self.dataarquivo + ' ' +linha) 
    
    def capturarData(self, linha):
        linhadata = re.findall(self.PADRAO_SAR_DATA, linha)
        if linhadata:
            splitlinha = str(linha)            
            splitlinha = splitlinha.split(' ')
            for val in splitlinha:
                strdata = re.findall('\d+/\d+/\d+', val)
                if strdata:
                    self.dataarquivo = retirarCaracterEspeciaisData(str(strdata))
    
    def fechararquivos(self):
        self.fileRead.close()
        self.filewrite.close()
        
    def abrirArquivoLeituraeEscrita(self):
        self.fileRead = open(self.path, "r")
        self.FILE = 'CPUSAR_' + datetime.now().strftime('%d%m%Y%H%M%S') + '.log'
        self.filewrite = open(self.FILE, "w")
        
    def carregarDadosTratados(self):
        self.cpuDataFrame =  pd.read_csv(self.FILE,
                   sep='\s+',
                   engine='python', 
                   na_values='-', 
                   header=None ,
                   names=self.COLUMNS,
                   converters={'User': convToFloat,
                              'Nice': convToFloat,
                              'System': convToFloat,
                              'Iowait': convToFloat,
                              'Steal': convToFloat,
                              'Idle': convToFloat}
                   )
        self.cpuDataFrame['DateTime'] = [parsedatetime(x, y, z) for x, y, z in self.cpuDataFrame[['Data','Hora', 'AmPm']].values]
        self.cpuDataFrame = self.cpuDataFrame.set_index('DateTime')
        self.cpuDataFrame = self.cpuDataFrame.sort_values(by='DateTime')
        self.cpuDataFrame['CPU %'] = [calcConsumoCPU(idle) for idle in self.cpuDataFrame[['Idle']].values]
        
   
   