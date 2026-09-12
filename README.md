# 📱 FocAÊ - App Mobile & Plataforma Educacional Consciente (Hackathon Bemobi)

> **Aplicativo escolar mobile voltado ao uso saudável de smartphones, unindo tecnologia, metodologias ativas, foco sem distrações e gamificação ética.**

---

## 🌟 Pilares do FocAÊ

- **Nome Oficial**: **FocAÊ** (Foco Consciente na Escola).
- **Mobile-First**: Interface desenvolvida no formato nativo de aplicativo de smartphone com navegação inferior (*Bottom Navigation Bar*).
- **Diferenciação Rígida de Papéis**:
  - **👨‍🏫 Professor (Prof. Ricardo)**: Acesso exclusivo à criação de atividades, concessão de bônus de presença consciente, visualização de todas as entregas em PDF e relatório agregado da turma.
  - **👩‍🎓 Estudantes (Evelyn, Thiago, Marley)**: As ferramentas docentes ficam **completamente ocultas**. Os estudantes visualizam apenas suas atividades, entregam seus PDFs, cumprem desafios fotográficos do mundo real e ativam o Modo Foco.
- **🔕 Bloqueador de Notificações (Modo Foco Ativo)**:
  - Botão interativo para silenciar alertas de redes sociais durante as aulas, mantendo contador em tempo real (*"14 notificações silenciadas"*).
- **📈 Relatório Semanal do Uso do Celular**:
  - Gráficos diários com a proporção de tempo de tela pedagógico (Kahoot, Gartic, PDFs) vs tempo em redes sociais, com insights semanais.
- **💡 Pílulas de Curiosidades de Conhecimentos Gerais**:
  - Notificações de curiosidades rápidas ("Você sabia?") no topo do app sobre biologia, física, astronomia e história.

---

## 👥 Atores Iniciais Cadastrados (Mock Inicial)

| Aluno | Turma | Pontos Iniciais | Ofensiva | Presença | Tempo Offline |
|---|---|---|---|---|---|
| **Evelyn** | Turma A (1º Médio) | 60 pts | 4 dias | 18 dias | 60 min |
| **Thiago** | Turma A (1º Médio) | 45 pts | 3 dias | 16 dias | 45 min |
| **Marley** | Turma B (1º Médio) | 50 pts | 2 dias | 15 dias | 30 min |

---

## 🚀 Como Executar

### 1. Iniciar o Aplicativo Web Mobile
```powershell
python app.py --server
```
- **No seu PC / Navegador**: `http://127.0.0.1:5000`
- **No Celular (mesmo Wi-Fi)**: `http://192.168.1.108:5000`

### 2. Rodar a Suíte de Testes Automatizados (unittest)
```powershell
python test_mvp.py
```
*(8 testes cobrindo alunos, pontuação, tempo offline, fotos reais, bônus de presença, submissão em PDF, DND e relatório semanal).*

### 3. Modo Demonstração no Terminal
```powershell
python app.py --demo
```
