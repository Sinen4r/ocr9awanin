import PyPDF2
import re

# Standard Adobe Glyph List (AGL) mapping for Arabic characters
# Based on Unicode standard and Adobe font specifications
def create_standard_arabic_mapping():
    """
    Creates a comprehensive mapping based on Adobe Glyph List standards
    """
    mapping = {}
    
    # Arabic letters with their Unicode values and positional forms
    arabic_letters = {
        # Letter: (Unicode, isolated, initial, medial, final)
        'alef': ('ا', 'ا', 'ا', '', 'ا'),           # U+0627
        'beh': ('ب', 'ب', 'ب', 'ب', 'ب'),           # U+0628  
        'teh': ('ت', 'ت', 'ت', 'ت', 'ت'),           # U+062A
        'theh': ('ث', 'ث', 'ث', 'ث', 'ث'),          # U+062B
        'jeem': ('ج', 'ج', 'ج', 'ج', 'ج'),          # U+062C
        'hah': ('ح', 'ح', 'ح', 'ح', 'ح'),           # U+062D
        'khah': ('خ', 'خ', 'خ', 'خ', 'خ'),          # U+062E
        'dal': ('د', 'د', 'د', '', 'د'),            # U+062F
        'thal': ('ذ', 'ذ', 'ذ', '', 'ذ'),           # U+0630
        'reh': ('ر', 'ر', 'ر', '', 'ر'),            # U+0631
        'zain': ('ز', 'ز', 'ز', '', 'ز'),           # U+0632
        'seen': ('س', 'س', 'س', 'س', 'س'),          # U+0633
        'sheen': ('ش', 'ش', 'ش', 'ش', 'ش'),         # U+0634
        'sad': ('ص', 'ص', 'ص', 'ص', 'ص'),           # U+0635
        'dad': ('ض', 'ض', 'ض', 'ض', 'ض'),           # U+0636
        'tah': ('ط', 'ط', 'ط', 'ط', 'ط'),           # U+0637
        'zah': ('ظ', 'ظ', 'ظ', 'ظ', 'ظ'),           # U+0638
        'ain': ('ع', 'ع', 'ع', 'ع', 'ع'),           # U+0639
        'ghain': ('غ', 'غ', 'غ', 'غ', 'غ'),          # U+063A
        'feh': ('ف', 'ف', 'ف', 'ف', 'ف'),           # U+0641
        'qaf': ('ق', 'ق', 'ق', 'ق', 'ق'),           # U+0642
        'kaf': ('ك', 'ك', 'ك', 'ك', 'ك'),           # U+0643
        'lam': ('ل', 'ل', 'ل', 'ل', 'ل'),           # U+0644
        'meem': ('م', 'م', 'م', 'م', 'م'),          # U+0645
        'noon': ('ن', 'ن', 'ن', 'ن', 'ن'),          # U+0646
        'heh': ('ه', 'ه', 'ه', 'ه', 'ه'),           # U+0647
        'waw': ('و', 'و', 'و', '', 'و'),            # U+0648
        'yeh': ('ي', 'ي', 'ي', 'ي', 'ي'),           # U+064A
    }
    
    # Generate all positional forms
    for letter, (char, isolated, initial, medial, final) in arabic_letters.items():
        # Add main character (isolated form)
        mapping[f'arabic{letter}'] = char
        mapping[letter] = char
        
        # Add positional forms if they exist
        if initial:
            mapping[f'{letter}initial'] = char
        if medial:
            mapping[f'{letter}medial'] = char  
        if final:
            mapping[f'{letter}final'] = char
    
    # Special Alef variants
    mapping.update({
        'alefwithhamzaabove': 'أ',     # U+0623
        'alefwithhamzabelow': 'إ',      # U+0625
        'alefmaksura': 'ى',            # U+0649
        'alefmaksurafinal': 'ى',
        
        # Lam-Alef ligatures
        'lamwithalef': 'لا',
        'lamwithaleffinal': 'لا',
        'lamwithalefisolated': 'لا',
        'lamwithalefhamzaabove': 'لأ',
        'lamwithalefhamzabelow': 'لإ',
        'lamwithalefhamzabelowisolated': 'لإ',
        
        # Hamza variants
        'wawwithhamzaabove': 'ؤ',      # U+0624
        'wawwithhamzaabovefinal': 'ؤ',
        'yehwithhamzaabove': 'ئ',      # U+0626
        'yehwithhamzaaboveinitial': 'ئ',
        'yehwithhamzaabovemedial': 'ئ',
        
        # Teh Marbuta
        'tehmarbuta': 'ة',             # U+0629
        'tehmarbutafinal': 'ة',
        
        # Diacritics
        'fatha': 'َ',                  # U+064E
        'damma': 'ُ',                  # U+064F  
        'kasra': 'ِ',                  # U+0650
        'shadda': 'ّ',                 # U+0651
        'shaddalow': 'ّ',              # Alternative name
        'sukun': 'ْ',                  # U+0652
        'fathatan': 'ً',               # U+064B
        'dammatan': 'ٌ',               # U+064C
        'kasratan': 'ٍ',               # U+064D
        
        # Arabic-Indic digits
        'arabicindiczero': '٠',        # U+0660
        'arabicindicone': '١',         # U+0661
        'arabicindictwo': '٢',         # U+0662
        'arabicindicthree': '٣',       # U+0663
        'arabicindicfour': '٤',        # U+0664
        'arabicindicfive': '٥',        # U+0665
        'arabicindicsix': '٦',         # U+0666
        'arabicindicseven': '٧',       # U+0667
        'arabicindiceight': '٨',       # U+0668
        'arabicindicnine': '٩',        # U+0669
        
        # Also handle common short names
        'zero': '٠', 'one': '١', 'two': '٢', 'three': '٣', 'four': '٤',
        'five': '٥', 'six': '٦', 'seven': '٧', 'eight': '٨', 'nine': '٩',
        
        # Arabic punctuation
        'arabiccomma': '،',            # U+060C
        'arabicsemicolon': '؛',        # U+061B  
        'arabicquestionmark': '؟',     # U+061F
        'comma': '،',
        'semicolon': '؛', 
        'questionmark': '؟',
        
        # Common punctuation
        'period': '.',
        'hyphen': '-',
        'space': ' ',
        'parenleft': '(',
        'parenright': ')',
    })
    
    return mapping

