import streamlit as st
import random
import time
import copy # Embora não usado ativamente, bom ter para futuras cópias profundas se necessário

# --- Configuração da Página ---
st.set_page_config(
    page_title="Matchmaking Pro Demo", # Nome Atualizado
    page_icon="✨",                   # Ícone Atualizado
    layout="centered",                # Layout centralizado padrão
    initial_sidebar_state="expanded"  # Sidebar aberta por padrão
)

# --- Simulação de Banco de Dados e Estado da Sessão ---
# Inicializar o estado da sessão se não existir para evitar erros no primeiro acesso
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users_db' not in st.session_state:
    # Banco de dados FAKE de usuários (com perfis desenhados para gerar matches na demo)
    st.session_state.users_db = {
        "user1": {"name": "Alice Braga", "headline": "CEO @ InovaTech", "photo": "https://via.placeholder.com/150/FFA07A/808080?text=Alice", "interests": ["IA", "Fintech", "Liderança", "SaaS"], "seeking": ["Investimento Seed", "Parcerias Estratégicas"], "offering": ["Mentoria em Gestão", "Experiência em SaaS"]},
        "user2": {"name": "Bruno Costa", "headline": "Desenvolvedor Full Stack @ DevSolutions", "photo": "https://via.placeholder.com/150/ADD8E6/808080?text=Bruno", "interests": ["Python", "Web Dev", "Cloud", "IA"], "seeking": ["Oportunidades de Freelance", "Networking Técnico"], "offering": ["Desenvolvimento Web", "Consultoria AWS"]},
        "user3": {"name": "Carla Dias", "headline": "Marketing Digital Specialist @ Connecta", "photo": "https://via.placeholder.com/150/90EE90/808080?text=Carla", "interests": ["SEO", "Mídias Sociais", "Growth Hacking"], "seeking": ["Clientes para Agência", "Ferramentas de Automação", "Parcerias Estratégicas"], "offering": ["Estratégias de Marketing", "Gestão de Campanhas"]},
        "user4": {"name": "Daniel Alves", "headline": "Investidor Anjo @ Future Ventures", "photo": "https://via.placeholder.com/150/FFFFE0/808080?text=Daniel", "interests": ["Startups", "Investimento", "Tecnologia", "Fintech"], "seeking": ["Startups Promissoras (Early Stage)", "Co-investidores"], "offering": ["Capital Semente", "Aconselhamento Estratégico", "Mentoria em Gestão"]},
        "user5": {"name": "Elisa Ferreira", "headline": "Product Manager @ Projeta", "photo": "https://via.placeholder.com/150/FFB6C1/808080?text=Elisa", "interests": ["UX/UI", "Metodologias Ágeis", "SaaS", "Liderança"], "seeking": ["Feedback de Usuários", "Desenvolvedores Talentosos", "Mentoria em Gestão"], "offering": ["Gestão de Produto", "Workshops de Design Thinking", "Experiência em SaaS"]},
        "user6": {"name": "Fernando Lima", "headline": "Vendedor @ VendeMais Corp", "photo": "https://via.placeholder.com/150/DDA0DD/808080?text=Fernando", "interests": ["Vendas B2B", "CRM", "Negociação", "SaaS"], "seeking": ["Leads Qualificados", "Parcerias de Vendas", "Clientes para Agência"], "offering": ["Soluções de Software CRM", "Treinamento de Vendas"]},
        "user7": {"name": "Gustavo Pinto", "headline": "Vendedor @ SalesForce One", "photo": "https://via.placeholder.com/150/E6E6FA/808080?text=Gustavo", "interests": ["Vendas", "Cloud Computing", "Enterprise", "Fintech"], "seeking": ["Grandes Contas", "Fechar negócios", "Investimento Seed"], "offering": ["Plataforma de Vendas Líder", "Consultoria AWS"]},
    }
if 'interactions' not in st.session_state:
    # Estrutura: {user_id: {"liked": {target_id1,...}, "skipped": {target_id2,...}}}
    st.session_state.interactions = {}
if 'matches' not in st.session_state:
    # Estrutura: {user_id: {frozenset({user1, user2}), frozenset({user1, user3}), ...}}
    # Usar frozenset garante que a ordem não importa e é hasheável (bom para chaves de dict/sets)
    st.session_state.matches = {}
if 'messages' not in st.session_state:
    # Estrutura: {frozenset({user1, user2}): [{"sender": user_id/system, "text": "...", "time": timestamp}, ...]}
    # A chave é o frozenset do match
    st.session_state.messages = {}
if 'current_suggestion_index' not in st.session_state:
    # Índice do usuário atual na lista de sugestões
    st.session_state.current_suggestion_index = 0
if 'suggestion_pool' not in st.session_state:
    # Lista ordenada (embaralhada) de user_ids sugeridos para o usuário atual
    st.session_state.suggestion_pool = []
