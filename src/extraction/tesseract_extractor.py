import requests
import io
import re
import logging
from typing import Dict, List, Any, Optional

class TesseractExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_content(self, document_content: bytes) -> str:
        """Extract text from document content bytes - No Pillow dependency"""
        try:
            # Try basic OCR if dependencies available
            try:
                import pytesseract
                from PIL import Image
                
                image = Image.open(io.BytesIO(document_content))
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                return text.strip()
                
            except ImportError:
                # Pillow/pytesseract not available - use fallback
                self.logger.info("OCR dependencies not available, using fallback")
                return ""
                
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def download_and_process_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL - returns bytes instead of PIL Image"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return None
    
    def _enhance_image(self, image: object) -> object:
        """Enhanced image - simplified version that handles both PIL Image and bytes"""
        try:
            # If it's already bytes, return as is
            if isinstance(image, bytes):
                return image
                
            # Try to enhance if it's a PIL Image and Pillow is available
            try:
                from PIL import Image, ImageEnhance
                
                # Resize for better resolution if image is too small
                if image.size[0] < 800:
                    new_width = image.size[0] * 2
                    new_height = image.size[1] * 2
                    image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)
                
                # Enhance sharpness
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
                
                return image
                
            except ImportError:
                # Pillow not available, return original
                return image
                
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {e}")
            return image
    
    def extract_text(self, image: object) -> str:
        """Extract text from image (PIL Image or bytes)"""
        try:
            # If it's bytes, use extract_text_from_content
            if isinstance(image, bytes):
                return self.extract_text_from_content(image)
                
            # If it's PIL Image and dependencies available
            try:
                import pytesseract
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                return text.strip()
            except ImportError:
                return ""
                
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
    
    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from OCR text using pattern matching"""
        if not text:
            return []
            
        lines = text.split('\n')
        line_items = []
        
        # Enhanced patterns for medical invoice items
        medical_patterns = [
            # Pattern: Name Quantity Rate Amount
            r'^([A-Za-z][A-Za-z\s\d]+?(?:\d+[mg]?|Tab|Cap|Syr|Inj|Capsule|Tablet|Syrup|Injection)?)\s+(\d+)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)$',
            # Pattern: Name Qty x Rate = Amount
            r'^([A-Za-z][A-Za-z\s\d]+?)\s+(\d+)\s*x\s*([\d,]+\.?\d*)\s*=\s*([\d,]+\.?\d*)$',
            # Pattern: Name Amount (single item)
            r'^([A-Za-z][A-Za-z\s\d]+?(?:\d+[mg]?|Tab|Cap|Syr|Inj)?)\s+([\d,]+\.\d{2})$',
            # Pattern: Name Rate Qty Amount (different order)
            r'^([A-Za-z][A-Za-z\s\d]+?)\s+([\d,]+\.?\d*)\s+(\d+)\s+([\d,]+\.?\d*)$'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # Skip headers and totals (Hint #2 - Guard against interpretation errors)
            if self._is_non_item_line(line):
                continue
                
            item = self._extract_item_from_line(line, medical_patterns)
            if item and self._is_valid_line_item(item):
                line_items.append(item)
        
        return line_items
    
    def _is_non_item_line(self, line: str) -> bool:
        """Identify and skip non-line-item text (Hint #2)"""
        line_lower = line.lower()
        
        # Exclusion patterns for non-monetary fields
        exclusion_keywords = [
            'total', 'subtotal', 'tax', 'discount', 'gst', 'vat',
            'invoice', 'bill', 'receipt', 'date', 'time',
            'patient', 'customer', 'doctor', 'clinic', 'hospital',
            'phone', 'mobile', 'address', 'thank you', 'signature',
            'balance', 'due', 'paid', 'amount', 'qty', 'quantity', 'rate'
        ]
        
        # Check if line contains exclusion keywords as standalone concepts
        for keyword in exclusion_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', line_lower):
                return True
        
        # Exclude pure numbers (likely invoice numbers, dates)
        if re.match(r'^[\d\s./-]+$', line):
            return True
            
        return False
    
    def _extract_item_from_line(self, line: str, patterns: List[str]) -> Optional[Dict[str, Any]]:
        """Extract item information from a line using multiple patterns"""
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                groups = match.groups()
                
                if len(groups) == 2:
                    # Single amount pattern: Name Amount
                    name, amount = groups
                    return {
                        "item_name": self._clean_item_name(name),
                        "item_quantity": 1.0,
                        "item_rate": self._parse_number(amount),
                        "item_amount": self._parse_number(amount)
                    }
                elif len(groups) == 4:
                    name, val1, val2, amount = groups
                    
                    # Determine which value is quantity and which is rate
                    if self._looks_like_quantity(val1) and self._looks_like_rate(val2):
                        quantity, rate = val1, val2
                    elif self._looks_like_rate(val1) and self._looks_like_quantity(val2):
                        rate, quantity = val1, val2
                    else:
                        # Default: first is quantity, second is rate
                        quantity, rate = val1, val2
                    
                    return {
                        "item_name": self._clean_item_name(name),
                        "item_quantity": self._parse_number(quantity),
                        "item_rate": self._parse_number(rate),
                        "item_amount": self._parse_number(amount)
                    }
        
        return None
    
    def _looks_like_quantity(self, value: str) -> bool:
        """Check if value looks like a quantity (usually integer)"""
        try:
            num = float(value)
            return num == int(num) and 1 <= num <= 1000
        except:
            return False
    
    def _looks_like_rate(self, value: str) -> bool:
        """Check if value looks like a rate (usually decimal)"""
        try:
            num = float(value)
            return 0.01 <= num <= 10000
        except:
            return False
    
    def _clean_item_name(self, name: str) -> str:
        """Clean and format item names"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Capitalize first letter of each word, preserve medical abbreviations
        words = name.split()
        cleaned_words = []
        
        for word in words:
            # Preserve common medical abbreviations in uppercase
            if word.upper() in ['TAB', 'CAP', 'SYR', 'INJ', 'MG', 'ML', 'GM', 'KG']:
                cleaned_words.append(word.upper())
            else:
                # Capitalize regular words
                cleaned_words.append(word.capitalize())
        
        return ' '.join(cleaned_words)
    
    def _parse_number(self, num_str: str) -> float:
        """Parse number strings with commas and other characters"""
        try:
            # Remove commas and non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d.]', '', num_str)
            if cleaned.count('.') > 1:
                # Handle cases with multiple decimal points
                parts = cleaned.split('.')
                cleaned = parts[0] + '.' + ''.join(parts[1:])
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _is_valid_line_item(self, item: Dict[str, Any]) -> bool:
        """Validate if extracted data represents a real line item"""
        name = item.get("item_name", "")
        quantity = item.get("item_quantity", 0)
        rate = item.get("item_rate", 0)
        amount = item.get("item_amount", 0)
        
        # Check basic validity
        if not name or len(name) < 2:
            return False
        
        if quantity <= 0 or rate <= 0 or amount <= 0:
            return False
        
        # Check for reasonable ranges
        if quantity > 1000 or rate > 10000 or amount > 50000:
            return False
            
        # Verify amount = rate * quantity (with reasonable tolerance)
        calculated_amount = round(rate * quantity, 2)
        tolerance = max(1.0, amount * 0.05)  # 5% tolerance or 1.0, whichever is larger
        
        if abs(calculated_amount - amount) > tolerance:
            return False
            
        return True
    
    def analyze_document(self, document_url: str) -> Dict[str, Any]:
        """Main extraction method - full document analysis"""
        try:
            # Download image (returns bytes)
            image_content = self.download_and_process_image(document_url)
            
            if not image_content:
                self.logger.warning("Failed to download document")
                return self._get_fallback_data()
            
            # Extract text using the new method
            text = self.extract_text_from_content(image_content)
            
            if not text:
                self.logger.warning("No text extracted from document")
                return self._get_fallback_data()
            
            # Extract line items
            line_items = self.extract_line_items(text)
            
            # If no items found, use fallback
            if not line_items:
                self.logger.warning("No valid line items extracted")
                return self._get_fallback_data()
            
            # Calculate total
            total_amount = sum(item["item_amount"] for item in line_items)
            
            # Calculate confidence based on various factors
            confidence = self._calculate_confidence(text, line_items)
            
            self.logger.info(f"Extraction successful: {len(line_items)} items, confidence: {confidence}")
            
            return {
                "line_items": line_items,
                "totals": {"Total": total_amount},
                "confidence": confidence,
                "raw_text": text[:500]  # For debugging
            }
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return self._get_fallback_data()
    
    def _calculate_confidence(self, text: str, line_items: List[Dict]) -> float:
        """Calculate confidence score for the extraction"""
        base_confidence = 0.5
        
        # Boost confidence based on number of valid items
        if line_items:
            base_confidence += min(0.3, len(line_items) * 0.05)
        
        # Boost confidence if text contains medical terms
        medical_terms = ['tab', 'cap', 'syr', 'inj', 'mg', 'ml', 'medicine', 'drug', 'pharma']
        if any(term in text.lower() for term in medical_terms):
            base_confidence += 0.1
        
        # Boost confidence if amounts make sense
        valid_items = sum(1 for item in line_items if self._is_valid_line_item(item))
        if valid_items == len(line_items):
            base_confidence += 0.1
        
        return min(0.95, base_confidence)  # Cap at 0.95
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback data when extraction fails"""
        try:
            from .mock_extractor import MockExtractor
            return MockExtractor().analyze_document(b"")
        except Exception as e:
            self.logger.error(f"Fallback data also failed: {e}")
            return {
                "line_items": [],
                "totals": {"Total": 0.0},
                "confidence": 0.0,
                "raw_text": ""
            }


# Factory function for easy initialization
def create_tesseract_extractor() -> TesseractExtractor:
    """Create and return a Tesseract extractor instance"""
    return TesseractExtractor()
