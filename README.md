# Crawler para Documentação Pública com Azure Functions

## 📌 Descrição
Este projeto consiste em uma **Azure Function em Python** que atua como um **crawler** para coletar documentação pública de um sistema. Os documentos coletados são armazenados localmente no formato `.html` e organizados por data e hora da coleta.

## 🎯 Objetivo
- Desenvolver um **crawler** para capturar documentos públicos de um sistema.
- Suportar **dois modos de operação**:
  - **Carga Full**: Captura todos os documentos disponíveis.
  - **Carga Incremental**: Captura apenas documentos novos ou atualizados.
- Armazenar os arquivos localmente antes de adaptar para o **Azure Storage Account**.
- Permitir execução automática via **timer trigger** e manual via **HTTP trigger**.

## 🛠️ Tecnologias Utilizadas
- **Python**
- **Azure Functions**
- **Azure Functions Core Tools** (para execução local)
- **Git** (para versionamento)

## 🚀 Como Executar o Projeto Localmente
### 1️⃣ Pré-requisitos
- Python instalado
- Azure Functions Core Tools configurado
- Conta no GitHub para versionamento

### 2️⃣ Instalar Dependências
```sh
python3 -m venv venv
```

```sh
source venv/bin/activate
```

```sh
pip install -r requirements.txt
```

### 3️⃣ Executar a Azure Function Localmente
```sh
func start
```

## 🔄 Modos de Execução
### **Carga Full**
Coleta todos os documentos disponíveis.

### **Carga Incremental**
Coleta apenas documentos novos ou atualizados desde a última execução.

## 📌 Próximos Passos
- [ ] Integrar o armazenamento com **Azure Storage Account**
- [ ] Implementar o **timer trigger**
- [ ] Implementar o **HTTP trigger**
- [ ] Deploy na Azure

## 📝 Observações
- O projeto está em desenvolvimento e futuras melhorias serão adicionadas.

---