if 'selected_page' not in st.session_state:
     # Página padrão a ser exibida após o login ou ao recarregar
     st.session_state.selected_page = "Matchmaking"


# --- Funções de Lógica e Simulação ---

def simulate_linkedin_login(username):
    """Simula o login, define o usuário atual e prepara as sugestões."""
    if username in st.session_state.users_db:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        # Inicializa estruturas de dados para o usuário se for o primeiro login neste "run"
        if username not in st.session_state.interactions:
            st.session_state.interactions[username] = {"liked": set(), "skipped": set()}
        if username not in st.session_state.matches:
            st.session_state.matches[username] = set()
        # Preenche o pool de sugestões imediatamente para a demo
        populate_suggestion_pool()
        st.session_state.current_suggestion_index = 0 # Começa do início da lista de sugestões
        st.session_state.selected_page = "Matchmaking" # Garante que vá para a tela principal da demo
        st.rerun() # Recarrega a página para refletir o estado logado
    else:
        st.error("Usuário inválido selecionado para demonstração.")

def simulate_logout():
    """Simula o logout, limpando o estado da sessão relevante do usuário."""
    # Mantém o DB de usuários, interações, matches e mensagens para preservar o estado geral da demo
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.current_suggestion_index = 0
    st.session_state.suggestion_pool = []
    # Limpa estados de UI específicos do usuário
    if 'selected_page' in st.session_state:
         del st.session_state['selected_page']
    if 'selected_chat_partner' in st.session_state:
        del st.session_state['selected_chat_partner']
    st.rerun() # Recarrega para mostrar a tela de login

def update_profile(user_id, interests, seeking, offering):
    """Simula a atualização do perfil do usuário no 'banco de dados'."""
    if user_id in st.session_state.users_db:
        st.session_state.users_db[user_id]['interests'] = interests
        st.session_state.users_db[user_id]['seeking'] = seeking
        st.session_state.users_db[user_id]['offering'] = offering
        st.success("Perfil atualizado com sucesso!")
        # Repopular sugestões é crucial, pois o perfil afeta o matching
        populate_suggestion_pool()
        st.session_state.current_suggestion_index = 0 # Resetar o índice para ver novas sugestões com base no perfil atualizado
        time.sleep(1.5) # Pausa para o usuário ler a mensagem de sucesso
        st.rerun() # Atualiza a interface (pode ir para outra página ou ficar no perfil)
    else:
        st.error("Erro ao atualizar perfil. Usuário não encontrado.")

def populate_suggestion_pool():
    """Preenche e embaralha a lista de usuários a serem sugeridos."""
    current_user_id = st.session_state.current_user
    if not current_user_id: # Não faz nada se não houver usuário logado
        st.session_state.suggestion_pool = []
        return

    all_users = list(st.session_state.users_db.keys())
    # Garante que a estrutura de interações exista
    if current_user_id not in st.session_state.interactions:
        st.session_state.interactions[current_user_id] = {"liked": set(), "skipped": set()}

    # Flag para indicar se um match ocorreu nesta interação específica
    match_occurred_in_this_call = False



    # Usuários com quem o usuário atual JÁ interagiu (like ou skip)
    interacted_users = st.session_state.interactions[current_user_id]["liked"].union(
        st.session_state.interactions[current_user_id]["skipped"]
    )
    # Adiciona também os parceiros de matches já existentes (para garantir que não sejam sugeridos novamente)
    if current_user_id in st.session_state.matches:
        matched_partners = {get_match_partner(match_id, current_user_id) for match_id in st.session_state.matches[current_user_id]}
        interacted_users.update(matched_partners)

    profile1 = st.session_state.users_db[current_user_id]
    # Regra específica da demo: Vendedores não veem outros vendedores como sugestão
    is_current_user_seller = "Vendedor" in profile1.get("headline", "")

    potential_pool = []
    for user_id in all_users:
        # --- Filtros Iniciais ---
        # 1. Não sugerir a si mesmo
        if user_id == current_user_id:
            continue
        # 2. Não sugerir quem já foi interagido (like/skip) ou já é match
        if user_id in interacted_users:
            continue

        profile2 = st.session_state.users_db[user_id]
        is_target_user_seller = "Vendedor" in profile2.get("headline", "")
        # 3. Regra demo: Não sugerir Vendedor para Vendedor
        if is_current_user_seller and is_target_user_seller:
            continue

        # --- Lógica de Matchmaking Simplificada (Verifica Conexão) ---
        # Usa .get com default de lista vazia para segurança
        common_interests = set(profile1.get('interests', [])) & set(profile2.get('interests', []))
        complementary_seek_offer = set(profile1.get('seeking', [])) & set(profile2.get('offering', []))
        complementary_offer_seek = set(profile1.get('offering', [])) & set(profile2.get('seeking', []))

        # 4. Apenas sugere se houver PELO MENOS UM ponto de conexão (interesse, busca/oferta)
        if common_interests or complementary_seek_offer or complementary_offer_seek:
             potential_pool.append(user_id)

    random.shuffle(potential_pool) # Embaralha a lista de sugestões válidas
    st.session_state.suggestion_pool = potential_pool
    # Não reseta o índice aqui; isso é feito no login ou atualização de perfil