# Create the standard mapping
mapping = create_standard_arabic_mapping()

def decode_tokens(token_text):
    """
    Decode Arabic glyph tokens to Arabic text using Adobe Glyph List standards
    """
    result = []
    tokens = token_text.split("/")
    
    for token in tokens:
        token = token.strip()
        if not token:  # Skip empty tokens
            continue
            
        # Handle direct Arabic text that might be mixed in
        if is_arabic_text(token):
            result.append(token)
            continue
            
        # Handle numbers
        if token.isdigit():
            # Convert to Arabic-Indic numerals if desired
            arabic_digits = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
            if len(token) == 1:
                result.append(arabic_digits[int(token)])
            else:
                result.append(token)  # Keep multi-digit numbers as-is
            continue
        
        # Try exact match first
        if token in mapping:
            result.append(mapping[token])
            continue
        
        # Try case-insensitive match
        token_lower = token.lower()
        found = False
        for key, value in mapping.items():
            if key.lower() == token_lower:
                result.append(value)
                found = True
                break
        
        if found:
            continue
            
        # Try to parse using AGL naming conventions
        parsed_char = parse_agl_name(token)
        if parsed_char:
            result.append(parsed_char)
            continue
            
        # Last resort: partial matching
        for key in mapping:
            if token.lower() in key.lower() or key.lower() in token.lower():
                result.append(mapping[key])
                found = True
                break
        
        if not found:
            print(f"Unknown glyph token: '{token}' - please add to mapping")
            result.append("?")
    
    return "".join(result)

def is_arabic_text(text):
    """Check if text contains Arabic characters"""
    for char in text:
        if '\u0600' <= char <= '\u06FF' or '\uFE70' <= char <= '\uFEFF':
            return True
    return False

def parse_agl_name(glyph_name):
    """
    Parse Adobe Glyph List naming convention
    Format: letterpostionalform (e.g., 'lamfinal', 'sadmedial')
    """
    # Common positional suffixes in AGL
    suffixes = {
        'initial': 'initial',
        'medial': 'medial', 
        'final': 'final',
        'isolated': ''
    }
    
    for suffix, pos in suffixes.items():
        if glyph_name.endswith(suffix):
            base_name = glyph_name[:-len(suffix)] if suffix else glyph_name
            
            # Try to find the base character
            for key in mapping:
                if key.startswith(base_name) and (not pos or key.endswith(pos)):
                    return mapping[key]
            
            # Try with 'arabic' prefix
            arabic_key = f'arabic{base_name}'
            if arabic_key in mapping:
                return mapping[arabic_key]
    
    return None

