"""
Role-based RAG Configuration
Maps user roles to specific RAG parameters and prompt templates
"""

# Role-aware RAG parameters
ROLE_RAG_PARAMS = {
    "admin": {
        "top_k": 20,
        "temperature": 0.0,
        "include_sources": True,
        "max_chars": 3000
    },
    "research_assistant": {
        "top_k": 15,
        "temperature": 0.0,
        "include_sources": True,
        "max_chars": 2500
    },
    "policy_maker": {
        "top_k": 12,
        "temperature": 0.0,
        "include_sources": True,
        "format": "policy_brief",
        "max_chars": 2000
    },
    "user": {
        "top_k": 5,
        "temperature": 0.2,
        "include_sources": False,
        "max_chars": 800
    }
}

# Alias for backward compatibility
ROLE_CONFIGS = ROLE_RAG_PARAMS

def build_chain_params(user):
    """
    Get RAG parameters based on user object
    
    Args:
        user: User object containing role information
    
    Returns:
        dict: RAG parameters for the role
    """
    user_role = user.get("role", "user")
    
    if user_role == "research_assistant":
        params = {"top_k": 15, "temperature": 0.0, "include_sources": True, "max_chars": 2500}
        print(f"📊 ROLE: {user_role} | PARAMS: temp={params['temperature']}, docs={params['top_k']}")
        return params

    if user_role == "policy_maker":
        params = {"top_k": 12, "temperature": 0.0, "include_sources": True, "format": "policy_brief", "max_chars": 2000}
        print(f"📊 ROLE: {user_role} | PARAMS: temp={params['temperature']}, docs={params['top_k']}")
        return params

    if user_role == "admin":
        params = {"top_k": 20, "temperature": 0.0, "include_sources": True, "format": "comprehensive", "max_chars": 3000}
        print(f"📊 ROLE: {user_role} | PARAMS: temp={params['temperature']}, docs={params['top_k']}")
        return params

    # default: user
    params = {"top_k": 5, "temperature": 0.2, "include_sources": False, "max_chars": 800}
    print(f"📊 ROLE: {user_role} | PARAMS: temp={params['temperature']}, docs={params['top_k']}")
    return params


# Prompt templates by role
RESEARCH_PROMPT = """You are an evidence-first research assistant. Use ONLY the provided document snippets and conversation history to answer. Cite sources as: [Document: <name>, p.<page>]. If information is not in the provided context, respond: "I cannot answer this based on the provided documents." Be concise and factual.

Conversation Context:
{conversation_context}

Recent Messages:
{chat_history}

Document Context:
{context}

Question: {input}

Answer:"""

POLICY_PROMPT = """You are a policy analysis assistant. Synthesize information from provided documents to create clear, actionable policy insights. Structure your response as:
1. Key Findings (2-3 bullet points)
2. Policy Implications
3. Recommendations

Always cite sources: [Document: <name>, p.<page>]. If information is insufficient, state: "Insufficient evidence in provided documents for comprehensive policy analysis."

Conversation Context:
{conversation_context}

Recent Messages:
{chat_history}

Document Context:
{context}

Question: {input}

Policy Brief:"""

USER_PROMPT = """You are a helpful assistant. Answer the question based on the provided documents and conversation history. Keep your response concise and easy to understand. Use simple language.

Conversation Context:
{conversation_context}

Recent Messages:
{chat_history}

Document Context:
{context}

Question: {input}

Answer:"""

ADMIN_PROMPT = """You are a comprehensive research and analysis assistant with full access. Provide detailed, evidence-based responses with complete source citations. Analyze information thoroughly and highlight any data gaps or inconsistencies.

Conversation Context:
{conversation_context}

Recent Messages:
{chat_history}

Document Context:
{context}

Question: {input}

Detailed Analysis:"""

ROLE_PROMPTS = {
    "admin": ADMIN_PROMPT,
    "research_assistant": RESEARCH_PROMPT,
    "policy_maker": POLICY_PROMPT,
    "user": USER_PROMPT
}

def get_prompt_template(user_role: str) -> str:
    """
    Get prompt template based on user role
    
    Args:
        user_role: User's role (admin, research_assistant, policy_maker, user)
    
    Returns:
        str: Prompt template for the role
    """
    return ROLE_PROMPTS.get(user_role, USER_PROMPT)
