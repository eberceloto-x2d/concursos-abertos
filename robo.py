import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

print("Iniciando a frota atualizada de robôs coletores...\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

ano_atual = datetime.now().year 

def analisar_texto(texto, titulo):
    # --- SALÁRIO ---
    salario_texto = "Salário não informado"
    salario_numero = 0
    busca_salario = re.search(r'R\$\s*([\d\.,]+)', texto)
    if busca_salario:
        salario_texto = busca_salario.group(0)
        try:
            salario_numero = float(busca_salario.group(1).replace('.', '').replace(',', '.'))
        except:
            salario_numero = 0
            
    # --- ESTADO (UF) ---
    busca_uf = re.search(r'\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b', titulo + " " + texto)
    estado = busca_uf.group(1) if busca_uf else "Nacional/Outros"
    
    # --- DATA DE INSCRIÇÃO ---
    data_limite_iso = None 
    data_texto_bonito = None 
    
    datas_encontradas = re.findall(r'\b(\d{2}/\d{2}(?:/\d{2,4})?)\b', texto)
    if datas_encontradas:
        ultima_data = datas_encontradas[-1] 
        try:
            if len(ultima_data) == 5: 
                data_obj = datetime.strptime(f"{ultima_data}/{ano_atual}", "%d/%m/%Y")
            elif len(ultima_data) == 8: 
                data_obj = datetime.strptime(ultima_data, "%d/%m/%y")
            else: 
                data_obj = datetime.strptime(ultima_data, "%d/%m/%Y")
            
            data_limite_iso = data_obj.strftime("%Y-%m-%d")
            data_texto_bonito = data_obj.strftime("%d/%m/%Y")
        except:
            pass 
            
    return salario_texto, salario_numero, estado, data_limite_iso, data_texto_bonito

# --- ROBÔ 1: PCI Concursos ---
def raspar_pci():
    print("🤖 Robô 1: Vasculhando PCI Concursos...")
    vagas = []
    try:
        site = BeautifulSoup(requests.get('https://www.pciconcursos.com.br/concursos/', headers=headers).text, 'html.parser')
        for tag_a in site.find_all('a'):
            link = tag_a.get('href')
            titulo = tag_a.text.strip()
            if link and link.startswith('https://www.pciconcursos.com.br/noticias/') and titulo:
                texto = " ".join(tag_a.parent.text.strip().split())
                s_texto, s_num, uf, d_iso, d_texto = analisar_texto(texto, titulo)
                vagas.append({"titulo": "[PCI] " + titulo, "link": link, "resumo": texto, "salario_texto": s_texto, "salario_numero": s_num, "uf": uf, "data_limite": d_iso, "data_texto": d_texto})
    except Exception as e:
        print(f"Erro no PCI: {e}")
    return vagas

# --- ROBÔ 2: JC Concursos ---
def raspar_jc():
    print("🤖 Robô 2: Vasculhando JC Concursos...")
    vagas = []
    try:
        site = BeautifulSoup(requests.get('https://jcconcursos.com.br/concursos/inscricoes-abertas', headers=headers).text, 'html.parser')
        for tag_a in site.find_all('a'):
            link = tag_a.get('href')
            titulo = tag_a.text.strip()
            if link and '/noticia/' in link and titulo and len(titulo) > 15:
                link = link if link.startswith('http') else 'https://jcconcursos.com.br' + link
                texto = " ".join(tag_a.parent.parent.text.strip().split())
                s_texto, s_num, uf, d_iso, d_texto = analisar_texto(texto, titulo)
                vagas.append({"titulo": "[JC] " + titulo, "link": link, "resumo": texto[:200] + "...", "salario_texto": s_texto, "salario_numero": s_num, "uf": uf, "data_limite": d_iso, "data_texto": d_texto})
    except Exception as e:
        print(f"Erro no JC: {e}")
    return vagas

# --- ROBÔ 3: Centro Paula Souza (CPS) ---
def raspar_cps():
    print("🤖 Robô 3: Vasculhando CPS (SP)...")
    vagas = []
    try:
        site = BeautifulSoup(requests.get('https://www.cps.sp.gov.br/concursopublico/', headers=headers).text, 'html.parser')
        for tag_a in site.find_all('a'):
            link = tag_a.get('href')
            titulo = tag_a.text.strip()
            if link and ('edital' in titulo.lower() or 'concurso' in titulo.lower() or 'processo seletivo' in titulo.lower()):
                texto = " ".join(tag_a.parent.text.strip().split())
                s_texto, s_num, _, d_iso, d_texto = analisar_texto(texto, titulo)
                vagas.append({"titulo": "[CPS] " + titulo, "link": link if link.startswith('http') else 'https://www.cps.sp.gov.br' + link, "resumo": texto, "salario_texto": s_texto, "salario_numero": s_num, "uf": "SP", "data_limite": d_iso, "data_texto": d_texto})
    except Exception as e:
        print(f"Erro no CPS: {e}")
    return vagas

# --- ROBÔ 4: Ache Concursos ---
def raspar_ache():
    print("🤖 Robô 4: Vasculhando Ache Concursos...")
    vagas = []
    try:
        site = BeautifulSoup(requests.get('https://www.acheconcursos.com.br/', headers=headers).text, 'html.parser')
        for tag_a in site.find_all('a'):
            link = tag_a.get('href')
            titulo = tag_a.text.strip()
            if link and '/concurso/' in link and titulo and len(titulo) > 15:
                link = link if link.startswith('http') else 'https://www.acheconcursos.com.br' + link
                parent_text = tag_a.parent.text.strip() if tag_a.parent else ""
                texto = " ".join((titulo + " " + parent_text).split())
                s_texto, s_num, uf, d_iso, d_texto = analisar_texto(texto, titulo)
                vagas.append({"titulo": "[AcheConcursos] " + titulo, "link": link, "resumo": texto[:200], "salario_texto": s_texto, "salario_numero": s_num, "uf": uf, "data_limite": d_iso, "data_texto": d_texto})
    except Exception as e:
        print(f"Erro no Ache Concursos: {e}")
    return vagas

# --- ROBÔ 5: Cebraspe ---
def raspar_cebraspe():
    print("🤖 Robô 5: Vasculhando Cebraspe...")
    vagas = []
    try:
        site = BeautifulSoup(requests.get('https://www.cebraspe.org.br/concursos/inscricoes-abertas/', headers=headers).text, 'html.parser')
        for tag_a in site.find_all('a'):
            link = tag_a.get('href')
            titulo = tag_a.text.strip()
            if link and titulo and len(titulo) > 5:
                link = link if link.startswith('http') else 'https://www.cebraspe.org.br' + link
                parent_text = tag_a.parent.text.strip() if tag_a.parent else ""
                texto = " ".join((titulo + " " + parent_text).split())
                s_texto, s_num, uf, d_iso, d_texto = analisar_texto(texto, titulo)
                vagas.append({"titulo": "[Cebraspe] " + titulo, "link": link, "resumo": texto, "salario_texto": s_texto, "salario_numero": s_num, "uf": uf, "data_limite": d_iso, "data_texto": d_texto})
    except Exception as e:
        print(f"Erro no Cebraspe: {e}")
    return vagas

# --- O COMANDANTE ---
todas_as_vagas = []
links_salvos = set()

lista_de_funcoes = [raspar_pci, raspar_jc, raspar_cps, raspar_ache, raspar_cebraspe]

for funcao in lista_de_funcoes:
    resultado_robo = funcao()
    for vaga in resultado_robo:
        if vaga['link'] not in links_salvos:
            todas_as_vagas.append(vaga)
            links_salvos.add(vaga['link'])

with open('vagas.json', 'w', encoding='utf-8') as arquivo:
    json.dump(todas_as_vagas, arquivo, ensure_ascii=False, indent=4)

print(f"\n🎉 SUCESSO! Total de {len(todas_as_vagas)} vagas únicas unificadas de 5 portais diferentes!")