def extract_and_parse_arabic_pdf(pdf_path):
    """
    Extract text from PDF and parse Arabic glyph tokens
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            all_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                print(f"--- Raw Page {i+1} ---")
                print(text[:200] + "..." if len(text) > 200 else text)
                print()
                
                # Parse Arabic tokens if they exist
                if "/" in text and any(token in text for token in ["arabicalef", "lam", "noon", "meem"]):
                    parsed_text = decode_tokens(text)
                    print(f"--- Parsed Arabic Page {i+1} ---")
                    print(parsed_text)
                    print("-" * 50)
                    all_text.append(parsed_text)
                else:
                    all_text.append(text)
            
            return "\n".join(all_text)
    
    except FileNotFoundError:
        print(f"File {pdf_path} not found!")
        return None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def parse_sample_text():
    """
    Parse the sample text you provided
    """
    sample_text = """edial/behinitial /aleffinal/nooninitial/ذوalefwithhamzaabovefinal/meeminitial /نaleffinal/kafinitial /arabicalef/ذalefwithhamzabelow /lamwithalefisolated/alefwithhamzabelow /hehfinal/lammedial/kafinitial/ وnoonfinal/meemmedial/aininitial /ولwawwithhamzaabovefinal/seenmedial/meeminitial /lamfinal/yehmedial/kafinitial/wawfinal/laminitial/arabicalef
 /reh/aleffinal/tehmedial/khahinitial/arabicalef /وalefwithhamzaabove /lamwithaleffinal/yehmedial/kafinitial/ن وwawfinal/kafmedial/yehinitial /نalefwithhamzaabove /hahfinal/lammedial/sadmedial/yehinitial /َ lamwithalefisolated /noonfinal/meeminitial /reh/aleffinal/tehmedial/khahinitial/arabicalef /arabicalef/ذalefwithhamzabelow /lamwithalefisolated/alefwithhamzabelow /noonfinal/meemmedial/dadmedial/yehinitial /lamwithaleffinal/fehinitial /sadfinal/khahmedial/sheeninitial /noonfinal/yehmedial/yehmedial/ainmedial/tehinitial /ونdalfinal/behinitial /behfinal/seenmedial/hahmedial/behinitial /hehfinal/tehmedial/behmedial/qafinitial/arabicalef/rehfinal/meeminitial /hehfinal/yehmedial/lammedial/aininitial /behfinal/jeeminitial/arabicalef/wawfinal/laminitial/arabicalef /noonfinal/meeminitial /نaleffinal/kafinitial /arabicalef/ذalefwithhamzabelow /hehfinal/behmedial/qafinitial/arabicalef/rehfinal/yehinitial /meemfinal/laminitial /وalefwithhamzaabove /ةrehfinal/dadmedial/meemmedial/laminitial/arabicalef /behfinal/lammedial/jeeminitial /aleffinal/meemmedial/behinitial /hehfinal/nooninitial/ذalefwithhamzaabove/ وhahfinal/laminitial/aleffinal/sadmedial/laminitial/arabicalef
 /تaleffinal/yehmedial/dadmedial/tehmedial/qafmedial/meeminitial/لaleffinal/hahmedial/laminitial/arabicalef."""
    
    print("--- Sample Text Parsing ---")
    parsed = decode_tokens(sample_text)
    print("Parsed Arabic text:")
    print(parsed)
    print()

def find_missing_tokens(text):
    """
    Find tokens that are not in the mapping to help extend it
    """
    tokens = text.split("/")
    missing = set()
    
    for token in tokens:
        token = token.strip()
        if token and token not in mapping and not token.isdigit():
            missing.add(token)
    
    if missing:
        print("Missing tokens found:")
        for token in sorted(missing):
            print(f"  '{token}': '',")
    
    return missing

# Main execution
if __name__ == "__main__":
    # Parse the sample text first
    # parse_sample_text()
    
    # Try to parse the PDF if it exists
    pdf_result = extract_and_parse_arabic_pdf("COCArabe.pdf")
    
    # You can also test with your sample text to find missing tokens
    # sample_text = """edial/behinitial /aleffinal/nooninitial/ذوalefwithhamzaabovefinal/meeminitial /نaleffinal/kafinitial /arabicalef/ذalefwithhamzabelow /lamwithalefisolated/alefwithhamzabelow /hehfinal/lammedial/kafinitial/ وnoonfinal/meemmedial/aininitial /ولwawwithhamzaabovefinal/seenmedial/meeminitial /lamfinal/yehmedial/kafinitial/wawfinal/laminitial/arabicalef"""
    
    print("\n--- Finding Missing Tokens ---")
    # find_missing_tokens(sample_text)