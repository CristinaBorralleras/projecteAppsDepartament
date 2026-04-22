
import sys
import os
from Dedicacions import Dedicacions
from Dedicacions import arrodFloat
import datetime
from jinja2 import Environment, FileSystemLoader
import pdfkit

def avui():
    now = datetime.datetime.now()
    return str(now.day)+"-"+str(now.month)+"-"+str(now.year)

def fillDetallDoc(pdi,dAssCursSem,ddetdoc,dpracGEA):
    cad=''
    if pdi in ddetdoc:
        for assig in ddetdoc[pdi]:
            for g in ddetdoc[pdi][assig]:
                info=ddetdoc[pdi][assig][g]
                h=sum([e[2] for e in info])
                hCPI=sum([e[3] for e in info])                
                (curs,semestre)=('-','-')
                if g in dAssCursSem:
                    if assig in dAssCursSem[g]:
                        (curs,semestre)=dAssCursSem[g][assig]
                if hCPI > 0:
                    cadA="<tr class='trLine'><td>"+assig+"</td><td>"+curs+"</td><td>"+semestre+"</td><td>"+g+"</td><td>"+str(h)+"</td><td>"+str(hCPI)+"</td></tr>"
                else:
                    cadA="<tr class='trLine'><td>"+assig+"</td><td>"+curs+"</td><td>"+semestre+"</td><td>"+g+"</td><td>"+str(h)+"</td></tr>"                
                cad=cad+cadA
            
    if pdi in dpracGEA:
        for assig in dpracGEA[pdi]:
            hores=dpracGEA[pdi][assig][0]
            horesAAA=dpracGEA[pdi][assig][1]
            if horesAAA>0:
                strhoresAAA = " +"+str(horesAAA)
            else:
                strhoresAAA = ""
            g="Enginyeria de l'Automoció"
            (curs,semestre)=('-','-')
            if g in dAssCursSem:
                    if assig in dAssCursSem[g]:
                        (curs,semestre)=dAssCursSem[g][assig]
            cadA="<tr class='trLine'><td>"+assig+"</td><td>"+curs+"</td><td>"+semestre+"</td><td>"+g+"</td><td>"+str(hores)+strhoresAAA+"</td></tr>"
            cad=cad+cadA
    return cad


def rowPDIInfo1(ass,grau,info):
    cad=""
    for e in info:
        shores=str(e[0]+e[3])
        if e[1]>0:
            shores+="(+"+str(e[1])+")"
        cad=cad+"<tr><td>"+' '+"</td><td>"+" "+"</td><td>"+" "+"</td><td>"+str(e[4])+"</td><td>"+shores+"</td></tr>"
    return cad

def rowPDIInfo2(pdi,info):
    cad=""
    responsableAssig = ""
    for e in info:
        shores=str(e[0]+e[3])
        if e[1]>0:
            shores+="(+"+str(e[1])+")"
        if e[7]: 
            responsableAssig = "*"
        cad=cad+"<tr><td>"+' '+"</td><td>"+" "+"</td><td>"+" "+"</td><td>"+str(e[4])+"</td><td>"+shores+"</td><td>"+pdi+"</td><td>"+responsableAssig+"</td></tr>"
    return cad

def fillDocPart(pdi,dAssProf,ddetdoc,dPDIPracGEA,dAssPracGEA,own):
    cad=''
    if pdi in ddetdoc:
        for assig in ddetdoc[pdi]:
            for g in ddetdoc[pdi][assig]:
                lprof=dAssProf[assig][g][0] 
                if own:
                    if len(lprof)==1:
                        cad=cad+"<tr><td>"+assig+"</td><td>"+g+"</td><td>"+str(dAssProf[assig][g][1])+"</td><td></td><td></td><td></td></tr>"
                        p=lprof[0]
                        infoP=ddetdoc[p][assig][g]
                        cad=cad+rowPDIInfo1(assig,g,infoP)
                else:
                    if len(lprof)>1:
                        cad=cad+"<tr><td>"+assig+"</td><td>"+g+"</td><td>"+str(dAssProf[assig][g][1])+"</td><td></td><td></td><td></td></tr>"
                        for p in lprof:
                            infoP=ddetdoc[p][assig][g]
                            cad=cad+rowPDIInfo2(p,infoP)
            cad=formatLastLine(cad) 
    g="Enginyeria de l'Automoció"
    if pdi in dPDIPracGEA:
        for assig in dPDIPracGEA[pdi]:
            lprof=dAssPracGEA[assig][0]
            totalHores=dAssPracGEA[assig][1]
            if own:
                if len(lprof)==1:
                    cad=cad+"<tr><td>"+assig+"</td><td>"+g+"</td><td>"+str(dAssPracGEA[assig][1])+"</td><td></td><td></td><td></td></tr>"
                    if pdi!=lprof[0]:
                        print("pdi incoherent")
                        sys.exit()
                    hores=dPDIPracGEA[pdi][assig][0]
                    horesAAA=dPDIPracGEA[pdi][assig][1]
                    cadAAA=''
                    if horesAAA>0:
                        cadAAA=" +"+str(horesAAA)
                    cad=cad+"<tr><td>"+' '+"</td><td>"+" "+"</td><td>"+" "+"</td><td>"+"Subgrup"+"</td><td>"+str(hores)+cadAAA+"</td></tr>"  
            else:
                if len(lprof)>1:
                    cad=cad+"<tr><td>"+assig+"</td><td>"+g+"</td><td>"+str(dAssPracGEA[assig][1])+"</td><td></td><td></td><td></td></tr>"
                    for p in lprof:
                        hores=dPDIPracGEA[p][assig][0]
                        horesAAA=dPDIPracGEA[p][assig][1]
                        if dPDIPracGEA[p][assig][2]:
                            respAssig = "*"
                        else:
                            respAssig = ""
                        cadAAA=''
                        if horesAAA>0:
                            cadAAA=" +"+str(horesAAA)
                        cad=cad+"<tr><td>"+' '+"</td><td>"+" "+"</td><td>"+" "+"</td><td>"+"Subgrup"+"</td><td>"+str(hores)+cadAAA+"</td><td>"+p+"</td><td>"+respAssig+"</td></tr>"  
            cad=formatLastLine(cad) 
    return cad              

