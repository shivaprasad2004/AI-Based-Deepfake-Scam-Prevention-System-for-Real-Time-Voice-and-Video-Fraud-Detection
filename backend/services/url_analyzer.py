import re
import requests
import subprocess
import json
import socket
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class URLAnalyzer:
    """Analyzes URLs to determine if they are legitimate or potentially fake/scam."""

    # Known legitimate domains
    TRUSTED_DOMAINS = {
        'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com',
        'facebook.com', 'www.facebook.com', 'fb.watch',
        'instagram.com', 'www.instagram.com',
        'twitter.com', 'x.com', 'www.twitter.com',
        'tiktok.com', 'www.tiktok.com',
        'vimeo.com', 'www.vimeo.com',
        'dailymotion.com', 'www.dailymotion.com',
        'reddit.com', 'www.reddit.com',
        'linkedin.com', 'www.linkedin.com',
        'twitch.tv', 'www.twitch.tv',
        'wikipedia.org', 'en.wikipedia.org',
        'github.com', 'www.github.com',
        'bbc.com', 'www.bbc.com', 'bbc.co.uk',
        'cnn.com', 'www.cnn.com',
        'nytimes.com', 'www.nytimes.com',
        'theguardian.com', 'www.theguardian.com',
        'reuters.com', 'www.reuters.com',
        'apnews.com', 'www.apnews.com',
        'google.com', 'www.google.com',
        'amazon.com', 'www.amazon.com',
        'microsoft.com', 'www.microsoft.com',
        'apple.com', 'www.apple.com',
        'netflix.com', 'www.netflix.com',
        'spotify.com', 'www.spotify.com',
        'stackoverflow.com', 'www.stackoverflow.com',
        'medium.com', 'www.medium.com',
        'quora.com', 'www.quora.com',
    }

    # Suspicious TLDs often used in scam/phishing
    SUSPICIOUS_TLDS = {
        'tk', 'ml', 'ga', 'cf', 'gq', 'buzz', 'top', 'xyz', 'club',
        'work', 'date', 'racing', 'win', 'bid', 'stream', 'download',
        'click', 'link', 'info', 'icu', 'monster', 'rest',
    }

    # Phishing keywords in URLs
    PHISHING_KEYWORDS = [
        'login', 'signin', 'verify', 'account', 'secure', 'update',
        'confirm', 'password', 'credential', 'banking', 'paypal',
        'wallet', 'prize', 'winner', 'free-money', 'giveaway',
        'claim', 'reward', 'urgent', 'suspended', 'limited-time',
    ]

    # URL shortener domains
    SHORTENER_DOMAINS = {
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
        'is.gd', 'buff.ly', 'rebrand.ly', 'cutt.ly', 'shorturl.at',
    }

    # Suspicious content patterns
    SUSPICIOUS_HTML_PATTERNS = [
        (r'<form[^>]*action=["\'](?!https?://[^"\']*(?:' + '|'.join([
            r'google\.com', r'facebook\.com', r'youtube\.com', r'github\.com',
            r'microsoft\.com', r'apple\.com', r'amazon\.com',
        ]) + r'))', 'External form action to unknown domain'),
        (r'<input[^>]*type=["\']password["\']', 'Password input field detected'),
        (r'<iframe[^>]*style=["\'][^"\']*display\s*:\s*none', 'Hidden iframe detected'),
        (r'<meta[^>]*http-equiv=["\']refresh["\']', 'Meta refresh redirect detected'),
        (r'document\.cookie', 'JavaScript accessing cookies'),
        (r'eval\s*\(', 'JavaScript eval() usage detected'),
        (r'window\.location\s*=', 'JavaScript redirect detected'),
        (r'<script[^>]*src=["\'](?:https?:)?//(?!(?:cdn|ajax|apis?|static|assets|code)\.|localhost)', 'External script from unknown source'),
    ]

    # Security headers to check
    SECURITY_HEADERS = [
        'x-frame-options',
        'x-content-type-options',
        'content-security-policy',
        'strict-transport-security',
        'x-xss-protection',
    ]

    @staticmethod
    def analyze(url):
        """Perform comprehensive URL analysis and return a report."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = 'https://' + url
                parsed = urlparse(url)

            if not parsed.hostname:
                return {'error': 'Invalid URL format'}

            hostname = parsed.hostname.lower()
            report = {
                'url': url,
                'hostname': hostname,
                'analysis_type': 'link',
                'timestamp': datetime.utcnow().isoformat(),
            }

            # Run all checks
            checks = {}
            checks['domain_trust'] = URLAnalyzer._check_domain_trust(hostname)
            checks['tld_safety'] = URLAnalyzer._check_tld(hostname)
            checks['url_structure'] = URLAnalyzer._check_url_structure(url, parsed)
            checks['phishing_keywords'] = URLAnalyzer._check_phishing_keywords(url)
            checks['ssl_certificate'] = URLAnalyzer._check_ssl(url, parsed)
            checks['redirect_chain'] = URLAnalyzer._check_redirects(url)
            checks['url_shortener'] = URLAnalyzer._check_shortener(hostname)
            checks['domain_age_signals'] = URLAnalyzer._check_domain_age_signals(hostname)
            checks['page_content'] = URLAnalyzer._check_page_content(url)
            checks['security_headers'] = URLAnalyzer._check_security_headers(url)
            checks['domain_whois'] = URLAnalyzer._check_domain_whois(hostname)

            # Platform-specific checks
            platform_info = URLAnalyzer._get_platform_info(url, hostname)
            if platform_info:
                report['platform_info'] = platform_info

            # Calculate scores
            risk_score, risk_details = URLAnalyzer._calculate_risk(checks)
            safety_score = max(0, 100 - risk_score)

            report['checks'] = checks
            report['risk_score'] = round(risk_score, 1)
            report['safety_score'] = round(safety_score, 1)
            report['fake_percentage'] = round(risk_score, 1)
            report['real_percentage'] = round(safety_score, 1)
            report['risk_level'] = URLAnalyzer._get_risk_level(risk_score)
            report['confidence_score'] = URLAnalyzer._calculate_confidence(checks)
            report['risk_details'] = risk_details
            report['verdict'] = URLAnalyzer._get_verdict(risk_score)

            # Analysis summary for charts
            report['analysis_summary'] = {
                'domain_trust': checks['domain_trust']['score'],
                'url_safety': checks['url_structure']['score'],
                'ssl_security': checks['ssl_certificate']['score'],
                'phishing_risk': 100 - checks['phishing_keywords']['score'],
                'redirect_safety': checks['redirect_chain']['score'],
                'content_safety': checks['page_content']['score'],
                'header_security': checks['security_headers']['score'],
            }

            report['metadata'] = {
                'url_length': len(url),
                'hostname': hostname,
                'scheme': parsed.scheme,
                'path': parsed.path,
                'has_query_params': bool(parsed.query),
            }

            return report

        except Exception as e:
            return {'error': f'URL analysis failed: {str(e)}'}

    @staticmethod
    def _check_domain_trust(hostname):
        """Check if the domain is in the trusted list."""
        if hostname in URLAnalyzer.TRUSTED_DOMAINS:
            return {'status': 'safe', 'score': 98, 'detail': f'{hostname} is a well-known trusted domain'}

        for trusted in URLAnalyzer.TRUSTED_DOMAINS:
            if hostname.endswith('.' + trusted):
                return {'status': 'safe', 'score': 88, 'detail': f'Subdomain of trusted domain {trusted}'}

        for trusted in URLAnalyzer.TRUSTED_DOMAINS:
            base = trusted.replace('www.', '')
            if URLAnalyzer._is_similar(hostname.replace('www.', ''), base):
                return {'status': 'warning', 'score': 15, 'detail': f'Domain looks similar to {trusted} — possible typosquatting'}

        return {'status': 'unknown', 'score': 35, 'detail': 'Domain is not in trusted list — requires further verification'}

    @staticmethod
    def _is_similar(a, b):
        """Simple Levenshtein-like check for typosquatting."""
        if a == b:
            return False
        if len(a) > 30 or len(b) > 30:
            return False
        if abs(len(a) - len(b)) > 2:
            return False
        diffs = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
        return 0 < diffs <= 2

    @staticmethod
    def _check_tld(hostname):
        """Check the TLD for suspicious patterns."""
        parts = hostname.rsplit('.', 1)
        tld = parts[-1] if len(parts) > 1 else ''

        if tld in URLAnalyzer.SUSPICIOUS_TLDS:
            return {'status': 'warning', 'score': 20, 'detail': f'.{tld} is a TLD commonly used in scam/phishing sites'}

        common_tlds = {'com', 'org', 'net', 'edu', 'gov'}
        if tld in common_tlds:
            return {'status': 'safe', 'score': 92, 'detail': f'.{tld} is a common, well-established TLD'}

        regional_tlds = {'io', 'co', 'me', 'uk', 'in', 'de', 'fr', 'jp', 'au', 'ca', 'us', 'eu'}
        if tld in regional_tlds:
            return {'status': 'safe', 'score': 80, 'detail': f'.{tld} is a recognized regional/tech TLD'}

        return {'status': 'neutral', 'score': 55, 'detail': f'.{tld} TLD — uncommon, exercise caution'}

    @staticmethod
    def _check_url_structure(url, parsed):
        """Analyze URL structure for suspicious patterns."""
        issues = []
        score = 92

        subdomain_count = len(parsed.hostname.split('.')) - 2
        if subdomain_count > 2:
            issues.append('Excessive subdomains detected')
            score -= 25
        elif subdomain_count > 0:
            score -= 3

        if len(url) > 200:
            issues.append('Unusually long URL')
            score -= 15
        elif len(url) > 100:
            score -= 5

        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', parsed.hostname):
            issues.append('Uses IP address instead of domain name')
            score -= 35

        if '@' in parsed.netloc:
            issues.append('Contains @ symbol — may disguise real destination')
            score -= 40

        if '%' in parsed.path and any(enc in url.lower() for enc in ['%2f', '%3a', '%40', '%3f']):
            issues.append('Contains encoded characters that may hide real URL')
            score -= 20

        if parsed.hostname.count('-') > 3:
            issues.append('Multiple hyphens in domain name')
            score -= 18

        # Check for suspicious path patterns
        path_lower = parsed.path.lower()
        if any(p in path_lower for p in ['/wp-admin', '/admin', '/.env', '/phpmyadmin']):
            issues.append('Suspicious admin/config path detected')
            score -= 15

        # Check for data URIs or javascript in URL
        if 'javascript:' in url.lower() or 'data:' in url.lower():
            issues.append('Contains potentially malicious URI scheme')
            score -= 40

        score = max(0, score)
        status = 'safe' if score >= 70 else 'warning' if score >= 40 else 'danger'
        detail = '; '.join(issues) if issues else 'URL structure looks normal'
        return {'status': status, 'score': score, 'detail': detail, 'issues': issues}

    @staticmethod
    def _check_phishing_keywords(url):
        """Check for phishing-related keywords in the URL."""
        url_lower = url.lower()
        found = [kw for kw in URLAnalyzer.PHISHING_KEYWORDS if kw in url_lower]

        if not found:
            return {'status': 'safe', 'score': 95, 'detail': 'No phishing keywords detected'}

        score = max(5, 95 - len(found) * 25)
        return {
            'status': 'warning' if len(found) < 3 else 'danger',
            'score': score,
            'detail': f'Phishing keywords found: {", ".join(found)}',
            'keywords_found': found,
        }

    @staticmethod
    def _check_ssl(url, parsed):
        """Check if the URL uses HTTPS and validate certificate."""
        if parsed.scheme != 'https':
            return {'status': 'danger', 'score': 15, 'detail': 'Uses HTTP — connection is not encrypted, highly suspicious'}

        # Try to verify SSL certificate
        try:
            response = requests.head(url, timeout=5, verify=True,
                                     headers={'User-Agent': 'Mozilla/5.0'})
            return {'status': 'safe', 'score': 92, 'detail': 'Uses HTTPS with valid SSL certificate'}
        except requests.exceptions.SSLError:
            return {'status': 'danger', 'score': 10, 'detail': 'HTTPS with INVALID SSL certificate — very suspicious'}
        except requests.exceptions.RequestException:
            return {'status': 'neutral', 'score': 70, 'detail': 'Uses HTTPS but could not verify certificate (site may be down)'}

    @staticmethod
    def _check_redirects(url):
        """Check the redirect chain of the URL."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=10,
                                     headers={'User-Agent': 'Mozilla/5.0'})
            redirects = response.history
            final_url = response.url

            if not redirects:
                return {'status': 'safe', 'score': 92, 'detail': 'No redirects detected', 'final_url': final_url}

            if len(redirects) > 3:
                return {
                    'status': 'danger', 'score': 20,
                    'detail': f'Excessive redirects ({len(redirects)}) — likely hiding real destination',
                    'redirect_count': len(redirects), 'final_url': final_url,
                }

            orig_host = urlparse(url).hostname
            final_host = urlparse(final_url).hostname
            if orig_host != final_host:
                # Check if redirecting to a trusted domain
                if final_host in URLAnalyzer.TRUSTED_DOMAINS:
                    return {
                        'status': 'neutral', 'score': 70,
                        'detail': f'Redirects to trusted domain: {final_host}',
                        'redirect_count': len(redirects), 'final_url': final_url,
                    }
                return {
                    'status': 'warning', 'score': 35,
                    'detail': f'Redirects to different domain: {final_host}',
                    'redirect_count': len(redirects), 'final_url': final_url,
                }

            return {
                'status': 'neutral', 'score': 78,
                'detail': f'{len(redirects)} redirect(s) — within same domain',
                'redirect_count': len(redirects), 'final_url': final_url,
            }
        except requests.RequestException:
            return {'status': 'unknown', 'score': 40, 'detail': 'Could not check redirects — site may be down or blocking requests'}

    @staticmethod
    def _check_shortener(hostname):
        """Check if the URL uses a URL shortener."""
        if hostname in URLAnalyzer.SHORTENER_DOMAINS:
            return {'status': 'warning', 'score': 25, 'detail': 'URL shortener detected — real destination is hidden'}
        return {'status': 'safe', 'score': 92, 'detail': 'Not a shortened URL'}

    @staticmethod
    def _check_domain_age_signals(hostname):
        """Heuristic signals about domain trustworthiness."""
        try:
            socket.setdefaulttimeout(5)
            ip = socket.gethostbyname(hostname)
            # Check if it resolves to a private IP (suspicious for public URLs)
            if ip.startswith(('10.', '172.16.', '192.168.', '127.')):
                return {'status': 'warning', 'score': 30, 'detail': 'Domain resolves to a private/local IP address'}
            return {'status': 'safe', 'score': 78, 'detail': f'Domain resolves to {ip}'}
        except socket.gaierror:
            return {'status': 'danger', 'score': 5, 'detail': 'Domain does not resolve — may not exist or is offline'}
        except Exception:
            return {'status': 'unknown', 'score': 40, 'detail': 'Could not verify domain resolution'}

    @staticmethod
    def _check_page_content(url):
        """Fetch and analyze page content for suspicious patterns."""
        try:
            response = requests.get(url, timeout=10, verify=False,
                                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                    allow_redirects=True)

            if response.status_code >= 400:
                return {'status': 'warning', 'score': 40,
                        'detail': f'Page returned HTTP {response.status_code} error'}

            content = response.text[:50000]  # Limit content analysis
            content_lower = content.lower()
            findings = []
            score = 90

            # Check for suspicious HTML patterns
            for pattern, description in URLAnalyzer.SUSPICIOUS_HTML_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append(description)
                    score -= 12

            # Check for excessive external links
            external_links = re.findall(r'href=["\']https?://([^/"\']+)', content)
            unique_domains = set(external_links)
            if len(unique_domains) > 20:
                findings.append(f'Page links to {len(unique_domains)} different external domains')
                score -= 10

            # Check for obfuscated JavaScript
            if 'atob(' in content_lower or 'btoa(' in content_lower:
                findings.append('Base64 encoding/decoding in JavaScript')
                score -= 8
            if content_lower.count('\\x') > 10:
                findings.append('Hex-encoded content detected')
                score -= 10
            if content_lower.count('\\u') > 20:
                findings.append('Unicode-escaped content detected')
                score -= 8

            # Check for fake urgency indicators
            urgency_words = ['act now', 'limited time', 'expires today', 'your account has been',
                             'suspended', 'verify immediately', 'unauthorized access', 'click here to confirm']
            found_urgency = [w for w in urgency_words if w in content_lower]
            if found_urgency:
                findings.append(f'Urgency/fear language: {", ".join(found_urgency[:3])}')
                score -= 15

            # Check page size (very small pages might be phishing shells)
            if len(content) < 500:
                findings.append('Very small page — may be a phishing shell')
                score -= 10

            score = max(0, min(100, score))
            status = 'safe' if score >= 70 else 'warning' if score >= 40 else 'danger'
            detail = '; '.join(findings) if findings else 'Page content appears normal'

            return {'status': status, 'score': score, 'detail': detail, 'findings': findings}

        except requests.exceptions.SSLError:
            return {'status': 'danger', 'score': 15, 'detail': 'SSL certificate error when fetching page'}
        except requests.exceptions.Timeout:
            return {'status': 'warning', 'score': 45, 'detail': 'Page took too long to respond'}
        except requests.exceptions.ConnectionError:
            return {'status': 'warning', 'score': 35, 'detail': 'Could not connect to the page'}
        except Exception:
            return {'status': 'unknown', 'score': 50, 'detail': 'Could not analyze page content'}

    @staticmethod
    def _check_security_headers(url):
        """Check HTTP security headers of the response."""
        try:
            response = requests.head(url, timeout=8,
                                     headers={'User-Agent': 'Mozilla/5.0'},
                                     allow_redirects=True)

            headers_lower = {k.lower(): v for k, v in response.headers.items()}
            present = []
            missing = []

            for header in URLAnalyzer.SECURITY_HEADERS:
                if header in headers_lower:
                    present.append(header)
                else:
                    missing.append(header)

            score = 50 + (len(present) / len(URLAnalyzer.SECURITY_HEADERS)) * 45

            # Bonus for HSTS
            if 'strict-transport-security' in headers_lower:
                score = min(100, score + 5)

            status = 'safe' if score >= 70 else 'warning' if score >= 45 else 'danger'
            detail_parts = []
            if present:
                detail_parts.append(f'Security headers present: {len(present)}/{len(URLAnalyzer.SECURITY_HEADERS)}')
            if missing:
                detail_parts.append(f'Missing: {", ".join(missing[:3])}')

            return {'status': status, 'score': round(score, 1),
                    'detail': '; '.join(detail_parts) if detail_parts else 'Could not check headers',
                    'present': present, 'missing': missing}

        except requests.RequestException:
            return {'status': 'unknown', 'score': 45, 'detail': 'Could not check security headers'}

    @staticmethod
    def _check_domain_whois(hostname):
        """Check domain WHOIS information for age and registration details."""
        try:
            import whois
            domain_info = whois.whois(hostname)

            creation_date = domain_info.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            if creation_date:
                age_days = (datetime.utcnow() - creation_date).days

                if age_days < 30:
                    return {'status': 'danger', 'score': 10,
                            'detail': f'Domain is only {age_days} days old — very suspicious',
                            'domain_age_days': age_days}
                elif age_days < 90:
                    return {'status': 'warning', 'score': 30,
                            'detail': f'Domain is {age_days} days old — relatively new',
                            'domain_age_days': age_days}
                elif age_days < 365:
                    return {'status': 'neutral', 'score': 60,
                            'detail': f'Domain is {age_days} days old — less than a year',
                            'domain_age_days': age_days}
                elif age_days < 365 * 3:
                    return {'status': 'safe', 'score': 78,
                            'detail': f'Domain is {age_days // 365} years old',
                            'domain_age_days': age_days}
                else:
                    return {'status': 'safe', 'score': 92,
                            'detail': f'Domain is {age_days // 365} years old — well-established',
                            'domain_age_days': age_days}

            # WHOIS returned but no creation date
            registrar = domain_info.registrar
            if registrar:
                return {'status': 'neutral', 'score': 55,
                        'detail': f'Registered with {registrar}, but creation date unknown'}

            return {'status': 'unknown', 'score': 45, 'detail': 'WHOIS data incomplete'}

        except ImportError:
            # python-whois not installed — use DNS-based heuristic
            return URLAnalyzer._check_domain_age_fallback(hostname)
        except Exception:
            return URLAnalyzer._check_domain_age_fallback(hostname)

    @staticmethod
    def _check_domain_age_fallback(hostname):
        """Fallback domain check when WHOIS is unavailable."""
        try:
            # Check if domain has MX records (established domains usually do)
            import subprocess
            result = subprocess.run(['nslookup', '-type=MX', hostname],
                                    capture_output=True, text=True, timeout=5)
            has_mx = 'mail exchanger' in result.stdout.lower() or 'mx' in result.stdout.lower()

            # Check if domain has multiple DNS records
            result2 = subprocess.run(['nslookup', '-type=NS', hostname],
                                     capture_output=True, text=True, timeout=5)
            ns_count = result2.stdout.lower().count('nameserver') + result2.stdout.lower().count('ns')

            score = 45
            details = []
            if has_mx:
                score += 15
                details.append('Has mail servers')
            if ns_count >= 2:
                score += 10
                details.append(f'Has {ns_count} nameservers')

            status = 'safe' if score >= 65 else 'neutral' if score >= 50 else 'warning'
            return {'status': status, 'score': score,
                    'detail': '; '.join(details) if details else 'Limited domain info available (WHOIS unavailable)'}
        except Exception:
            return {'status': 'unknown', 'score': 45, 'detail': 'Could not check domain registration info'}

    @staticmethod
    def _get_platform_info(url, hostname):
        """Get platform-specific info (e.g., YouTube video metadata)."""
        youtube_hosts = {'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com'}
        if hostname not in youtube_hosts:
            return None

        try:
            cmd = ['yt-dlp', '--no-playlist', '--dump-json', '--no-warnings', '--no-download', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return {'platform': 'YouTube', 'status': 'Video not accessible or does not exist'}

            info = json.loads(result.stdout)
            return {
                'platform': 'YouTube',
                'title': info.get('title', 'Unknown'),
                'channel': info.get('channel', info.get('uploader', 'Unknown')),
                'channel_verified': info.get('channel_is_verified', False),
                'upload_date': info.get('upload_date', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'duration': info.get('duration', 0),
                'description_snippet': (info.get('description', '') or '')[:300],
                'channel_follower_count': info.get('channel_follower_count', 0),
            }
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return {'platform': 'YouTube', 'status': 'Could not fetch video metadata'}

    @staticmethod
    def _calculate_risk(checks):
        """Calculate overall risk score from individual checks."""
        weights = {
            'domain_trust': 0.18,
            'tld_safety': 0.07,
            'url_structure': 0.10,
            'phishing_keywords': 0.12,
            'ssl_certificate': 0.08,
            'redirect_chain': 0.08,
            'url_shortener': 0.04,
            'domain_age_signals': 0.06,
            'page_content': 0.12,
            'security_headers': 0.08,
            'domain_whois': 0.07,
        }

        weighted_safety = 0
        details = []
        for key, weight in weights.items():
            check = checks.get(key, {})
            score = check.get('score', 50)
            weighted_safety += score * weight

            if check.get('status') in ('warning', 'danger'):
                details.append(check.get('detail', ''))

        risk_score = max(0, min(100, 100 - weighted_safety))
        return risk_score, details

    @staticmethod
    def _calculate_confidence(checks):
        """Calculate confidence based on how much data was successfully gathered."""
        definitive = 0
        total = 0
        high_value_checks = {'page_content', 'domain_whois', 'redirect_chain', 'security_headers', 'ssl_certificate'}

        for key, check in checks.items():
            total += 1
            status = check.get('status', 'unknown')
            if status != 'unknown':
                definitive += 1
                if key in high_value_checks:
                    definitive += 0.5  # High-value checks boost confidence

        if total == 0:
            return 50.0

        ratio = definitive / (total + len(high_value_checks) * 0.5)
        confidence = 55 + ratio * 40  # Range: 55-95

        return round(min(98, confidence), 1)

    @staticmethod
    def _get_risk_level(risk_score):
        if risk_score >= 75:
            return 'Critical'
        elif risk_score >= 50:
            return 'High'
        elif risk_score >= 25:
            return 'Medium'
        return 'Low'

    @staticmethod
    def _get_verdict(risk_score):
        if risk_score >= 75:
            return 'This URL appears highly suspicious and is likely a scam or phishing attempt. Do NOT click or share.'
        elif risk_score >= 50:
            return 'This URL shows significant warning signs. Exercise extreme caution before interacting.'
        elif risk_score >= 25:
            return 'This URL has some minor concerns but is likely safe. Verify the source before sharing sensitive info.'
        return 'This URL appears to be legitimate and safe based on our analysis.'