def get_next_suggestion():
    """Retorna o ID do próximo usuário na lista de sugestões, ou None se a lista acabou."""
    pool = st.session_state.suggestion_pool
    index = st.session_state.current_suggestion_index
    if index < len(pool):
        return pool[index]
    return None # Fim da lista

def record_interaction(target_id, action):
    """Registra um 'like' ou 'skip', verifica se houve match mútuo e avança para a próxima sugestão."""
    current_user_id = st.session_state.current_user
    if not current_user_id: return # Segurança: não fazer nada se não houver usuário

    target_name = st.session_state.users_db[target_id]['name']

    # Garante que a estrutura de interações existe
    if current_user_id not in st.session_state.interactions:
         st.session_state.interactions[current_user_id] = {"liked": set(), "skipped": set()}

    if action == "like":
        st.session_state.interactions[current_user_id]["liked"].add(target_id)
        st.toast(f"✅ Interesse registrado em {target_name}!", icon="👍")

        # --- Verificação de Match Mútuo ---
        # Verifica se o target_id já deu like no current_user_id
        target_interactions = st.session_state.interactions.get(target_id, {})
        if current_user_id in target_interactions.get("liked", set()):
            # É um MATCH!
            confirm_match(current_user_id, target_id)
            st.balloons() # Efeito visual de celebração

            # ---> INÍCIO DA ALTERAÇÃO <---
            # Sinaliza que devemos navegar para 'Meus Matches' no próximo rerun
            st.session_state.navigate_to_matches = True
            match_occurred = True # Marca que um match ocorreu
            # ---> FIM DA ALTERAÇÃO <---


            # Mensagem mais explícita pode ser mostrada na tela de Matches ou Chat
    elif action == "skip":
        st.session_state.interactions[current_user_id]["skipped"].add(target_id)
        st.toast(f"❌ Perfil de {target_name} pulado.", icon="⏭️")

    # Avança o índice para a próxima sugestão na lista
    st.session_state.current_suggestion_index += 1
    # A atualização da UI (rerun) será feita pelo botão que chamou esta função

def confirm_match(user1_id, user2_id):
    """Registra um match confirmado para ambos os usuários e gera a pauta inicial se for a primeira vez."""
    # Usa frozenset para chave única e independente da ordem (ideal para dict keys e sets)
    match_id = frozenset((user1_id, user2_id))

    # Garante que as entradas no dicionário 'matches' existam para ambos os usuários
    if user1_id not in st.session_state.matches: st.session_state.matches[user1_id] = set()
    if user2_id not in st.session_state.matches: st.session_state.matches[user2_id] = set()

    # Adiciona o match_id ao conjunto de matches de cada usuário APENAS SE AINDA NÃO EXISTIR
    new_match_created = False
    if match_id not in st.session_state.matches[user1_id]:
        st.session_state.matches[user1_id].add(match_id)
        st.session_state.matches[user2_id].add(match_id)
        new_match_created = True

    # Gera a pauta (tópicos de conversa) apenas na primeira vez que o match é criado
    # Evita adicionar a pauta novamente se a função for chamada acidentalmente de novo
    if new_match_created and match_id not in st.session_state.messages:
        st.session_state.messages[match_id] = generate_agenda_topics(user1_id, user2_id)

def generate_agenda_topics(user1_id, user2_id):
    """Simula a geração (ex: por IA) de tópicos de conversa iniciais com base nos perfis."""
    profile1 = st.session_state.users_db[user1_id]
    profile2 = st.session_state.users_db[user2_id]
    # Usar .get com default para evitar erros se os campos não existirem nos perfis
    common_interests = list(set(profile1.get('interests', [])) & set(profile2.get('interests', [])))
    complementary_seek_offer = list(set(profile1.get('seeking', [])) & set(profile2.get('offering', [])))
    complementary_offer_seek = list(set(profile1.get('offering', [])) & set(profile2.get('seeking', [])))

    # Monta a lista de mensagens iniciais do sistema
    agenda = [{"sender": "system", "text": "🤖 *Olá! Percebi que vocês se conectaram. Que tal começar a conversa por aqui?*", "time": time.time()}]
    if common_interests:
        agenda.append({"sender": "system", "text": f"🎯 **Interesses em Comum:** {', '.join(common_interests)}", "time": time.time() + 0.1}) # Pequeno delay para ordem
    if complementary_seek_offer:
        agenda.append({"sender": "system", "text": f"🔗 **Conexão Busca/Oferta:** {profile1['name']} busca *'{', '.join(complementary_seek_offer)}'* que {profile2['name']} oferece.", "time": time.time() + 0.2})
    if complementary_offer_seek:
         agenda.append({"sender": "system", "text": f"🔗 **Conexão Oferta/Busca:** {profile1['name']} oferece *'{', '.join(complementary_offer_seek)}'* que {profile2['name']} busca.", "time": time.time() + 0.3})
    # Mensagem genérica se não houver pontos óbvios de conexão
    if not common_interests and not complementary_seek_offer and not complementary_offer_seek:
        agenda.append({"sender": "system", "text": "💡 *Não encontrei pontos específicos nos perfis, mas explorar os objetivos de cada um no evento é sempre um bom começo!*", "time": time.time() + 0.4})

    return agenda # Retorna a lista de dicionários de mensagens

