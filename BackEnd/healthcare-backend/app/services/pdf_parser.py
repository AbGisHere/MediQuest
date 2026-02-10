"""
PDF Parser Service
Extracts medical data from blood test report PDFs.
"""
import re
import hashlib
from typing import Dict, Optional, Tuple
import pdfplumber
from app.models.blood_report import ReportType


class PDFParser:
    """
    Parses blood test reports from PDF files.
    Extracts structured data using pattern matching.
    """
    
    # Regular expression patterns for extracting values
    # Format: r'(?i)' for case-insensitive matching
    PATTERNS = {
        # CBC Values
        'hemoglobin': [
            r'(?i)hemoglobin[\s:]+(\d+\.?\d*)',
            r'(?i)hb[\s:]+(\d+\.?\d*)',
            r'(?i)hgb[\s:]+(\d+\.?\d*)',
        ],
        'wbc_count': [
            r'(?i)wbc[\s:]+(\d+\.?\d*)',
            r'(?i)white\s*blood\s*cell[\s:]+(\d+\.?\d*)',
            r'(?i)leucocyte[\s:]+(\d+\.?\d*)',
        ],
        'rbc_count': [
            r'(?i)rbc[\s:]+(\d+\.?\d*)',
            r'(?i)red\s*blood\s*cell[\s:]+(\d+\.?\d*)',
            r'(?i)erythrocyte[\s:]+(\d+\.?\d*)',
        ],
        'platelet_count': [
            r'(?i)platelet[\s:]+(\d+\.?\d*)',
            r'(?i)plt[\s:]+(\d+\.?\d*)',
        ],
        'hematocrit': [
            r'(?i)hematocrit[\s:]+(\d+\.?\d*)',
            r'(?i)hct[\s:]+(\d+\.?\d*)',
            r'(?i)pcv[\s:]+(\d+\.?\d*)',
        ],
        
        # Glucose
        'glucose_fasting': [
            r'(?i)fasting\s*glucose[\s:]+(\d+\.?\d*)',
            r'(?i)fbs[\s:]+(\d+\.?\d*)',
            r'(?i)fpg[\s:]+(\d+\.?\d*)',
        ],
        'glucose_random': [
            r'(?i)random\s*glucose[\s:]+(\d+\.?\d*)',
            r'(?i)rbs[\s:]+(\d+\.?\d*)',
        ],
        'glucose_pp': [
            r'(?i)pp\s*glucose[\s:]+(\d+\.?\d*)',
            r'(?i)post\s*prandial[\s:]+(\d+\.?\d*)',
            r'(?i)ppbs[\s:]+(\d+\.?\d*)',
        ],
        'hba1c': [
            r'(?i)hba1c[\s:]+(\d+\.?\d*)',
            r'(?i)glycated\s*hemoglobin[\s:]+(\d+\.?\d*)',
        ],
        
        # Lipid Panel
        'cholesterol_total': [
            r'(?i)total\s*cholesterol[\s:]+(\d+\.?\d*)',
            r'(?i)cholesterol[\s:]+(\d+\.?\d*)',
            r'(?i)tc[\s:]+(\d+\.?\d*)',
        ],
        'cholesterol_hdl': [
            r'(?i)hdl[\s:]+(\d+\.?\d*)',
            r'(?i)hdl\s*cholesterol[\s:]+(\d+\.?\d*)',
        ],
        'cholesterol_ldl': [
            r'(?i)ldl[\s:]+(\d+\.?\d*)',
            r'(?i)ldl\s*cholesterol[\s:]+(\d+\.?\d*)',
        ],
        'cholesterol_vldl': [
            r'(?i)vldl[\s:]+(\d+\.?\d*)',
            r'(?i)vldl\s*cholesterol[\s:]+(\d+\.?\d*)',
        ],
        'triglycerides': [
            r'(?i)triglycerides[\s:]+(\d+\.?\d*)',
            r'(?i)tg[\s:]+(\d+\.?\d*)',
        ],
        
        # Liver Function
        'sgot': [
            r'(?i)sgot[\s:]+(\d+\.?\d*)',
            r'(?i)ast[\s:]+(\d+\.?\d*)',
        ],
        'sgpt': [
            r'(?i)sgpt[\s:]+(\d+\.?\d*)',
            r'(?i)alt[\s:]+(\d+\.?\d*)',
        ],
        'alkaline_phosphatase': [
            r'(?i)alkaline\s*phosphatase[\s:]+(\d+\.?\d*)',
            r'(?i)alp[\s:]+(\d+\.?\d*)',
        ],
        'bilirubin_total': [
            r'(?i)total\s*bilirubin[\s:]+(\d+\.?\d*)',
            r'(?i)bilirubin\s*total[\s:]+(\d+\.?\d*)',
        ],
        'bilirubin_direct': [
            r'(?i)direct\s*bilirubin[\s:]+(\d+\.?\d*)',
            r'(?i)bilirubin\s*direct[\s:]+(\d+\.?\d*)',
        ],
        'total_protein': [
            r'(?i)total\s*protein[\s:]+(\d+\.?\d*)',
        ],
        'albumin': [
            r'(?i)albumin[\s:]+(\d+\.?\d*)',
        ],
        
        # Kidney Function
        'creatinine': [
            r'(?i)creatinine[\s:]+(\d+\.?\d*)',
            r'(?i)creat[\s:]+(\d+\.?\d*)',
        ],
        'urea': [
            r'(?i)urea[\s:]+(\d+\.?\d*)',
            r'(?i)blood\s*urea[\s:]+(\d+\.?\d*)',
        ],
        'uric_acid': [
            r'(?i)uric\s*acid[\s:]+(\d+\.?\d*)',
        ],
        'bun': [
            r'(?i)bun[\s:]+(\d+\.?\d*)',
            r'(?i)blood\s*urea\s*nitrogen[\s:]+(\d+\.?\d*)',
        ],
        'egfr': [
            r'(?i)egfr[\s:]+(\d+\.?\d*)',
            r'(?i)gfr[\s:]+(\d+\.?\d*)',
        ],
        
        # Thyroid
        'tsh': [
            r'(?i)tsh[\s:]+(\d+\.?\d*)',
        ],
        't3': [
            r'(?i)t3[\s:]+(\d+\.?\d*)',
        ],
        't4': [
            r'(?i)t4[\s:]+(\d+\.?\d*)',
        ],
        
        # Electrolytes
        'sodium': [
            r'(?i)sodium[\s:]+(\d+\.?\d*)',
            r'(?i)na[\s:]+(\d+\.?\d*)',
        ],
        'potassium': [
            r'(?i)potassium[\s:]+(\d+\.?\d*)',
            r'(?i)k[\s:]+(\d+\.?\d*)',
        ],
        'chloride': [
            r'(?i)chloride[\s:]+(\d+\.?\d*)',
            r'(?i)cl[\s:]+(\d+\.?\d*)',
        ],
    }
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            text = ""
        
        return text
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file for integrity verification.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def extract_value(text: str, field_name: str) -> Optional[float]:
        """
        Extract a numeric value from text using predefined patterns.
        
        Args:
            text: Text to search in
            field_name: Name of the field to extract
            
        Returns:
            Extracted value as float, or None if not found
        """
        patterns = PDFParser.PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    value = float(match.group(1))
                    return value
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def detect_report_type(text: str) -> ReportType:
        """
        Detect the type of report based on content.
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Detected ReportType
        """
        text_lower = text.lower()
        
        # CBC indicators
        cbc_indicators = ['hemoglobin', 'wbc', 'rbc', 'platelet', 'complete blood count', 'cbc']
        if any(indicator in text_lower for indicator in cbc_indicators):
            return ReportType.CBC
        
        # Lipid panel indicators
        lipid_indicators = ['cholesterol', 'hdl', 'ldl', 'triglyceride', 'lipid profile']
        if any(indicator in text_lower for indicator in lipid_indicators):
            return ReportType.LIPID_PANEL
        
        # Liver function indicators
        liver_indicators = ['sgot', 'sgpt', 'alt', 'ast', 'liver function', 'lft']
        if any(indicator in text_lower for indicator in liver_indicators):
            return ReportType.LIVER_FUNCTION
        
        # Kidney function indicators
        kidney_indicators = ['creatinine', 'urea', 'kidney function', 'kft', 'rft']
        if any(indicator in text_lower for indicator in kidney_indicators):
            return ReportType.KIDNEY_FUNCTION
        
        # Thyroid indicators
        thyroid_indicators = ['tsh', 't3', 't4', 'thyroid']
        if any(indicator in text_lower for indicator in thyroid_indicators):
            return ReportType.THYROID
        
        # Diabetes indicators
        diabetes_indicators = ['glucose', 'hba1c', 'blood sugar']
        if any(indicator in text_lower for indicator in diabetes_indicators):
            return ReportType.DIABETES
        
        return ReportType.GENERAL
    
    @staticmethod
    def parse_blood_report(pdf_path: str) -> Tuple[Dict, str, ReportType, float]:
        """
        Parse a blood report PDF and extract all values.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_values_dict, full_text, report_type, confidence)
        """
        # Extract text from PDF
        text = PDFParser.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {}, "", ReportType.OTHER, 0.0
        
        # Detect report type
        report_type = PDFParser.detect_report_type(text)
        
        # Extract all possible values
        extracted_values = {}
        fields_found = 0
        total_fields_checked = 0
        
        for field_name in PDFParser.PATTERNS.keys():
            total_fields_checked += 1
            value = PDFParser.extract_value(text, field_name)
            if value is not None:
                extracted_values[field_name] = value
                fields_found += 1
        
        # Calculate confidence (percentage of fields found)
        confidence = (fields_found / total_fields_checked * 100) if total_fields_checked > 0 else 0.0
        
        return extracted_values, text, report_type, confidence
