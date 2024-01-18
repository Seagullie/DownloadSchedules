import re

def extract_last_update_text(text: str) -> str:
    
    # the last updated text looks like this: "(оновлено 11.10.2023)"
    
    pattern = r'\(оновлено (\d{2}\.\d{2}\.\d{4})\)'

    match = re.search(pattern, text)
    
    if match is None:
        return ""
    
    return match.group(1)


        
    
    