def send_message(match_id, sender_id, text):
    """Adiciona uma nova mensagem enviada por um usuário ao histórico do chat correspondente."""
    if match_id not in st.session_state.messages:
        # Segurança: cria a lista se ela não existir (embora devesse ter sido criada em confirm_match)
        st.session_state.messages[match_id] = []
    st.session_state.messages[match_id].append({
        "sender": sender_id,
        "text": text,
        "time": time.time() # Registra o timestamp do envio
    })
    st.toast("Mensagem enviada!", icon="✉️")
    # A atualização da UI (rerun) é feita pelo st.form que chama esta função

def get_match_partner(match_id, current_user_id):
    """Dado um match_id (frozenset de 2 usuários) e o ID do usuário atual, retorna o ID do *outro* usuário."""
    # Converte o frozenset para lista para acesso por índice
    users = list(match_id)
    # Retorna o ID que NÃO é o do usuário atual
    return users[0] if users[1] == current_user_id else users[1]

# --- Função Auxiliar para UI ---
def calculate_match_reasons(user1_id, user2_id):
    """Calcula e formata as razões (pontos de conexão) para sugerir um match. Usado na UI."""
    reasons = []
    profile1 = st.session_state.users_db[user1_id]
    profile2 = st.session_state.users_db[user2_id]

    # Usa .get com default para segurança
    common_interests = list(set(profile1.get('interests', [])) & set(profile2.get('interests', [])))
    complementary_seek_offer = list(set(profile1.get('seeking', [])) & set(profile2.get('offering', [])))
    complementary_offer_seek = list(set(profile1.get('offering', [])) & set(profile2.get('seeking', [])))

    # Formata as razões encontradas para exibição
    if common_interests:
        reasons.append(f"🎯 **Interesses em Comum:** {', '.join(common_interests)}")
    if complementary_seek_offer:
        # Mostra a perspectiva do usuário atual (user1_id)
        reasons.append(f"🔗 **Você busca / {profile2['name']} oferece:** {', '.join(complementary_seek_offer)}")
    if complementary_offer_seek:
        # Mostra a perspectiva do usuário atual (user1_id)
        reasons.append(f"🔗 **Você oferece / {profile2['name']} busca:** {', '.join(complementary_offer_seek)}")

    # Se nenhuma razão específica foi encontrada, adiciona uma genérica
    if not reasons:
         reasons.append("✅ Potencial conexão geral para networking no evento!")

    return reasons # Retorna lista de strings formatadas

# --- Função de Métricas (para Dashboard) ---
def simulate_get_metrics():
    """Calcula e retorna métricas básicas de engajamento da plataforma (simulado)."""
    total_users = len(st.session_state.users_db)
    total_matches_set = set() # Usa um set para garantir contagem única de matches (frozensets)
    total_likes = 0
    total_skips = 0
    total_user_messages = 0 # Conta apenas mensagens de usuários, não do sistema

    # Soma interações de todos os usuários
    for user_interactions in st.session_state.interactions.values():
        total_likes += len(user_interactions.get('liked', set()))
        total_skips += len(user_interactions.get('skipped', set()))

    # Agrega todos os match_ids únicos
    for user_matches in st.session_state.matches.values():
        total_matches_set.update(user_matches)

    # Soma mensagens de usuários em todos os chats
    for chat_messages in st.session_state.messages.values():
        total_user_messages += sum(1 for msg in chat_messages if msg['sender'] != 'system')

    # Cálculos das métricas
    total_confirmed_matches = len(total_matches_set)
    interactions_total = total_likes + total_skips
    like_rate = (total_likes / interactions_total * 100) if interactions_total > 0 else 0
    avg_msg_per_match = (total_user_messages / total_confirmed_matches) if total_confirmed_matches > 0 else 0

    return {
        "total_users": total_users,
        "total_matches": total_confirmed_matches,
        "total_interactions": interactions_total,
        "like_rate_percent": like_rate,
        "avg_messages_per_match": avg_msg_per_match,
        "total_messages_sent": total_user_messages # Renomeado para clareza
    }

# =============================================================================
# --- Interface Streamlit ---
# =============================================================================

# --- Barra Lateral (Login e Navegação) ---
st.sidebar.title("✨ Matchmaking Pro")
st.sidebar.divider()

