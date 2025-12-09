"""
PDF Parser Service using MinerU
Provides single-file parsing functionality for the upload endpoint
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, Optional
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def parse_single_pdf(pdf_path: str, output_dir: Optional[str] = None) -> Dict:
    """
    Parse a single PDF file using MinerU
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Optional output directory (defaults to data/processed/{filename})
    
    Returns:
        Dict with parse results and status
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return {
            "success": False,
            "error": "File not found",
            "pdf_path": str(pdf_path)
        }
    
    # Create output directory
    if output_dir is None:
        output_dir = Path("data/processed") / pdf_path.stem
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Parsing PDF: {pdf_path.name}")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        # Check if MinerU is available
        result = subprocess.run(
            ["magic-pdf", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.warning("MinerU (magic-pdf) not available, skipping parsing")
            return {
                "success": False,
                "error": "MinerU not installed",
                "message": "Install with: pip install magic-pdf",
                "pdf_path": str(pdf_path),
                "output_dir": str(output_dir)
            }
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("MinerU (magic-pdf) not found in PATH")
        return {
            "success": False,
            "error": "MinerU not found",
            "message": "Install with: pip install magic-pdf",
            "pdf_path": str(pdf_path),
            "output_dir": str(output_dir)
        }
    
    # Run MinerU parsing
    try:
        cmd = [
            "magic-pdf",
            "-p", str(pdf_path),
            "-o", str(output_dir),
            "-m", "auto"  # auto mode for best results
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully parsed: {pdf_path.name}")
            
            # Check for output files
            markdown_file = output_dir / f"{pdf_path.stem}.md"
            json_file = output_dir / f"{pdf_path.stem}.json"
            
            return {
                "success": True,
                "pdf_path": str(pdf_path),
                "output_dir": str(output_dir),
                "markdown_file": str(markdown_file) if markdown_file.exists() else None,
                "json_file": str(json_file) if json_file.exists() else None,
                "stdout": result.stdout,
            }
        else:
            logger.error(f"❌ MinerU parsing failed for: {pdf_path.name}")
            logger.error(f"Error: {result.stderr}")
            
            return {
                "success": False,
                "error": "Parsing failed",
                "pdf_path": str(pdf_path),
                "output_dir": str(output_dir),
                "stderr": result.stderr,
                "stdout": result.stdout
            }
    
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Parsing timeout for: {pdf_path.name}")
        return {
            "success": False,
            "error": "Parsing timeout (>5 minutes)",
            "pdf_path": str(pdf_path),
            "output_dir": str(output_dir)
        }
    
    except Exception as e:
        logger.error(f"❌ Unexpected error parsing {pdf_path.name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "pdf_path": str(pdf_path),
            "output_dir": str(output_dir)
        }


def parse_single_pdf_simple(pdf_path: str) -> Dict:
    """
    Simplified version that just extracts text without MinerU
    Fallback for when MinerU is not available
    """
    try:
        import PyPDF2
        
        pdf_path = Path(pdf_path)
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        
        # Save extracted text
        output_dir = Path("data/processed") / pdf_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        text_file = output_dir / f"{pdf_path.stem}.txt"
        text_file.write_text(text, encoding='utf-8')
        
        return {
            "success": True,
            "method": "PyPDF2",
            "pdf_path": str(pdf_path),
            "output_dir": str(output_dir),
            "text_file": str(text_file),
            "text_length": len(text)
        }
    
    except ImportError:
        return {
            "success": False,
            "error": "PyPDF2 not installed",
            "message": "Install with: pip install PyPDF2"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }