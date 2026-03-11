import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

from app.services.engine.models import ResumeEngineData

def escape_latex(text: str) -> str:
    """Escapes special LaTeX characters to prevent compilation errors."""
    if text is None:
        return ""
    
    # Ordered escape sequence to prevent double escaping
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    
    # Handle backslash first to prevent escaping our own escape sequences
    text = str(text)
    # A simple but robust replacement loop
    escaped_str = ""
    for char in text:
        if char in special_chars:
            escaped_str += special_chars[char]
        else:
            escaped_str += char
            
    return escaped_str

def strip_url(url: str) -> str:
    """Strips https://, http://, and www. from a URL for cleaner display."""
    if not url:
        return ""
    
    url = url.replace("https://", "").replace("http://", "")
    if url.startswith("www."):
        url = url[4:]
    return url

def setup_jinja_env(templates_dir: str) -> Environment:
    """Sets up Jinja2 environment with LaTeX-compatible delimiters."""
    # LaTeX uses { } heavily, so we use \VAR{ } and \BLOCK{ } for Jinja
    # to avoid conflicts with native LaTeX syntax.
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    
    # Register the escape filter
    env.filters['escape_latex'] = escape_latex
    env.filters['escape_latex_safe'] = escape_latex
    env.filters['strip_url'] = strip_url
    return env

def build_latex_resume(resume_data: ResumeEngineData) -> str:
    """Renders the LaTeX template with the given resume data."""
    # Find the backend templates directory
    # apps/backend/app/services/engine -> apps/backend/templates/latex
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    templates_dir = os.path.join(backend_dir, "templates", "latex")
    
    if not os.path.exists(templates_dir):
        raise FileNotFoundError(f"LaTeX templates directory not found at {templates_dir}")
        
    env = setup_jinja_env(templates_dir)
    template = env.get_template("base_resume.tex")
    
    # Convert Pydantic model to dictionary for Jinja
    data_dict = resume_data.model_dump()
    
    # Render
    latex_str = template.render(**data_dict)
    
    return latex_str
