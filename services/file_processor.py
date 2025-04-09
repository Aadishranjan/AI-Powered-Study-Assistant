import logging
import io
from werkzeug.datastructures import FileStorage
from typing import Union

# Setup logging
logger = logging.getLogger(__name__)

def process_file_content(file: FileStorage) -> str:
    """Process uploaded file and extract its text content.
    
    Args:
        file: The uploaded file object
        
    Returns:
        The extracted text content
        
    Raises:
        ValueError: If the file type is not supported or processing fails
    """
    filename = file.filename.lower()
    
    if filename.endswith('.txt'):
        return _process_txt_file(file)
    elif filename.endswith('.pdf'):
        return _process_pdf_file(file)
    elif filename.endswith('.docx'):
        return _process_docx_file(file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def _process_txt_file(file: FileStorage) -> str:
    """Process a text file and return its content.
    
    Args:
        file: The uploaded text file
        
    Returns:
        The text content
    """
    try:
        content = file.read().decode('utf-8')
        return content
    except UnicodeDecodeError:
        try:
            # Try another common encoding if utf-8 fails
            file.seek(0)
            content = file.read().decode('latin-1')
            return content
        except Exception as e:
            logger.error(f"Error decoding text file: {str(e)}")
            raise ValueError(f"Could not decode text file: {str(e)}")

def _process_pdf_file(file: FileStorage) -> str:
    """Process a PDF file and extract its text content.
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        The extracted text content
    """
    try:
        # Import PyPDF2 here to avoid dependency issues if it's not installed
        import PyPDF2
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        
        if not text.strip():
            logger.warning("PDF text extraction returned empty result")
            raise ValueError("Could not extract text from PDF - it may be scanned or image-based")
            
        return text
    
    except ImportError:
        logger.error("PyPDF2 library not available")
        raise ValueError("PDF processing is not available - PyPDF2 library is required")
    except Exception as e:
        logger.error(f"Error processing PDF file: {str(e)}")
        raise ValueError(f"Error processing PDF file: {str(e)}")

def _process_docx_file(file: FileStorage) -> str:
    """Process a DOCX file and extract its text content.
    
    Args:
        file: The uploaded DOCX file
        
    Returns:
        The extracted text content
    """
    try:
        # Import docx here to avoid dependency issues if it's not installed
        import docx
        
        doc = docx.Document(io.BytesIO(file.read()))
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        if not text.strip():
            logger.warning("DOCX text extraction returned empty result")
            raise ValueError("Could not extract text from DOCX - it may be corrupted or empty")
            
        return text
    
    except ImportError:
        logger.error("python-docx library not available")
        raise ValueError("DOCX processing is not available - python-docx library is required")
    except Exception as e:
        logger.error(f"Error processing DOCX file: {str(e)}")
        raise ValueError(f"Error processing DOCX file: {str(e)}")

def get_file_content_summary(content: str, max_length: int = 200) -> str:
    """Get a short summary of file content for display purposes.
    
    Args:
        content: The full content text
        max_length: Maximum length of the summary
        
    Returns:
        A truncated summary of the content
    """
    # Remove excess whitespace
    content = " ".join(content.split())
    
    if len(content) <= max_length:
        return content
    
    # Truncate and add ellipsis
    return content[:max_length - 3] + "..."
