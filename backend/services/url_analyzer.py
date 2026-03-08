import re
import requests
import subprocess
import json
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
            report['confidence_score'] = round(min(95, 60 + len([c for c in checks.values() if c['status'] != 'unknown']) * 5), 1)
            report['risk_details'] = risk_details
            report['verdict'] = URLAnalyzer._get_verdict(risk_score)

            # Analysis summary for charts
            report['analysis_summary'] = {
                'domain_trust': checks['domain_trust']['score'],
                'url_safety': checks['url_structure']['score'],
                'ssl_security': checks['ssl_certificate']['score'],
                'phishing_risk': 100 - checks['phishing_keywords']['score'],
                'redirect_safety': checks['redirect_chain']['score'],
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
        # Check exact match
        if hostname in URLAnalyzer.TRUSTED_DOMAINS:
            return {'status': 'safe', 'score': 95, 'detail': f'{hostname} is a well-known trusted domain'}

        # Check if subdomain of trusted domain
        for trusted in URLAnalyzer.TRUSTED_DOMAINS:
            if hostname.endswith('.' + trusted):
                return {'status': 'safe', 'score': 85, 'detail': f'Subdomain of trusted domain {trusted}'}

        # Check for typosquatting (similar to trusted domains)
        for trusted in URLAnalyzer.TRUSTED_DOMAINS:
            base = trusted.replace('www.', '')
            if URLAnalyzer._is_similar(hostname.replace('www.', ''), base):
                return {'status': 'warning', 'score': 25, 'detail': f'Domain looks similar to {trusted} — possible typosquatting'}

        return {'status': 'unknown', 'score': 50, 'detail': 'Domain is not in trusted list (not necessarily unsafe)'}

    @staticmethod
    def _is_similar(a, b):
        """Simple Levenshtein-like check for typosquatting."""
        if a == b:
            return False
        if len(a) > 30 or len(b) > 30:
            return False
        # Check edit distance <= 2
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
            return {'status': 'warning', 'score': 30, 'detail': f'.{tld} is a TLD commonly used in scam/phishing sites'}

        common_tlds = {'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'me', 'uk', 'in', 'de', 'fr', 'jp', 'au', 'ca'}
        if tld in common_tlds:
            return {'status': 'safe', 'score': 90, 'detail': f'.{tld} is a common, well-established TLD'}

        return {'status': 'neutral', 'score': 65, 'detail': f'.{tld} TLD — less common but not necessarily suspicious'}

    @staticmethod
    def _check_url_structure(url, parsed):
        """Analyze URL structure for suspicious patterns."""
        issues = []
        score = 90

        # Excessive subdomains
        subdomain_count = len(parsed.hostname.split('.')) - 2
        if subdomain_count > 2:
            issues.append('Excessive subdomains detected')
            score -= 20

        # Very long URL
        if len(url) > 200:
            issues.append('Unusually long URL')
            score -= 10

        # IP address instead of domain
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', parsed.hostname):
            issues.append('Uses IP address instead of domain name')
            score -= 30

        # @ symbol in URL (credential phishing)
        if '@' in parsed.netloc:
            issues.append('Contains @ symbol — may disguise real destination')
            score -= 35

        # Suspicious characters
        if '%' in parsed.path and any(enc in url.lower() for enc in ['%2f', '%3a', '%40', '%3f']):
            issues.append('Contains encoded characters that may hide real URL')
            score -= 15

        # Multiple hyphens in domain
        if parsed.hostname.count('-') > 3:
            issues.append('Multiple hyphens in domain name')
            score -= 15

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

        score = max(10, 95 - len(found) * 20)
        return {
            'status': 'warning' if len(found) < 3 else 'danger',
            'score': score,
            'detail': f'Phishing keywords found: {", ".join(found)}',
            'keywords_found': found,
        }

    @staticmethod
    def _check_ssl(url, parsed):
        """Check if the URL uses HTTPS."""
        if parsed.scheme == 'https':
            return {'status': 'safe', 'score': 90, 'detail': 'Uses HTTPS (encrypted connection)'}
        return {'status': 'warning', 'score': 30, 'detail': 'Uses HTTP — connection is not encrypted'}

    @staticmethod
    def _check_redirects(url):
        """Check the redirect chain of the URL."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=10,
                                     headers={'User-Agent': 'Mozilla/5.0'})
            redirects = response.history
            final_url = response.url

            if not redirects:
                return {'status': 'safe', 'score': 90, 'detail': 'No redirects detected', 'final_url': final_url}

            if len(redirects) > 3:
                return {
                    'status': 'warning', 'score': 35,
                    'detail': f'Excessive redirects ({len(redirects)}) — may be hiding destination',
                    'redirect_count': len(redirects), 'final_url': final_url,
                }

            # Check if final domain differs significantly
            orig_host = urlparse(url).hostname
            final_host = urlparse(final_url).hostname
            if orig_host != final_host:
                return {
                    'status': 'warning', 'score': 50,
                    'detail': f'Redirects to different domain: {final_host}',
                    'redirect_count': len(redirects), 'final_url': final_url,
                }

            return {
                'status': 'neutral', 'score': 75,
                'detail': f'{len(redirects)} redirect(s) — within same domain',
                'redirect_count': len(redirects), 'final_url': final_url,
            }
        except requests.RequestException:
            return {'status': 'unknown', 'score': 50, 'detail': 'Could not check redirects (site may be down)'}

    @staticmethod
    def _check_shortener(hostname):
        """Check if the URL uses a URL shortener."""
        if hostname in URLAnalyzer.SHORTENER_DOMAINS:
            return {'status': 'warning', 'score': 40, 'detail': 'URL shortener detected — real destination is hidden'}
        return {'status': 'safe', 'score': 90, 'detail': 'Not a shortened URL'}

    @staticmethod
    def _check_domain_age_signals(hostname):
        """Heuristic signals about domain trustworthiness."""
        # Check if domain resolves
        try:
            import socket
            socket.setdefaulttimeout(5)
            socket.gethostbyname(hostname)
            return {'status': 'safe', 'score': 75, 'detail': 'Domain resolves to a valid IP address'}
        except socket.gaierror:
            return {'status': 'danger', 'score': 15, 'detail': 'Domain does not resolve — may not exist'}
        except Exception:
            return {'status': 'unknown', 'score': 50, 'detail': 'Could not verify domain resolution'}

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
            'domain_trust': 0.25,
            'tld_safety': 0.10,
            'url_structure': 0.15,
            'phishing_keywords': 0.15,
            'ssl_certificate': 0.10,
            'redirect_chain': 0.10,
            'url_shortener': 0.05,
            'domain_age_signals': 0.10,
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