def formatLastLine(cad):
    l = cad.split("<tr")
    if len(l)>1:
        l[len(l)-1]=" class='trLine'"+l[len(l)-1]
    return "<tr".join(l)
    
def fillTemplateAss(nom,ded):       #no hi ha TFG ni Practs
    propiesVisible='visible'
    compartidesVisible='visible'
    cadPropies=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),True)
    if cadPropies=='':
        propiesVisible = 'hidden'
    cadCompartides=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),False)
    if cadCompartides=='':
        compartidesVisible = 'hidden'
    
    templateV = {"nom" : nom,
                 "data": avui(),
                 "totalHores":ded.getHoresDocencia(nom),
                 "totalects":ded.getTotalEcts(nom),
                 "detallDocencia": fillDetallDoc(nom, ded.getAssCursSem(), ded.getDetallDocencia(), ded.getDetallPDIPracGEA()),
                 "docenciaParticipants1": fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),True),
                 "docenciaParticipants2": fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),False),
                 "propiesVisible":propiesVisible,
                 "compartidesVisible":compartidesVisible
                 }
    return templateV

def fillTemplateFix(nom, ded):
    
    gestioVisible='visible'
    propiesVisible='visible'
    compartidesVisible='visible'
    if nom not in ded.getdGestio():
        gestioVisible='hidden'
    cadPropies=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),True)
    if cadPropies=='':
        propiesVisible='hidden'
    cadCompartides=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),False)
    if cadCompartides=='':
        compartidesVisible='hidden'
    horesCPIVisible = "none"
    if (nom in ded.getPDIambCPI()):
        horesCPIVisible = "table-cell"
    templateV = {"nom" : nom,
                 "data": avui(),
                 "horesTutorTFG":ded.gethorestutTFG(nom),
                 "horesPract":ded.gethoresPrac(nom),
                 "horesDocencia":ded.getHoresDocencia(nom),
                 "horesRecerca":ded.getRecerca(nom),
                 "horesFormacio":ded.getFormacio(nom),
                 "horesGestio":ded.getGestio(nom),
                 "horesAA":ded.getAA(nom),
                 "horesTotal":ded.getTotalHores(nom),
                 "horesPendent":ded.getHoresPendent(nom),
                 "ects":ded.getTotalEcts(nom),
                 "observacions":ded.getObservacions(nom),
                 "detallDocencia": fillDetallDoc(nom, ded.getAssCursSem(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA()),
                 "docenciaParticipants1": cadPropies,
                 "docenciaParticipants2": cadCompartides,
                 "detallGestio":fillDetallGestio(nom,ded.getdGestio()),
                 "gestioVisible":gestioVisible,
                 "propiesVisible":propiesVisible,
                 "compartidesVisible":compartidesVisible,
                 "horesCPIVisible":horesCPIVisible
                 }
    return templateV 

def fillTemplateAltresCentres(nom,ded):       #no hi ha TFG ni Practs
    propiesVisible='visible'
    compartidesVisible='visible'
    cadPropies=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),True)
    if cadPropies=='':
        propiesVisible='hidden'
    cadCompartides=fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),False)
    if cadCompartides=='':
        compartidesVisible='hidden'
    horesCPIVisible = "none"
    if (nom in ded.getPDIambCPI()):
        horesCPIVisible = "table-cell"
    templateV = {"nom" : nom,
                 "data": avui(),
                 "totalHores":ded.getHoresAltresCentres(nom),
                 "detallDocencia": fillDetallDoc(nom, ded.getAssCursSem(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA()),
                 "docenciaParticipants1": fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),True),
                 "docenciaParticipants2": fillDocPart(nom,ded.getAssProf(),ded.getDetallDocencia(),ded.getDetallPDIPracGEA(),ded.getDetallAssPracGEA(),False),                 
                 "propiesVisible":propiesVisible,
                 "compartidesVisible":compartidesVisible,
                 "horesCPIVisible":horesCPIVisible
                 }
    return templateV