# --- Bloco de Login (Se não estiver logado) ---
if not st.session_state.logged_in:
    st.sidebar.header("Login (Simulado)")
    # Opções de login baseadas nos usuários do DB simulado
    login_options = list(st.session_state.users_db.keys())
    login_user = st.sidebar.selectbox(
        "Selecione o usuário para logar:",
        options=login_options,
        index=None, # Nenhum selecionado por padrão
        format_func=lambda key: f"{st.session_state.users_db[key]['name']} ({key})", # Mostra nome e ID
        placeholder="Escolha um perfil para simular..."
    )
    if st.sidebar.button("Entrar (Simulado)", type="primary", use_container_width=True):
        if login_user:
            simulate_linkedin_login(login_user)
        else:
            st.sidebar.warning("⚠️ Por favor, selecione um usuário.")
    st.sidebar.info("Use os perfis acima para simular diferentes participantes e ver os matches sugeridos.")
    st.sidebar.divider()
    st.sidebar.caption("Demonstração por [Seu Nome/Empresa]") # Adicione seu crédito aqui

# --- Bloco de Navegação (Se estiver logado) ---
else:
    # Exibe informações do usuário logado
    user_info = st.session_state.users_db[st.session_state.current_user]
    st.sidebar.image(user_info['photo'], width=80, caption=f"{user_info['name']}") # Foto menor na sidebar
    st.sidebar.caption(f"_{user_info['headline']}_")
    st.sidebar.divider()

    # Menu de Navegação Principal
    pages = ["Matchmaking", "Meus Matches", "Chat", "Meu Perfil", "Dashboard Organizador"]
    # Tenta manter a página selecionada; default para Matchmaking
    try:
        current_page_index = pages.index(st.session_state.get('selected_page', 'Matchmaking'))
    except ValueError:
        current_page_index = 0 # Default para Matchmaking se a página salva não for válida
    selected_page = st.sidebar.radio(
        "Navegação Principal",
        pages,
        index=current_page_index,
        key='selected_page_radio' # Chave para manter o estado do radio button
        )
    st.session_state.selected_page = selected_page # Salva a seleção atual no estado

    st.sidebar.divider()
    # Botão de Logout
    if st.sidebar.button("Logout", use_container_width=True):
        simulate_logout()

    # ==============================================================
    # --- Conteúdo Principal da Página (Depende da Seleção) ---
    # ==============================================================

    # --- PÁGINA DE MATCHMAKING ---
    if selected_page == "Matchmaking":
        st.header("✨ Encontre Conexões Relevantes")
        st.markdown("Analise os perfis sugeridos abaixo, baseados em seus interesses e objetivos. Decida se deseja conectar!")
        st.write("") # Espaçamento

        target_user_id = get_next_suggestion()

        if target_user_id:
            target_info = st.session_state.users_db[target_user_id]
            current_user_id = st.session_state.current_user

            # --- Card de Sugestão Visualmente Aprimorado ---
            with st.container(border=True): # Cria um container com borda (efeito de card)
                col_img, col_info = st.columns([1, 3]) # Coluna da imagem mais estreita

                with col_img:
                    st.image(target_info['photo'], use_container_width=True) # Imagem preenche a coluna

                with col_info:
                    st.subheader(target_info['name'])
                    st.caption(f"_{target_info['headline']}_") # Headline como legenda

                st.divider() # Linha separadora dentro do card

                # --- Razões para o Match (Informação Chave Visível) ---
                match_reasons = calculate_match_reasons(current_user_id, target_user_id)
                if match_reasons:
                    st.markdown("**🤝 Por que conectar?**") # Título destacado
                    for reason in match_reasons:
                        st.markdown(f"- {reason}") # Exibe cada razão como item de lista
                    st.write("") # Espaço antes do expander

                # --- Detalhes Adicionais (Ocultos por padrão para não sobrecarregar) ---
                with st.expander("Ver perfil completo..."):
                    if target_info.get('interests'):
                        st.markdown("**Interesses:**")
                        st.write(", ".join(target_info['interests'])) # Formato simples
                    if target_info.get('seeking'):
                        st.markdown("**Buscando:**")
                        for item in target_info['seeking']: # Formato de lista para clareza
                            st.write(f"- {item}")
                    if target_info.get('offering'):
                        st.markdown("**Oferecendo:**")
                        for item in target_info['offering']: # Formato de lista para clareza
                             st.write(f"- {item}")

            # --- Botões de Ação (Layout com espaçamento) ---
            st.write("") # Espaço antes dos botões
            col_skip, col_spacer, col_like = st.columns([2, 1, 2]) # Colunas: Pular | Espaço | Conectar

            with col_skip:
                if st.button("❌ Pular", key=f"skip_{target_user_id}", use_container_width=True):
                    record_interaction(target_user_id, "skip")
                    # ---> INÍCIO DA ALTERAÇÃO (Botão Pular) <---
                    # Limpa o flag de navegação por segurança, caso exista (não deveria para skip)
                    if st.session_state.get('navigate_to_matches', False):
                         del st.session_state.navigate_to_matches
                    # ---> FIM DA ALTERAÇÃO (Botão Pular) <---


                    st.rerun() # Recarrega para mostrar a próxima sugestão

            # col_spacer permanece vazia para criar o espaçamento visual

            with col_like:
                # Botão primário para destacar a ação principal
                if st.button("🤝 Conectar", key=f"like_{target_user_id}", type="primary", use_container_width=True):
                    record_interaction(target_user_id, "like")


                    # ---> INÍCIO DA ALTERAÇÃO (Botão Conectar) <---
                    # Verifica se o flag para navegar foi ativado DENTRO de record_interaction
                    if st.session_state.get('navigate_to_matches', False):
                        st.session_state.selected_page = "Meus Matches" # Muda a página alvo para 'Meus Matches'
                        del st.session_state.navigate_to_matches # Limpa o flag após usá-lo
                    # ---> FIM DA ALTERAÇÃO (Botão Conectar) <---




                    st.rerun() # Recarrega (pode mostrar match ou próxima sugestão)

        else:
            # Mensagem exibida quando não há mais sugestões na lista atual
            st.info("🎉 Você já viu todas as sugestões disponíveis no momento!")
            st.markdown("Verifique seus **Meus Matches** ou atualize seu **Meu Perfil** para refinar futuras sugestões.")
            if st.button("🔄 Verificar Novas Sugestões"):
                st.session_state.current_suggestion_index = 0 # Reinicia o índice para rever a lista (se repopulada)
                populate_suggestion_pool() # Tenta repopular (pode não haver novos usuários)
                st.rerun()

    # --- PÁGINA MEU PERFIL ---
    elif selected_page == "Meu Perfil":
        st.header("👤 Meu Perfil de Networking")
        st.markdown("Edite seus **interesses**, o que você **busca** e o que **oferece** no evento. Perfis completos geram melhores conexões!")
        st.divider()

        profile_data = st.session_state.users_db[st.session_state.current_user]

        with st.form("profile_form"):
            # Preenche os campos com os dados atuais do usuário
            current_interests = ", ".join(profile_data.get('interests', []))
            current_seeking = ", ".join(profile_data.get('seeking', []))
            current_offering = ", ".join(profile_data.get('offering', []))

            # Text Areas para edição com placeholders e dicas
            interests_text = st.text_area(
                "Meus Interesses Profissionais (separados por vírgula)",
                value=current_interests,
                placeholder="Ex: Inteligência Artificial, Fintech, Liderança Executiva, SaaS B2B...",
                help="Tópicos chave que você deseja discutir ou aprender."
            )
            seeking_text = st.text_area(
                "Estou Buscando (separados por vírgula)",
                value=current_seeking,
                placeholder="Ex: Investimento Série A, Parcerias de Distribuição, Clientes Enterprise, Talentos de UX...",
                help="Seus principais objetivos ao conectar com outros participantes."
            )
            offering_text = st.text_area(
                "Posso Oferecer (separados por vírgula)",
                value=current_offering,
                placeholder="Ex: Mentoria para Startups, Experiência em Cloud Escalável, Consultoria de Marketing Digital, Acesso a Rede de Contatos...",
                help="Suas habilidades, conhecimentos, serviços ou recursos que podem ser úteis para outros."
            )

            # Botão de submit do formulário
            submitted = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
            if submitted:
                # Processa os inputs: separa por vírgula, remove espaços extras e itens vazios
                interests_list = [i.strip() for i in interests_text.split(',') if i.strip()]
                seeking_list = [s.strip() for s in seeking_text.split(',') if s.strip()]
                offering_list = [o.strip() for o in offering_text.split(',') if o.strip()]
                # Chama a função para atualizar os dados (que também repopula sugestões e dá rerun)
                update_profile(st.session_state.current_user, interests_list, seeking_list, offering_list)

    # --- PÁGINA MEUS MATCHES ---
    elif selected_page == "Meus Matches":
        st.header("✅ Conexões Confirmadas")
        # Pega os IDs (frozensets) dos matches do usuário atual
        my_match_ids = st.session_state.matches.get(st.session_state.current_user, set())

        if not my_match_ids:
            st.info("Você ainda não formou conexões. Explore a seção 'Matchmaking' e conecte-se!")
        else:
            st.success(f"Você tem {len(my_match_ids)} conexão(ões)! Clique em 'Chat' para iniciar a conversa.")
            st.write("") # Espaçamento

            # Ordena a lista de matches pelo nome do parceiro para exibição consistente
            sorted_match_list = sorted(
                list(my_match_ids),
                key=lambda mid: st.session_state.users_db[get_match_partner(mid, st.session_state.current_user)]['name']
            )

            # Itera sobre os matches ordenados e exibe um card para cada um
            for match_id in sorted_match_list:
                partner_id = get_match_partner(match_id, st.session_state.current_user)
                partner_info = st.session_state.users_db[partner_id]

                with st.container(border=True): # Card para cada match
                    col1, col2, col3 = st.columns([1, 3, 1.5]) # Layout: Imagem | Info | Botão Chat
                    with col1:
                        st.image(partner_info['photo'], width=70) # Imagem do parceiro
                    with col2:
                        st.subheader(f"{partner_info['name']}") # Nome do parceiro
                        st.caption(f"_{partner_info['headline']}_") # Headline do parceiro
                        # Sugestões de tópicos (geradas pela "IA") ficam em um expander discreto
                        initial_messages = [msg['text'] for msg in st.session_state.messages.get(match_id, []) if msg['sender'] == 'system']
                        if initial_messages:
                            with st.expander("🤖 Sugestões para iniciar a conversa", expanded=False): # Fechado por padrão
                                for topic in initial_messages:
                                    st.caption(topic) # Usa caption para ser menos intrusivo

                    with col3:
                        # Botão que leva diretamente para o chat com este parceiro
                        if st.button("💬 Iniciar Chat", key=f"chat_{partner_id}", use_container_width=True):
                             st.session_state.selected_chat_partner = partner_id # Armazena o ID do parceiro para pré-seleção no chat
                             st.session_state.selected_page = "Chat" # Define a página de destino
                             st.rerun() # Recarrega a aplicação para ir para a página de Chat

    # --- PÁGINA CHAT ---
    elif selected_page == "Chat":
        st.header("💬 Mensagens")
        current_user_id = st.session_state.current_user
        # Cria um dicionário mapeando partner_id -> match_id para fácil acesso
        my_matches_dict = {
            get_match_partner(match_id, current_user_id): match_id
            for match_id in st.session_state.matches.get(current_user_id, set())
        }

        if not my_matches_dict:
            st.info("Você precisa ter conexões confirmadas ('Matches') para poder conversar.")
        else:
            # Prepara opções para o selectbox: {partner_id: partner_name}
            partner_options = {pid: st.session_state.users_db[pid]['name'] for pid in my_matches_dict.keys()}
            # Lista ordenada de IDs dos parceiros (para consistência no selectbox)
            partner_ids_list = sorted(list(partner_options.keys()), key=lambda pid: partner_options[pid])

            # --- Lógica para Pré-selecionar o Chat vindo da Tela de Matches ---
            pre_selected_partner_index = 0 # Default é o primeiro da lista ordenada
            if 'selected_chat_partner' in st.session_state:
                partner_to_select = st.session_state.selected_chat_partner
                if partner_to_select in partner_ids_list:
                    try:
                        # Tenta encontrar o índice do parceiro que veio da outra tela
                        pre_selected_partner_index = partner_ids_list.index(partner_to_select)
                    except ValueError:
                        pass # Se ID não for encontrado (raro), mantém o default
                # Limpa a variável de estado para não ficar "presa" nela em futuras navegações
                del st.session_state.selected_chat_partner
            # --- Fim da Lógica de Pré-seleção ---

            # Selectbox para escolher com qual match conversar
            selected_partner_id = st.selectbox(
                "Selecione uma conexão para conversar:",
                options=partner_ids_list, # Usa a lista ordenada de IDs
                format_func=lambda pid: partner_options[pid], # Mostra o nome do parceiro
                index=pre_selected_partner_index, # Define o parceiro pré-selecionado
                placeholder="Escolha com quem conversar..."
            )

            # Se um parceiro foi selecionado no selectbox
            if selected_partner_id:
                selected_match_id = my_matches_dict[selected_partner_id] # Pega o ID do match correspondente
                partner_name = partner_options[selected_partner_id] # Pega o nome do parceiro
                st.subheader(f"Conversa com {partner_name}") # Título do chat
                st.divider()

                # --- Exibição do Histórico de Mensagens com Balões ---
                message_history = st.session_state.messages.get(selected_match_id, [])
                # Container com altura fixa para criar uma área de chat rolável
                chat_container = st.container(height=400, border=False) # Ajuste a altura conforme necessário
                with chat_container:
                    for i, msg in enumerate(message_history): # Usar enumerate pode ser útil para chaves únicas se necessário
                        is_user = msg['sender'] == current_user_id
                        is_system = msg['sender'] == 'system'

                        if is_system:
                            # Mensagem do sistema: centralizada, fundo cinza claro, texto menor
                             st.markdown(f"<div style='text-align: center; margin: 10px 5%;'><span style='background-color: #f0f2f6; color: #65676b; border-radius: 10px; padding: 5px 10px; font-size: 0.85em; display: inline-block;'>{msg['text']}</span></div>", unsafe_allow_html=True)
                        else:
                            # Balões de chat para usuário e parceiro
                            align = "right" if is_user else "left"
                            # Cores dos balões (padrão WhatsApp-like)
                            bg_color = "#DCF8C6" if is_user else "#FFFFFF" # Verde claro para usuário, branco para outro
                            # Estilo CSS inline para o balão
                            bubble_style = f"background-color: {bg_color}; border-radius: 15px; padding: 8px 12px; display: inline-block; max-width: 75%; margin-bottom: 8px; border: 1px solid #E9E9EB; box-shadow: 0px 1px 1px rgba(0,0,0,0.05); word-wrap: break-word;"
                            # Estilo do container do balão para controlar alinhamento (flexbox)
                            container_style = f"display: flex; justify-content: {'flex-end' if is_user else 'flex-start'}; margin-left: {'10%' if is_user else '0'}; margin-right: {'0' if is_user else '10%'};" # Adiciona margem oposta para não colar nas bordas

                            # Renderiza o balão usando markdown com HTML
                            st.markdown(f"""
                            <div style="{container_style}">
                                <div style="{bubble_style}">
                                    {msg['text'].replace('<','<').replace('>','>')} <!-- Escapa HTML básico no texto da mensagem -->
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                # --- Formulário para Envio de Nova Mensagem ---
                st.divider()
                with st.form(key=f"chat_form_{selected_match_id}", clear_on_submit=True):
                    col_input, col_send = st.columns([4, 1]) # Coluna de input maior que a de botão
                    with col_input:
                        new_message = st.text_input(
                            "Mensagem",
                            key=f"msg_input_{selected_match_id}",
                            label_visibility="collapsed", # Oculta o label "Mensagem"
                            placeholder=f"Digite sua mensagem para {partner_name}..."
                        )
                    with col_send:
                        # Botão de envio dentro do form
                        submitted = st.form_submit_button("Enviar ➤", use_container_width=True)

                    # Processa o envio se o botão foi clicado e há texto
                    if submitted and new_message.strip(): # Verifica se a mensagem não está vazia ou só com espaços
                        send_message(selected_match_id, current_user_id, new_message.strip())
                        st.rerun() # Recarrega a página para mostrar a mensagem enviada no histórico
                    elif submitted and not new_message.strip():
                        st.warning("⚠️ Digite algo para enviar.") # Feedback se tentar enviar mensagem vazia

    # --- PÁGINA DASHBOARD ORGANIZADOR ---
    elif selected_page == "Dashboard Organizador":
        st.header("📊 Dashboard do Organizador")
        st.info("ℹ️ Nota: Em uma aplicação real, esta página teria controle de acesso restrito aos organizadores do evento.")
        st.divider()

        # Busca as métricas simuladas
        metrics = simulate_get_metrics()

        st.subheader("Métricas Chave de Engajamento")
        # Exibe as métricas em colunas para melhor visualização
        cols1 = st.columns(3)
        cols1[0].metric("👤 Participantes (Perfis)", metrics['total_users'])
        cols1[1].metric("✅ Matches Confirmados (Únicos)", metrics['total_matches'])
        cols1[2].metric("↔️ Total de Interações (Like/Skip)", metrics['total_interactions'])

        cols2 = st.columns(3)
        cols2[0].metric("👍 Taxa de 'Conectar' (Likes / Interações)", f"{metrics['like_rate_percent']:.1f}%")
        cols2[1].metric("✉️ Total de Mensagens (Usuários)", metrics['total_messages_sent'])
        cols2[2].metric("💬 Média Msgs por Match", f"{metrics['avg_messages_per_match']:.1f}")

        st.divider()
        st.subheader("Dados Brutos da Simulação (Debug)")
        # Expander para não poluir a tela principal do dashboard
        with st.expander("Mostrar/Ocultar Dados Completos da Simulação"):
             st.caption("Banco de Dados de Usuários:")
             st.json(st.session_state.users_db, expanded=False) # Inicia fechado
             st.caption("Interações Registradas (Likes/Skips por Usuário):")
             st.json(st.session_state.interactions, expanded=False)
             st.caption("Matches Confirmados (IDs dos Pares por Usuário):")
             # Converte frozensets para listas para poder serializar em JSON
             serializable_matches = {user: [list(match) for match in matches]
                                     for user, matches in st.session_state.matches.items()}
             st.json(serializable_matches, expanded=False)
             st.caption("Histórico de Mensagens (por ID do Match):")
             # Converte frozensets das chaves para strings (listas) para serializar em JSON
             serializable_messages = {str(list(match_id)): msgs
                                      for match_id, msgs in st.session_state.messages.items()}
             st.json(serializable_messages, expanded=False)

# --- Tela Inicial (Se não estiver logado) ---
# Mostra uma mensagem de boas-vindas e instrução na área principal quando ninguém está logado
if not st.session_state.logged_in:
    st.title("Bem-vindo(a) ao Matchmaking Pro Demo!")
    st.markdown("Use a **barra lateral à esquerda** para simular o login como diferentes participantes e explorar as funcionalidades de conexão.")
    st.image(
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80",
        caption="Imagem: Antenna on Unsplash"
    )
    st.divider()
    st.caption("Este é um protótipo interativo para demonstração.")
