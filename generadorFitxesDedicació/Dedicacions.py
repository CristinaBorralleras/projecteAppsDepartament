import openpyxl as ope
import sys

def getVal(v):
    if v == None:
        return 0
    else:
        return v
        
def getCad(v):
    if v == None:
        return ''
    else:
        return v

def arrodFloat(v):
        vI = int(v)
        vF = float(v)
        if vI == vF:
            return vI
        else:
            return round(vF,1)
        
class Dedicacions:

    def __init__(self,fileName):

        self.doc = self.getFile(fileName) 
        self.fullPDI = self.getSheet(self.doc,'Total_Dedicació_PDI')
        self.fulldetalldoc = self.getSheet(self.doc,'DOCÈNCIA 26_27')
        self.fullPDIAltresCentres = self.getSheet(self.doc,'PDI_Formac_AAA_Doctor_Acr')        
        self.fullGestio = self.getSheet(self.doc,'Gestió')
        self.fullPracGEA = self.getSheet(self.doc,'PRÀCT')
        self.setPDIambCPI = set()
        self.createStructure()


    def createStructure(self):
        (self.dAss,self.dFix)=self.creadicPDI(self.fullPDI)
        (self.ddetdoc,self.dAssGProf,self.dAssCursSem)=self.creadicDetall(self.fulldetalldoc,self.dAss,self.dFix)
        self.calculHoresAltresCentres(self.dAss,self.ddetdoc)
        (self.dPDIPracGEA,self.dAssPracGEA)=self.creadicPracGEA(self.fullPracGEA)
        self.dGestio=self.creadicGestio(self.fullGestio,self.dFix)
        
    def getDetallPDIPracGEA(self):
        return self.dPDIPracGEA
    
    def getDetallAssPracGEA(self):
        return self.dAssPracGEA

    def getAssCursSem(self):
        return self.dAssCursSem
    
    def getPDIFix(self):
        return self.dFix

    def getPDIAss(self):
        return self.dAss
    
    def getDetallDocencia(self):
        return self.ddetdoc

    def getAssProf(self):
        return self.dAssGProf

    def getPDIambCPI(self):
        return self.setPDIambCPI

    def getHoresDocencia(self,pdi):
        if pdi in self.dAss:
            return self.dAss[pdi]["docenciaTot"]+self.gethoresPracGEA(pdi)
        elif pdi in self.dFix:
            return self.dFix[pdi]["docenciaTot"]+self.gethoresPracGEA(pdi)
        else:
            print(pdi,"no existeix")
            return 0

    def getHoresAltresCentres(self,pdi):
        if pdi in self.dAss:
            return self.dAss[pdi]['docenciaTot']
        else:
            return 0

    def getTotalHores(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["totalHores"]
        else:
            print(pdi,"no existeix")
            return 0

    def getTotalEcts(self,pdi):
        if pdi in self.dAss:
            return self.dAss[pdi]["ects"] 
        elif pdi in self.dFix:
            return self.dFix[pdi]["ects"]
        else:
            print(pdi,"no existeix")
            return 0
        
    def getHoresPendent(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["totalHoresPendents"]
        else:
            print(pdi,"no existeix")
            return 0 

    def getRecerca(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["recerca"]
        else:
            print(pdi,"no existeix")
            return 0

    def getFormacio(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["formacio"]
        else:
            print(pdi,"no existeix")
            return 0

    def getDept(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["dept"]
        elif pdi in self.dAss:
            return self.dAss[pdi]["dept"]
        else:
            return ""
        
    def getAA(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["AA"]
        else:
            print(pdi,"no existeix")
            return 0

    def getGestio(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["gestio"]
        else:
            print(pdi,"no existeix")
            return 0

    def getdGestio(self):
        return self.dGestio
    
    def getObservacions(self,pdi):
        if pdi in self.dFix:
            if self.dFix[pdi]["observacions"]=='':
                return '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp-'
            else:
                return self.dFix[pdi]["observacions"]
        else:
            print(pdi,"no existeix")
            return 0

    def gethoresPracGEA(self,pdi):
        nhores=0
        if pdi in self.dPDIPracGEA:
            for assig in self.dPDIPracGEA[pdi]:
                nhores+=self.dPDIPracGEA[pdi][assig][0]
        return nhores

    def gethorestutTFG(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["tfg"]
        else:
            return 0

    def gethoresTribTFG(self,pdi):
        if pdi in self.dFix:
            return self.dFix[pdi]["tribunals"]
        else:
            return 0

    def gethoresPrac(self,pdi):
        if pdi in self.dFix:
            if pdi in self.dPDIPracGEA:
                return self.dFix[pdi]["practiques"]-self.gethoresPracGEA(pdi)
            else:
                return self.dFix[pdi]["practiques"]
        else:
            return 0
   

    def afegirPDIAltresCentres(self,full,dFix,dAss):
        for row in full:
            try:
                nom=str(getCad(row[0].value)).upper()
                departament=str(getCad(row[2].value)).upper()
                if nom not in dFix and nom not in dAss:
                    if departament not in ["DEPARTAMENT DE BIOCIÈNCIES","DEPARTAMENT D'ENGINYERIES",""]:
                        dAss[nom]={"dept":departament,"cat":'',"docenciaTot":0,"docenciaMasterTot":0,"observacions":'Altre centre',"ects":0,"ectsMaster":0}
            except:
                pass #print("fila de GlobalProfessorat no tractada")
    
    
    def creadicPDI(self,full):
        dAss={}
        dFix={}
        for row in full.rows:
            dept=str(getCad(row[1].value)).strip().upper()
            nom=str(getCad(row[0].value)).strip().upper() 
            if dept == "DEPARTAMENT D'ENGINYERIES" or dept == "DEPARTAMENT DE BIOCIÈNCIES": 
                cat = str(getCad(row[2].value)).upper()
                if "ASSOCIAT/DA" in cat or "INVESTIGADOR" in cat or "PAS" in cat or "AJUDANT" in cat or "ALTRES" in cat or "TEKNOS" in cat or "TÈCNIC" in cat:
                    docencia=getVal(row[10].value)
                    if docencia>0:
                        ects=round(getVal(row[7].value),2)
                        observacions=self.setObs(getVal(row[18].value),getVal(row[19].value),getVal(row[20].value),getVal(row[21].value),0)
                        dAss[nom]={"dept":dept,"cat":cat,"docenciaTot":docencia,"observacions":observacions,"ects":ects}
                elif "BAIXA" not in cat:
                    jornada=getVal(row[3].value)
                    if jornada=="TC":
                        horesDed=1600
                    elif jornada=="TP1":
                        horesDed=1200
                    elif jornada=="TP2":
                        horesDed=800
                    else:
                        horesDed=0
                    docencia=getVal(row[10].value)
                    ects=round(getVal(row[7].value),2)               
                    recerca=getVal(row[12].value)
                    gestio=getVal(row[11].value)
                    formacio=getVal(row[13].value)
                    altraAct=getVal(row[14].value)
                    TFG=getVal(row[15].value)
                    practiques=getVal(row[16].value)
                    tesisLlegides=getVal(row[17].value)
                    totalHores=getVal(row[8].value)
                    totalHoresCPI=getVal(row[25].value)
                    #totalHoresPendents=horesDed-totalHores
                    totalHoresPendents=-getVal(row[9].value)
                    observacions=self.setObs(getVal(row[18].value),getVal(row[19].value),getVal(row[20].value),getVal(row[21].value),tesisLlegides)
                    dFix[nom]={"dept":dept, "cat":cat,"docenciaTot":docencia,"recerca":recerca,"gestio":gestio,"formacio":formacio,"AA":altraAct,
                               "totalHores":totalHores,"totalHoresPendents":totalHoresPendents,"observacions":observacions,
                               "ects":ects,"tfg":TFG,"practiques":practiques,"tesis llegides":tesisLlegides, "totalHoresCPI":totalHoresCPI}
        
        self.afegirPDIAltresCentres(self.fullPDIAltresCentres,dFix,dAss)
        return(dAss,dFix)

    def setObs(self,fcsb,fetep,fec,fm,tesis):
        if tesis>0:
            cat="Dir. tesis: "+str(tesis)+"h "
        else:
            cat=''
        if fetep>0:
            cat+="FETEP: "+str(fetep)+"h  "
        if fcsb>0:
            cat+="FCSB: "+str(fcsb)+"h  "
        if fec>0:
            cat+="FEC: "+str(fec)+"h  "
        if fm>0:
            cat+="FM: "+str(fm)+"h  "
        return cat
            

    def creadicPracGEA(self,full):
        dPDIPracGEA={}
        dAssPracGEA={}
        for row in full.rows:
            if "AUTOMOCIÓ" in str(getCad(row[0].value)).strip().upper():
                pdi = str(getCad(row[7].value)).strip().upper()
                assig = str(getCad(row[2].value)).strip()
                hores = getVal(row[10].value)
                horesAAA = getVal(row[12].value)
                responsableAssig = str(getCad(row[17].value)).strip().upper() == "SI"
                if hores>0 or horesAAA>0:
                    if pdi in dPDIPracGEA:
                        if assig in dPDIPracGEA[pdi]:
                            dPDIPracGEA[pdi][assig] = (dPDIPracGEA[pdi][assig][0]+hores, dPDIPracGEA[pdi][assig][0]+horesAAA, responsableAssig)
                        else:
                            dPDIPracGEA[pdi][assig] = (hores, horesAAA, responsableAssig)
                    else:
                            dPDIPracGEA[pdi] = { assig : (hores, horesAAA, responsableAssig)}

                    if assig in dAssPracGEA:
                        if pdi not in dAssPracGEA[assig]:
                            dAssPracGEA[assig].append(pdi)
                    else:
                        dAssPracGEA[assig]=[pdi]
        self.addTotalHoresAssPracGEA(dPDIPracGEA,dAssPracGEA)
        return (dPDIPracGEA,dAssPracGEA)

    def addTotalHoresAssPracGEA(self,dPDIPracGEA,dAssPracGEA):
        for a in dAssPracGEA:
            totalhores=0
            totalhoresAAA=0
            for pdi in dAssPracGEA[a]:
                totalhores=totalhores+dPDIPracGEA[pdi][a][0]
                totalhoresAAA=totalhores+dPDIPracGEA[pdi][a][1]
            dAssPracGEA[a]=(dAssPracGEA[a],totalhores,totalhoresAAA)
                
    def addTotalHoresAss(self,dAssGProf,ddetdoc):
        for a in dAssGProf:
            for g in dAssGProf[a]:
                totalhores=0
                for pdi in dAssGProf[a][g]:
                    for e in ddetdoc[pdi][a][g]:
                        totalhores=totalhores+e[2]
                dAssGProf[a][g]=(dAssGProf[a][g],totalhores)
    

    def initTFGPract(self,d,dAss,dFix):
        for k in dAss:
            d[k]=[0,0,0]
        for k in dFix:
            d[k]=[0,0,0]
        d['DOCÈNCIA ASSIGNABLE']=[0,0,0]
        d['CONFERÈNCIES']=[0,0,0]

    def convStr(self,c_s): #c_s in [1,2,3,4]
        if c_s in [1,3]:
            return str(c_s)+"r"
        elif c_s == 2:
            return str(c_s)+"n"
        elif c_s == 4:
            return str(c_s)+"t"
        else:
            return str(c_s)
        
    def addAssignCursSem(self,dAssCursSem,grau,assig,curs,semestre):
        if grau in dAssCursSem:
            if assig not in dAssCursSem[grau]:
                dAssCursSem[grau][assig]=(curs,semestre)
        else:
            dAssCursSem[grau]={assig:(curs,semestre)}
            
    def creadicDetall(self,fulldetalldoc,dAss,dFix):
        i=0
        ddetdoc={}
        dAssGProf={}
        dAssCursSem={"Enginyeria de l'Automoció":{"Pràctiques en Empresa I":("3r","2n"),"Pràctiques en Empresa II":("3r","2n"),
                                                   "Pràctiques en Empresa III":("4t","1r"),"Pràctiques en Empresa IV":("4t","1r")}}
        for (i,row) in enumerate(fulldetalldoc.rows):
            if i==0:
                continue
            nom=str(getCad(row[19].value)).strip().upper()
            dept=str(getCad(row[18].value)).strip().upper()
            if nom=='DOCÈNCIA NO ASSIGNABLE':
                continue
            if nom=='':
                nom='DOCÈNCIA ASSIGNABLE'
            grau=getCad(row[0].value)
            assig=getCad(row[6].value)
            curs=getCad(row[2].value)
            semestre=getCad(row[3].value)
            if assig=='':
                break
            categ = getCad(row[7].value)
            horesReals = arrodFloat(getVal(row[20].value))
            horesAdd = arrodFloat(getVal(row[21].value))
            horesTotal = arrodFloat(getVal(row[23].value))
            horesCPI = arrodFloat(getVal(row[22].value))
            if horesCPI > 0:
                self.setPDIambCPI.add(nom)
            if horesTotal > 0 or horesCPI > 0:
                self.addAssignCursSem(dAssCursSem,grau,assig,self.convStr(curs),self.convStr(semestre))
                tipGrup = getCad(row[11].value)              
                if "GC_" in tipGrup or "DOC_FD" in tipGrup or "LAB" in tipGrup or "ABP" in tipGrup or "SEMINARI" in tipGrup:
                    codiGrup = str(getVal(row[9].value))
                    if "GC_" in tipGrup:
                        tipGrup = 'Grup_'+codiGrup+'  '
                    elif "DOC_FD" in tipGrup:
                        tipGrup = 'DOC_FD_'+codiGrup+'  '
                    else:
                        tipGrup = 'Subgrup_'+codiGrup+'  '
                    angles = int(getVal(row[17].value))>0 
                    coordABP = int(getVal(row[15].value))>0 
                    responsableAssig = (getCad(row[29].value).strip().upper()=='SI') 
                    if nom in ddetdoc:
                        if assig in ddetdoc[nom]:
                            if grau in ddetdoc[nom][assig]:
                                ddetdoc[nom][assig][grau].append((horesReals,horesAdd,horesTotal,horesCPI,tipGrup,angles,coordABP,responsableAssig))
                            else:
                                ddetdoc[nom][assig][grau]=[(horesReals,horesAdd,horesTotal,horesCPI,tipGrup,angles,coordABP,responsableAssig)]
                        else:
                            ddetdoc[nom][assig]={grau:[(horesReals,horesAdd,horesTotal,horesCPI,tipGrup,angles,coordABP,responsableAssig)]}
                    else:
                        ddetdoc[nom]={assig:{grau:[(horesReals,horesAdd,horesTotal,horesCPI,tipGrup,angles,coordABP,responsableAssig)]}}
                            
                    if assig in dAssGProf:
                        if grau in dAssGProf[assig]:
                            if nom not in dAssGProf[assig][grau]:
                                dAssGProf[assig][grau].append(nom)
                        else:
                            dAssGProf[assig][grau]=[nom]
                    else:
                        dAssGProf[assig]={grau:[nom]}
                    
        self.addTotalHoresAss(dAssGProf,ddetdoc)
        return (ddetdoc,dAssGProf,dAssCursSem)


    def creadicGestio(self,full,dFix):
        d={}
        for row in full.rows:
            try:
                nom=str(getCad(row[1].value)).strip().upper()
                hores=str(getCad(row[3].value)).strip()
                if (hores!='0' and hores!='') or (str(getCad(row[6].value)).upper() == "RESPONSABLE ÀREA"): 
                    if hores == '0':
                        hores = ''
                    if nom in dFix:
                        if nom in d:
                            d[nom].append((getCad(row[5].value),hores))
                        else:
                            d[nom]=[(getCad(row[5].value),hores)]
            except:
                pass
        return d

    
    def calculHoresAltresCentres(self,dAss,ddetdoc):
        toRemove=[]
        for pdi in dAss:
            hores=0
            if dAss[pdi]["observacions"]=="Altre centre":
                if pdi in ddetdoc:
                    for ass in ddetdoc[pdi]:
                        for g in ddetdoc[pdi][ass]:
                            for e in ddetdoc[pdi][ass][g]:
                                hores=hores+e[2]
                dAss[pdi]['docenciaTot']=hores
                if hores==0:
                    toRemove.append(pdi)
        for pdi in toRemove:
            del dAss[pdi]

                
    def getSheet(self,doc,sheetName):
        try:
            full=doc[sheetName]
            return full
        except:
            print("El full "+sheetName+" no existeix")
            sys.exit(0)
    

    def getFile(self,fileName):
        try:
            doc = ope.load_workbook(fileName,data_only=True,read_only=True)
            return doc
        except:
            print("El fitxer "+fileName+" no existeix")
            sys.exit(0)


