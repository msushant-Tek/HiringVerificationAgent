import aiohttp
from typing import Dict, Any, Optional
import os

class GitHubAuditor:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.github_token}" if self.github_token else ""
        }

    async def fetch_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        if not username:
            return None
            
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/users/{username}") as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def fetch_user_repos(self, username: str) -> list:
        if not username:
            return []
            
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/users/{username}/repos?sort=updated&per_page=10") as response:
                if response.status == 200:
                    return await response.json()
                return []
                
    async def audit_technical_skills(self, github_handle: str) -> str:
        """
        Gathers a summary of the user's technical activity on GitHub.
        """
        if not github_handle:
            return "No GitHub handle provided."
            
        profile = await self.fetch_user_profile(github_handle)
        if not profile:
            return f"Could not fetch profile for GitHub user: {github_handle}"
            
        repos = await self.fetch_user_repos(github_handle)
        
        language_stats = {}
        total_stars = 0
        
        for repo in repos:
            lang = repo.get("language")
            if lang:
                language_stats[lang] = language_stats.get(lang, 0) + 1
            total_stars += repo.get("stargazers_count", 0)
            
        # Format the audit summary
        top_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        langs_str = ", ".join([f"{lang} ({count} repos)" for lang, count in top_languages])
        
        audit_summary = (
            f"GitHub Audit for {github_handle}:\n"
            f"- Public Repositories: {profile.get('public_repos', 0)}\n"
            f"- Followers: {profile.get('followers', 0)}\n"
            f"- Total Stars on recent repos: {total_stars}\n"
            f"- Top Languages in recent repos: {langs_str if langs_str else 'N/A'}\n"
        )
        
        return audit_summary
