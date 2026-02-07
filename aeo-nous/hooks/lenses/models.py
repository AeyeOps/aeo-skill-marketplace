"""
Nous Typed Models

Pydantic models for automatic JSON hydration:
- StatuslineEntry: Full nested statusline with meta fields
- LearningSignal: Extraction output for behavioral learnings
- KnowledgeSignal: Extraction output for project knowledge
"""

from pydantic import create_model


# =============================================================================
# StatuslineEntry - Nested models matching statusline JSON structure
# =============================================================================

ModelInfo = create_model(
    "ModelInfo",
    id=(str, ...),
    display_name=(str, ...),
)

Workspace = create_model(
    "Workspace",
    current_dir=(str, ...),
    project_dir=(str, ...),
)

OutputStyle = create_model(
    "OutputStyle",
    name=(str, ...),
)

Cost = create_model(
    "Cost",
    total_cost_usd=(float, ...),
    total_duration_ms=(int, ...),
    total_api_duration_ms=(int, ...),
    total_lines_added=(int, ...),
    total_lines_removed=(int, ...),
)

CurrentUsage = create_model(
    "CurrentUsage",
    input_tokens=(int, ...),
    output_tokens=(int, ...),
    cache_creation_input_tokens=(int, ...),
    cache_read_input_tokens=(int, ...),
)

ContextWindow = create_model(
    "ContextWindow",
    context_window_size=(int, ...),
    used_percentage=(int, ...),
    remaining_percentage=(int, ...),
    total_input_tokens=(int, ...),
    total_output_tokens=(int, ...),
    current_usage=(CurrentUsage, ...),
)

StatuslineEntry = create_model(
    "StatuslineEntry",
    # Meta (added by statusline.sh)
    meta_ts=(str, ...),
    meta_host=(str, ...),
    # Session
    session_id=(str, ...),
    transcript_path=(str, ...),
    cwd=(str, ...),
    version=(str, ...),
    # Nested objects
    model=(ModelInfo, ...),
    workspace=(Workspace, ...),
    output_style=(OutputStyle, ...),
    cost=(Cost, ...),
    context_window=(ContextWindow, ...),
    # Flags
    exceeds_200k_tokens=(bool, ...),
)


# =============================================================================
# Extraction Signals - Output from claude --print calls
# =============================================================================

LearningSignal = create_model(
    "LearningSignal",
    ts=(str, ...),
    project=(str, ...),
    session=(str, ...),
    content=(str, ...),
    context=(str, ...),
    suggested_target=(str, ...),
)

KnowledgeSignal = create_model(
    "KnowledgeSignal",
    ts=(str, ...),
    project=(str, ...),
    session=(str, ...),
    category=(str, ...),
    content=(str, ...),
    context=(str, ...),
    suggested_target=(str, ...),
)
