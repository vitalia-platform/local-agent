-- Ativar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Extensão uuid-ossp para geração de UUIDs (caso necessário)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Conhecimento e Auditoria (RAG & HITL)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    source_uri VARCHAR(512),
    doc_type VARCHAR(50),
    page_count INT,
    extracted_text_hash VARCHAR(64),
    hitl_status VARCHAR(20) DEFAULT 'PENDING',
    hitl_reviewer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Memória e Aprendizado (Few-Shot)
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    code_syntax_context TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orquestração e Rastreabilidade do Raciocínio (Agentic Workflow)
CREATE TABLE IF NOT EXISTS openhands_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    workspace_path VARCHAR(255),
    status VARCHAR(50) DEFAULT 'RUNNING',
    result_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_reasoning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trace_id VARCHAR(100) NOT NULL,
    agent_role VARCHAR(100) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    context_snapshot TEXT,
    discarded_options TEXT,
    model_rationale TEXT,
    routing_decision TEXT,
    internal_thought_process TEXT,
    action_taken TEXT,
    is_relevant_for_learning BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nova Tabela: Destilação da Solução Limpa (Agent Lessons)
CREATE TABLE IF NOT EXISTS agent_lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL,
    problem_statement TEXT NOT NULL,
    clean_solution_path TEXT NOT NULL,
    key_takeaway TEXT,
    success_score INT CHECK (success_score >= 0 AND success_score <= 100),
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices HNSW para busca vetorial rápida (opcional, pode ser ajustado para a métrica de distância desejada)
-- CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);
-- CREATE INDEX ON agent_memory USING hnsw (embedding vector_cosine_ops);
-- CREATE INDEX ON agent_lessons USING hnsw (embedding vector_cosine_ops);
