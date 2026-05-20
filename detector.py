"""
LinkSafe Phishing Detector
Singapore SMB uchun phishing link aniqlash logic
"""

import re
from urllib.parse import urlparse


SG_BRANDS = [
    'dbs', 'posb', 'ocbc', 'uob', 'maybank', 'hsbc', 'citibank',
    'singpass', 'iras', 'mom', 'ica', 'hdb', 'cpf', 'moh',
    'singpost', 'ninjavan', 'lalamove', 'qxpress',
    'shopee', 'lazada', 'carousell', 'qoo10',
    'singtel', 'starhub', 'm1'
]

SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club']

PHISHING_KEYWORDS = [
    'verify', 'secure', 'login', 'signin', 'update', 'confirm',
    'account', 'password', 'banking', 'wallet', 'authenticate'
]


def check_link(url):
    signals = []
    
    original_url = url.strip()
    if not original_url.startswith(('http://', 'https://')):
        url = 'http://' + original_url
    else:
        url = original_url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        full_url = url.lower()
    except Exception:
        return {
            'risk_level': 'ERROR',
            'signals': ['Invalid URL format'],
            'emoji': '❌',
            'verdict': 'INVALID URL',
            'message': 'Could not parse this URL.'
        }
    
    if not domain:
        return {
            'risk_level': 'ERROR',
            'signals': ['No domain found'],
            'emoji': '❌',
            'verdict': 'INVALID URL',
            'message': 'No valid domain detected.'
        }
    
    # Signal 1: HTTPS
    if not original_url.startswith('https://'):
        signals.append('🔒 No HTTPS (unencrypted connection)')
    
    # Signal 2: IP address
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}'
    if re.match(ip_pattern, domain):
        signals.append('💻 Uses IP address instead of domain')
    
    # Signal 3: Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            signals.append('⚠️ Suspicious TLD (' + tld + ')')
            break
    
    # Signal 4: Phishing keywords
    found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in full_url]
    if found_keywords:
        signals.append('🎣 Phishing keywords: ' + ', '.join(found_keywords[:3]))
    
    # Signal 5: Brand impersonation
    for brand in SG_BRANDS:
        if brand in domain:
            legit_patterns = [
                brand + '.com.sg',
                brand + '.com',
                brand + '.sg',
                'www.' + brand + '.com.sg',
                'www.' + brand + '.com',
                'www.' + brand + '.sg'
            ]
            is_legit = any(domain == p or domain.endswith('.' + p) for p in legit_patterns)
            if not is_legit:
                signals.append('🎭 Possible ' + brand.upper() + ' brand impersonation')
                break
    
    # Signal 6: Excessive subdomains
    subdomain_count = domain.count('.')
    if subdomain_count > 3:
        signals.append('🌳 Excessive subdomains (' + str(subdomain_count) + ' dots)')
    
    # Signal 7: Punycode
    if 'xn--' in domain:
        signals.append('🅰️ Punycode detected')
    
    # Signal 8: Long URL
    if len(url) > 100:
        signals.append('🐌 Unusually long URL (' + str(len(url)) + ' characters)')
    
    # @ symbol
    if '@' in url:
        try:
            if url.index('@') > url.index('//') + 2:
                signals.append('🎭 Deceptive @ symbol')
        except ValueError:
            pass
    
    signal_count = len(signals)
    
    if signal_count == 0:
        return {
            'risk_level': 'SAFE',
            'signals': [],
            'emoji': '✅',
            'verdict': 'SAFE',
            'message': 'No suspicious indicators found. This link appears safe. Always exercise caution with unknown sources.'
        }
    elif signal_count <= 2:
        return {
            'risk_level': 'SUSPICIOUS',
            'signals': signals,
            'emoji': '⚠️',
            'verdict': 'SUSPICIOUS',
            'message': 'Some warning signs detected. Be careful before clicking.'
        }
    else:
        return {
            'risk_level': 'DANGER',
            'signals': signals,
            'emoji': '🚨',
            'verdict': 'DANGER',
            'message': 'Multiple red flags detected. DO NOT click this link!'
        }


def format_result(url, result):
    emoji = result['emoji']
    verdict = result['verdict']
    
    response = emoji + ' *' + verdict + '*\n\n'
    
    if len(url) > 60:
        display_url = url[:60] + '...'
    else:
        display_url = url
    
    response += '🔗 *Link:* `' + display_url + '`\n\n'
    
    if result['signals']:
        response += '*Issues found:*\n'
        for signal in result['signals']:
            response += '• ' + signal + '\n'
        response += '\n'
    
    response += '_' + result['message'] + '_\n\n'
    response += '━━━━━━━━━━━━━━━\n'
    response += '🛡️ *LinkSafe* — Stop phishing in 2 seconds\n'
    response += '🇸🇬 Built in Singapore'
    
    return response