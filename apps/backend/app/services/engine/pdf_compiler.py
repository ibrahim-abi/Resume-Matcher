import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

async def compile_to_pdf_docker(latex_content: str, output_path: str) -> bool:
    """
    Compiles a LaTeX string to a PDF file using a lightweight Docker container (aergus/latex).
    This avoids needing to install a massive 2+ GB TeX Live distribution on the host.
    """
    try:
        # Create a temporary directory to mount into the docker container
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file_path = temp_path / "resume.tex"
            
            # Write the raw LaTeX string to the internal temp file
            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
                
            # Run the LaTeX compile command inside docker
            # We mount the temporary directory to /data inside the container
            # We use interaction=nonstopmode to ensure it doesn't wait for user input on error
            docker_cmd = [
                "docker", "run", "--rm", 
                "-v", f"{str(temp_path.absolute())}:/data", 
                "aergus/latex", 
                "pdflatex", 
                "-interaction=nonstopmode", 
                "-output-directory=/data", 
                "/data/resume.tex"
            ]
            
            logger.info("Starting Docker LaTeX compilation...")
            
            # Use subprocess to run the docker command synchronously (or asyncio.create_subprocess_exec for true async)
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"LaTeX Compilation Failed (Code {process.returncode})")
                logger.error(stdout.decode())
                logger.error(stderr.decode())
                return False
                
            # The PDF was created successfully inside temp_dir
            generated_pdf_path = temp_path / "resume.pdf"
            
            if generated_pdf_path.exists():
                # Move the PDF to the requested output_path
                import shutil
                shutil.copy(generated_pdf_path, output_path)
                logger.info(f"LaTeX PDF successfully created at {output_path}")
                return True
            else:
                logger.error("pdflatex completed but the PDF file was not generated.")
                return False
                
    except Exception as e:
        logger.error(f"Failed to compile PDF via Docker: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

import asyncio