def fillDetallGestio(pdi,d):
    cad=''
    if pdi in d:
        for e in d[pdi]:
            cad=cad+"<tr><td>"+e[0]+"</td><td>"+e[1]+"</td></tr>"
    return cad

def genFile(filename,temp,templateVars,config):
    env = Environment(loader=FileSystemLoader('templates'), autoescape=False)
    template = env.get_template(temp)
    html_out = template.render(templateVars)
    pdfkit.from_string(html_out, filename,configuration=config)

def gen1F(pdi,ded,config):
    tempV=fillTemplateFix(pdi,ded) 
    genFile("output/plantilla/"+pdi+"-"+avui()+".pdf","template1Fix.html",tempV,config)

def gen1FDept(pdi,ded,config,dept):
    dir="_ENG"
    if "BIO" in dept:
       dir="_BIO" 
    tempV=fillTemplateFix(pdi,ded) 
    genFile("output/plantilla"+dir+"/"+pdi+"-"+avui()+".pdf","template1Fix.html",tempV,config)

def genAllFix(ded,config):
    for pdi in ded.getPDIFix():
        gen1F(pdi,ded,config)

def genAllFixDept(ded,config,dept):
    for pdi in ded.getPDIFix():
        if dept in ded.getDept(pdi):
            gen1FDept(pdi,ded,config,dept)
        

def gen1A(pdi,ded,config):
    tempV=fillTemplateAss(pdi,ded)
    genFile("output/associats/"+pdi+"-"+avui()+".pdf","template1Ass.html",tempV,config)

def gen1ADept(pdi,ded,config,dept):
    dir="_ENG"
    if "BIO" in dept:
       dir="_BIO"
    tempV=fillTemplateAss(pdi,ded)
    genFile("output/associats"+dir+"/"+pdi+"-"+avui()+".pdf","template1Ass.html",tempV,config)

def genAllAss(ded,config):
    d=ded.getPDIAss()
    for pdi in d:
        if d[pdi]['observacions']!='Altre centre':
            print(pdi)
            gen1A(pdi,ded,config)
            print("done",pdi)

def genAllAssDept(ded,config,dept):
    d=ded.getPDIAss()
    for pdi in d:
        if dept in ded.getDept(pdi):
        #if d[pdi]['observacions']!='Altre centre':
            gen1ADept(pdi,ded,config,dept)

def genAllAltresCentres(ded,config):
    d=ded.getPDIAss()
    for pdi in d:
         if d[pdi]['observacions']=='Altre centre':
             gen1AltresCentres(pdi,ded,config)

def gen1AltresCentres(pdi,ded,config):
    tempV=fillTemplateAltresCentres(pdi,ded)
    genFile("output/altresCentres/"+pdi+"-"+avui()+".pdf","template1AltresCentres.html",tempV,config)



def getOption():
    print("1. Generar PDI FCTE")
    print("2. Generar PDI FCTE per departaments")
    print("3. Generar PDI Plantilla Enginyeries")
    print("4. Generar PDI Associats Enginyeries")
    print("5. Generar PDI Plantilla Biociències")
    print("6. Generar PDI Associats Biociències")
    print("7. Generar PDI Altres Centres")
    print("8. Generar 1 document")
    print("9. Sortir")
    opc=input("Opció: ")
    return opc

def genDirs(base="output"):
    dirs = [
        "plantilla_ENG",
        "plantilla_BIO",
        "associats_ENG",
        "associats_BIO",
        "altresCentres"
    ]

    if not os.path.exists(base):
        os.makedirs(base)

    for d in dirs:
        path = os.path.join(base, d)
        if not os.path.exists(path):
            os.makedirs(path)

if __name__=="__main__":
    
        
    path_wkthmltopdf = r'/usr/bin/wkhtmltopdf'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    deds=Dedicacions('FCTE 26_27.xlsx')
    genDirs()
    opc=getOption()
    while opc!="9":
        if opc=="1":
            genAllFix(deds,config)
            genAllAss(deds,config)
        elif opc=="2":
            genAllFixDept(deds,config,"ENGINYERIES")
            genAllFixDept(deds,config,"BIOCIÈNCIES")
            genAllAssDept(deds,config,"ENGINYERIES")
            genAllAssDept(deds,config,"BIOCIÈNCIES")
        elif opc=="3":
            genAllFixDept(deds,config,"ENGINYERIES")
        elif opc=="4":
            genAllAssDept(deds,config,"ENGINYERIES")
        elif opc=="5":
            genAllFixDept(deds,config,"BIOCIÈNCIES")
        elif opc=="6":
            genAllAssDept(deds,config,"BIOCIÈNCIES")
        elif opc=="7":
            genAllAltresCentres(deds,config)
        elif opc=="8":
            nom=input("Nom:").upper()
            dF=deds.getPDIFix()
            dA=deds.getPDIAss()
            if nom in dF:
                gen1FDept(nom,deds,config,deds.getDept(nom))
            elif nom in dA:
                if dA[nom]['observacions']!='Altre centre':
                    gen1ADept(nom,deds,config,deds.getDept(nom))
                else:
                    gen1AltresCentres(nom,deds,config)
        opc=getOption()



